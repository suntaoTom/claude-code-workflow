#!/usr/bin/env python3
"""
OpenAPI -> 按 tag 拆分的 Java 后端 Markdown 契约索引生成器

输入:
    docs/contracts/openapi/*.json

输出:
    docs/apis/<tag-slug>.md
    docs/apis/README.md

设计原则:
- OpenAPI JSON 是契约源，Markdown 是生成的索引层，禁止手改生成文件。
- 每个 operation 一个二级标题，operationId 作为稳定锚点。
- Java 源码中的 @api 引用从 workspace/src/main/java/ 扫描并校验。

使用:
    python3 tools/gen_api_md.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "apis"

# OpenAPI 主源路径候选 (按优先级)
OPENAPI_DIR_CANDIDATES = [
    ROOT / "docs" / "contracts" / "openapi",
]

# 代码扫描候选: (路径, 文件 glob 列表) — 用于 @api 锚点断链检查
WORKSPACE_SCAN_CANDIDATES: list[tuple[Path, tuple[str, ...]]] = [
    (ROOT / "workspace" / "src" / "main" / "java", ("*.java",)),
]

# 标记自动生成, 防止有人手改
AUTO_GEN_BANNER = (
    "> ⚠️ 本文件由 `tools/gen_api_md.py` 从 OpenAPI 自动生成, **不要手改**。\n"
    "> 接口变更 → 替换 `docs/apis/openapi/*.json` → 重新执行脚本。"
)


def slugify(text: str) -> str:
    """tag/operationId → kebab-case 锚点"""
    s = re.sub(r"[^a-zA-Z0-9一-龥]+", "-", text).strip("-").lower()
    return s or "untagged"


def derive_op_id(method: str, path: str, op: dict[str, Any]) -> str:
    """优先取 operationId, 否则按 method+path 推导"""
    if op.get("operationId"):
        return slugify(op["operationId"])
    # /member/security/email -> security-email
    cleaned = re.sub(r"\{[^}]+\}", "by-param", path)
    return slugify(f"{method}-{cleaned}")


def resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    """#/components/schemas/Xxx -> 实际 schema 对象"""
    parts = ref.lstrip("#/").split("/")
    node: Any = spec
    for p in parts:
        node = node.get(p, {})
    return node


def schema_inline(schema: dict[str, Any], spec: dict[str, Any], depth: int = 0) -> str:
    """schema → 简短类型表达式 (用于字段表的「类型」列)"""
    if not schema:
        return "any"
    if "$ref" in schema:
        name = schema["$ref"].split("/")[-1]
        return f"[{name}](#schema-{slugify(name)})"
    t = schema.get("type")
    fmt = schema.get("format")
    if t == "array":
        return f"array<{schema_inline(schema.get('items', {}), spec, depth + 1)}>"
    if t == "object":
        return "object"
    if fmt:
        return f"{t}({fmt})"
    if "enum" in schema:
        return f"enum[{', '.join(map(str, schema['enum']))}]"
    return t or "any"


def render_props_table(schema: dict[str, Any], spec: dict[str, Any]) -> str:
    """object schema → 字段表 Markdown"""
    if "$ref" in schema:
        schema = resolve_ref(spec, schema["$ref"])
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    if not props:
        return "_(无字段)_"
    lines = ["| 字段 | 类型 | 必填 | 描述 |", "|------|------|------|------|"]
    for name, p in props.items():
        type_str = schema_inline(p, spec)
        req = "✓" if name in required else ""
        desc = (p.get("description") or "").replace("\n", " ").replace("|", "\\|")
        lines.append(f"| `{name}` | {type_str} | {req} | {desc} |")
    return "\n".join(lines)


def render_request(op: dict[str, Any], spec: dict[str, Any]) -> str:
    """请求参数 + 请求体 渲染"""
    blocks: list[str] = []

    # path / query / header 参数
    params = op.get("parameters", [])
    if params:
        lines = ["**请求参数**:", "", "| 位置 | 名称 | 类型 | 必填 | 描述 |", "|------|------|------|------|------|"]
        for p in params:
            loc = p.get("in", "")
            name = p.get("name", "")
            t = schema_inline(p.get("schema", {}), spec)
            req = "✓" if p.get("required") else ""
            desc = (p.get("description") or "").replace("\n", " ").replace("|", "\\|")
            lines.append(f"| {loc} | `{name}` | {t} | {req} | {desc} |")
        blocks.append("\n".join(lines))

    # request body
    rb = op.get("requestBody")
    if rb:
        content = rb.get("content", {})
        json_schema = (
            content.get("application/json", {}).get("schema")
            or next(iter(content.values()), {}).get("schema")
            or {}
        )
        if json_schema:
            if "$ref" in json_schema:
                ref_name = json_schema["$ref"].split("/")[-1]
                resolved = resolve_ref(spec, json_schema["$ref"])
                blocks.append(
                    f"**请求体** ([{ref_name}](#schema-{slugify(ref_name)})):\n\n"
                    + render_props_table(resolved, spec)
                )
            else:
                blocks.append("**请求体**:\n\n" + render_props_table(json_schema, spec))

    return "\n\n".join(blocks) if blocks else "_(无请求参数)_"


def render_response(op: dict[str, Any], spec: dict[str, Any]) -> str:
    """响应 渲染 (只取 200)"""
    responses = op.get("responses", {})
    ok = responses.get("200") or responses.get("201") or next(iter(responses.values()), {})
    if not ok:
        return "_(无响应定义)_"
    content = ok.get("content", {})
    schema = (
        content.get("application/json", {}).get("schema")
        or next(iter(content.values()), {}).get("schema")
        or {}
    )
    if not schema:
        return "**响应**: " + (ok.get("description") or "OK")
    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        return f"**响应**: [{ref_name}](#schema-{slugify(ref_name)})"
    return "**响应**: `" + schema_inline(schema, spec) + "`"


def collect_referenced_schemas(op: dict[str, Any]) -> set[str]:
    """递归收集本 operation 引用的所有 schema 名"""
    refs: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "$ref" in node and isinstance(node["$ref"], str):
                refs.add(node["$ref"].split("/")[-1])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(op)
    return refs


def render_operation(method: str, path: str, op: dict[str, Any], spec: dict[str, Any]) -> tuple[str, set[str]]:
    """单个 operation → md 段落, 同时返回它引用的 schema 集合"""
    op_id = derive_op_id(method, path, op)
    summary = op.get("summary") or op_id
    description = op.get("description", "").strip()

    parts = [
        f"## {op_id}",
        "",
        f"- **接口**: `{method.upper()} {path}`",
        f"- **摘要**: {summary}",
    ]
    if description:
        parts.append(f"- **描述**: {description}")
    parts.append("")
    parts.append(render_request(op, spec))
    parts.append("")
    parts.append(render_response(op, spec))

    # 业务上下文占位 (人工补充, 不被覆盖)
    parts.extend(
        [
            "",
            "### H5 旧实现",
            "",
            "_(待补: H5 页面/路由 + 调用时机)_",
            "",
            "### Flutter 迁移备注",
            "",
            "_(待补: 错误码映射 / 鉴权要求 / 缓存策略 / 与其他接口的调用顺序)_",
            "",
        ]
    )

    schemas_used = collect_referenced_schemas(op)
    return "\n".join(parts), schemas_used


def render_schemas_section(schema_names: set[str], spec: dict[str, Any]) -> str:
    """文件末尾的 Schema 字典段落"""
    if not schema_names:
        return ""
    all_schemas = spec.get("components", {}).get("schemas", {})
    # 递归展开嵌套引用
    expanded: set[str] = set()
    queue = list(schema_names)
    while queue:
        n = queue.pop()
        if n in expanded or n not in all_schemas:
            continue
        expanded.add(n)
        for ref in collect_referenced_schemas(all_schemas[n]):
            if ref not in expanded:
                queue.append(ref)

    lines = ["---", "", "## 数据结构 (Schemas)", ""]
    for name in sorted(expanded):
        s = all_schemas.get(name, {})
        lines.append(f"### schema-{slugify(name)}")
        lines.append("")
        lines.append(f"`{name}`")
        lines.append("")
        if "enum" in s:
            lines.append(f"枚举类型 ({schema_inline(s, spec)}): " + ", ".join(map(str, s["enum"])))
        else:
            lines.append(render_props_table(s, spec))
        lines.append("")
    return "\n".join(lines)


def render_tag_file(tag: str, ops: list[tuple[str, str, dict[str, Any]]], spec: dict[str, Any], source_file: str) -> str:
    """单个 tag → 一个完整的 md 文件内容"""
    parts = [
        f"# {tag} 接口",
        "",
        AUTO_GEN_BANNER,
        "",
        f"- **协议源**: `docs/apis/openapi/{source_file}`",
        f"- **接口数量**: {len(ops)}",
        f"- **PRD 引用方式**: `@api docs/apis/{slugify(tag)}.md#<operation-id>`",
        "",
        "## 接口列表",
        "",
        "| Operation | Method | Path | 摘要 |",
        "|-----------|--------|------|------|",
    ]
    for method, path, op in ops:
        op_id = derive_op_id(method, path, op)
        summary = (op.get("summary") or "").replace("|", "\\|")
        parts.append(f"| [{op_id}](#{op_id}) | {method.upper()} | `{path}` | {summary} |")
    parts.append("")
    parts.append("---")
    parts.append("")

    schemas_used: set[str] = set()
    for method, path, op in ops:
        section, refs = render_operation(method, path, op, spec)
        parts.append(section)
        schemas_used.update(refs)

    parts.append(render_schemas_section(schemas_used, spec))
    return "\n".join(parts)


def group_by_tag(spec: dict[str, Any]) -> dict[str, list[tuple[str, str, dict[str, Any]]]]:
    """所有 operation 按 tag 聚合"""
    by_tag: dict[str, list[tuple[str, str, dict[str, Any]]]] = {}
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            tags = op.get("tags") or ["Untagged"]
            for tag in tags:
                by_tag.setdefault(tag, []).append((method, path, op))
    return by_tag


# ---------------------------------------------------------------------------
# 锚点 diff + 代码引用断链检查
# ---------------------------------------------------------------------------

# 匹配 .md 里的二级标题 (operation 锚点) 与三级 schema 标题
ANCHOR_OP_RE = re.compile(r"^## ([a-z0-9一-龥-]+)\s*$", re.MULTILINE)
ANCHOR_SCHEMA_RE = re.compile(r"^### (schema-[a-z0-9-]+)\s*$", re.MULTILINE)

# 匹配 JavaDoc/Javadoc 中的 @api 引用 (支持一行多个, 逗号分隔)
# @api docs/apis/security.md#current, docs/apis/wallet.md#schema-walletform
JAVA_API_REF_RE = re.compile(r"@api\s+([^\n\r]+)")
API_REF_TARGET_RE = re.compile(r"docs/apis/([a-z0-9-]+)\.md#([a-z0-9-]+)")


def extract_anchors(md_text: str) -> set[str]:
    """从已写出的 .md 文本提取所有可被 @api 引用的锚点"""
    return set(ANCHOR_OP_RE.findall(md_text)) | set(ANCHOR_SCHEMA_RE.findall(md_text))


def scan_code_api_refs() -> list[tuple[Path, str, str]]:
    """扫描 workspace/src/main/java 下的 Java 源码，提取 @api 引用。"""
    refs: list[tuple[Path, str, str]] = []
    for ws_path, globs in WORKSPACE_SCAN_CANDIDATES:
        if not ws_path.exists():
            continue
        for pattern in globs:
            for src_file in ws_path.rglob(pattern):
                try:
                    text = src_file.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                for line_match in JAVA_API_REF_RE.finditer(text):
                    for target in API_REF_TARGET_RE.finditer(line_match.group(1)):
                        refs.append((src_file, f"{target.group(1)}.md", target.group(2)))
    return refs


def render_index(per_source: dict[str, dict[str, int]]) -> str:
    """docs/apis/README.md 入口"""
    parts = [
        "# 协议层接口文档索引",
        "",
        "> 协议层接口的「契约源」, PRD 通过 `@api` 锚点引用具体接口。",
        "",
        "## 目录结构",
        "",
        "```",
        "docs/apis/",
        "├── README.md              # 本文件",
        "└── <tag-slug>.md          # 按 tag 拆分的人类可读 + AI 可读索引",
        "```",
        "",
        "## 维护规则",
        "",
        "1. **主源**: `docs/contracts/openapi/*.json` 是事实来源，由后端协议层导出，**不手改**",
        "2. **生成**: 替换 JSON 后执行 `python3 tools/gen_api_md.py` 重新生成 `docs/apis/` 索引",
        "3. **业务上下文**: 每个 operation 的「迁移备注」等人工内容不得写入自动生成文件",
        "4. **PRD 引用**: `@api docs/apis/<tag-slug>.md#<operation-id>`",
        "",
        "## 当前协议源",
        "",
    ]
    for src, tags in per_source.items():
        total = sum(tags.values())
        parts.append(f"### `{src}` — {total} 个接口 / {len(tags)} 个 tag")
        parts.append("")
        parts.append("| Tag (业务域) | 接口数 | 索引文件 |")
        parts.append("|-------------|--------|----------|")
        for tag, count in sorted(tags.items(), key=lambda x: -x[1]):
            parts.append(f"| {tag} | {count} | [{slugify(tag)}.md]({slugify(tag)}.md) |")
        parts.append("")
    return "\n".join(parts)


def main() -> int:
    # 自动探测 OpenAPI 主源目录
    openapi_dir: Path | None = None
    for candidate in OPENAPI_DIR_CANDIDATES:
        if candidate.exists() and any(candidate.glob("*.json")):
            openapi_dir = candidate
            break
    if openapi_dir is None:
        print(
            "❌ 未找到 OpenAPI 主源 JSON, 请把后端导出的 OpenAPI 放到以下任一目录:\n"
            + "\n".join(f"    - {p.relative_to(ROOT)}/*.json" for p in OPENAPI_DIR_CANDIDATES),
            file=sys.stderr,
        )
        return 1

    json_files = sorted(openapi_dir.glob("*.json"))
    print(f"📂 OpenAPI 主源: {openapi_dir.relative_to(ROOT)}/ ({len(json_files)} 个 JSON)")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: 生成前, 收集旧锚点 ──────────────────────────────────────
    old_anchors_by_file: dict[str, set[str]] = {}
    for old_md in OUT_DIR.glob("*.md"):
        if old_md.name == "README.md":
            continue
        old_anchors_by_file[old_md.name] = extract_anchors(old_md.read_text(encoding="utf-8"))

    # ── Step 2: 多源按 tag 合并 ─────────────────────────────────────────
    merged_by_tag: dict[str, list[tuple[str, str, dict[str, Any]]]] = {}
    merged_spec: dict[str, Any] = {"components": {"schemas": {}}}
    per_source: dict[str, dict[str, int]] = {}
    source_for_tag: dict[str, str] = {}

    for jf in json_files:
        spec = json.loads(jf.read_text(encoding="utf-8"))
        by_tag = group_by_tag(spec)
        per_source[jf.name] = {t: len(ops) for t, ops in by_tag.items()}
        for tag, ops in by_tag.items():
            merged_by_tag.setdefault(tag, []).extend(ops)
            source_for_tag.setdefault(tag, jf.name)
        # 合并 schemas
        merged_spec["components"]["schemas"].update(
            spec.get("components", {}).get("schemas", {})
        )

    # ── Step 3: 写出每个 tag 的 .md, 同时收集新锚点 ──────────────────────
    written: list[Path] = []
    new_anchors_by_file: dict[str, set[str]] = {}
    for tag, ops in merged_by_tag.items():
        content = render_tag_file(tag, ops, merged_spec, source_for_tag[tag])
        out_name = f"{slugify(tag)}.md"
        (OUT_DIR / out_name).write_text(content, encoding="utf-8")
        written.append(OUT_DIR / out_name)
        new_anchors_by_file[out_name] = extract_anchors(content)

    # 写入口 README
    (OUT_DIR / "README.md").write_text(render_index(per_source), encoding="utf-8")

    print(f"✅ 生成完成: {len(written)} 个 tag 文件 + README.md")

    # ── Step 4: 锚点 diff (added / removed / renamed) ──────────────────
    if old_anchors_by_file:
        print("\n📊 锚点变更对比 (相对上一次生成):")
        any_change = False
        all_files = sorted(set(old_anchors_by_file) | set(new_anchors_by_file))
        for fname in all_files:
            old = old_anchors_by_file.get(fname, set())
            new = new_anchors_by_file.get(fname, set())
            added = new - old
            removed = old - new
            if not added and not removed:
                continue
            any_change = True
            print(f"  📄 {fname}")
            for a in sorted(added):
                print(f"      ➕ {a}")
            for r in sorted(removed):
                print(f"      ➖ {r}")
        if not any_change:
            print("  (锚点无变化)")
    else:
        print("\n📊 首次生成, 无历史锚点可对比")

    # ── Step 5: 扫描 workspace/src/main/java 源码 @api 引用, 检查断链 ────────
    java_refs = scan_code_api_refs()
    print(f"\n🔗 扫描 Java 源码 @api 引用: 共 {len(java_refs)} 处")
    broken: list[tuple[Path, str, str]] = []
    for src, tag_md, anchor in java_refs:
        new_anchors = new_anchors_by_file.get(tag_md)
        if new_anchors is None or anchor not in new_anchors:
            broken.append((src, tag_md, anchor))
    if broken:
        print(f"  ⚠️ 断链 {len(broken)} 处 — 协议层变更后代码 @api 锚点失效:")
        for src, tag_md, anchor in broken:
            rel = src.relative_to(ROOT) if src.is_relative_to(ROOT) else src
            print(f"      ❌ {rel} → docs/apis/{tag_md}#{anchor}")
        print("\n  处理建议: 在新接口里查找等价 operationId, 更新源文件 @api 字段")
        return 2  # 非零退出, 便于 CI 拦截
    else:
        print("  ✅ 所有引用都指向存在的锚点")

    return 0


if __name__ == "__main__":
    sys.exit(main())
