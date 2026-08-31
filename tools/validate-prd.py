#!/usr/bin/env python3
"""Validate the deterministic, non-semantic parts of a Java backend PRD."""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

DOMAIN = "java-backend"
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
PATH_RE = re.compile(r"(?<![A-Za-z0-9_./-])((?:\.claude|docs|tools|workspace)/[A-Za-z0-9_./-]+(?:#[^\s)`>,。）】]+)?)")


def root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_anchor(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9一-龥]+", "-", value)
    return value.strip("-")


def headings(text: str) -> list[tuple[int, str, int]]:
    return [(len(match.group(1)), match.group(2), index + 1) for index, line in enumerate(text.splitlines()) if (match := HEADING_RE.match(line))]


def anchor_exists(path: Path, anchor: str) -> bool:
    if not anchor:
        return True
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return False
    target = normalize_anchor(anchor)
    return any(normalize_anchor(title) == target for _, title, _ in headings(content))


def check_rules(text: str) -> list[str]:
    lines = text.splitlines()
    rule_sections = [index for index, line in enumerate(lines) if re.match(r"^###\s+业务规则\s*$", line)]
    if not rule_sections:
        return ["缺少 `### 业务规则` 章节"]
    errors: list[str] = []
    for section_index, index in enumerate(rule_sections):
        end = rule_sections[section_index + 1] if section_index + 1 < len(rule_sections) else len(lines)
        for next_index in range(index + 1, end):
            if lines[next_index].startswith("#"):
                end = next_index
                break
        rules = [item for item in lines[index + 1 : end] if re.match(r"^\s*(?:\d+[.)]|[-*])\s+\S", item)]
        if not rules:
            errors.append(f"业务规则章节为空（第 {index + 1} 行）")
    return errors


def validate(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"PRD 文件不存在：{path}"]
    if path.suffix.lower() != ".md":
        errors.append("输入文件必须是 Markdown（.md）")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["PRD 不是 UTF-8 文本"]

    if not re.search(r"(?:^|[|`\s])domain\s*[:|=]\s*[`\"']?java-backend", text, re.IGNORECASE):
        errors.append("缺少 domain: java-backend")
    if "[待确认]" in text:
        errors.append("仍包含 [待确认]")
    for index, line in enumerate(text.splitlines(), start=1):
        if "[待填写]" in line and not any(label in line for label in ("负责人", "变更人")):
            errors.append(f"正文包含越界 [待填写]（第 {index} 行）")
    if "[默认假设]" in text:
        print("WARN validate-prd: 包含 [默认假设]，需人工确认", file=sys.stderr)
    if re.search(r"^##\s+冲突待决\s*$", text, re.MULTILINE):
        errors.append("存在 ## 冲突待决，必须先解决")
    errors.extend(check_rules(text))

    required_headings = ["调用与边界", "数据与协议", "可靠性与异常"]
    existing = {title.strip() for _, title, _ in headings(text)}
    for title in required_headings:
        if title not in existing:
            errors.append(f"缺少后端需求章节：{title}")
    if "配置项" not in existing and "验收清单" not in existing:
        errors.append("至少需要 `## 配置项` 或 `## 验收清单` 章节")

    for match in PATH_RE.finditer(text):
        line_no = text.count("\n", 0, match.start()) + 1
        reference = match.group(1).rstrip(".,;:，。；：")
        relative, _, anchor = reference.partition("#")
        target = root / relative
        if not target.exists():
            errors.append(f"第 {line_no} 行引用文件不存在：{reference}")
        elif anchor and not anchor_exists(target, anchor):
            errors.append(f"第 {line_no} 行引用锚点不存在：{reference}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prd", type=Path)
    args = parser.parse_args()
    root = Path(os.environ.get("WORKFLOW_ROOT", str(root_dir()))).resolve()
    path = args.prd if args.prd.is_absolute() else root / args.prd
    if path.name in {"_template.md", "REVIEW.md", "_intake-spec.md"}:
        print(f"NOT_APPLICABLE validate-prd: 模板/规范文件不参与 PRD 校验：{path}")
        return 0
    errors = validate(path.resolve(), root)
    if errors:
        print(f"FAIL validate-prd: {path}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS validate-prd: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
