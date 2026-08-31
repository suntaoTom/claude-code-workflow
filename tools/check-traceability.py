#!/usr/bin/env python3
"""Check active Java backend PRD/task/source/test traceability."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

DOMAIN = "java-backend"
TAG_RE = re.compile(r"@(prd|task|api)\s+([^\s*]+)")
RULE_LINE_RE = re.compile(r"^\s*\*\s+-\s+\S")


def root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_anchor(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9一-龥]+", "-", value)
    return value.strip("-")


def heading_set(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return {normalize_anchor(match.group(1)) for match in re.finditer(r"^#{2,6}\s+(.+?)\s*#*\s*$", text, re.MULTILINE)}


def safe_target(root: Path, relative: str) -> Path | None:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        return None
    return root / path


def reference_exists(root: Path, reference: str, anchor_required: bool = True) -> bool:
    relative, separator, anchor = reference.partition("#")
    path = safe_target(root, relative)
    if path is None or not path.is_file():
        return False
    if not separator or not anchor_required:
        return True
    return normalize_anchor(anchor) in heading_set(path)


def active_tasks(root: Path) -> tuple[dict[str, dict], list[str]]:
    tasks: dict[str, dict] = {}
    warnings: list[str] = []
    for path in sorted((root / "docs/tasks").glob("tasks-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            warnings.append(f"无法解析任务文件：{path.relative_to(root)}")
            continue
        if not isinstance(data, dict) or data.get("domain") != DOMAIN:
            continue
        task_items = data.get("tasks", [])
        if not isinstance(task_items, list):
            warnings.append(f"任务文件 tasks 不是数组：{path.relative_to(root)}")
            continue
        for task in task_items:
            if not isinstance(task, dict):
                warnings.append(f"任务条目不是 object：{path.relative_to(root)}")
                continue
            task_id = task.get("taskId")
            if isinstance(task_id, str):
                if task_id in tasks:
                    warnings.append(f"重复 taskId：{task_id}（{tasks[task_id]['_manifest']} 与 {path.relative_to(root)}）")
                else:
                    tasks[task_id] = {**task, "_manifest": path.relative_to(root).as_posix()}
    return tasks, warnings


def rule_count(text: str) -> int:
    in_rules = False
    count = 0
    for line in text.splitlines():
        if re.match(r"^\s*\*?\s*@rules\s*$", line):
            in_rules = True
            continue
        if in_rules and re.match(r"^\s*\*?\s*@\w+", line):
            break
        if in_rules and RULE_LINE_RE.match(line):
            count += 1
    return count


def validate(root: Path) -> tuple[list[str], list[str], bool]:
    errors: list[str] = []
    warnings: list[str] = []
    tasks, task_warnings = active_tasks(root)
    warnings.extend(task_warnings)
    prds = [path for path in sorted((root / "docs/prds").glob("*.md")) if path.name not in {"_template.md", "REVIEW.md", "_intake-spec.md"}]
    java_files = sorted((root / "workspace/src/main/java").rglob("*.java")) if (root / "workspace/src/main/java").exists() else []
    test_files = sorted((root / "workspace/src/test/java").rglob("*.java")) if (root / "workspace/src/test/java").exists() else []
    active = bool(prds or tasks or java_files or test_files)
    if not active:
        return [], ["没有活跃 Java PRD、task 或 Java 源码；当前 workspace 尚未接入业务工程"], False

    for path in prds:
        text = path.read_text(encoding="utf-8")
        if "domain: java-backend" not in text:
            warnings.append(f"PRD 未声明 Java domain，跳过：{path.relative_to(root)}")

    for path in java_files + test_files:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for tag, reference in TAG_RE.findall(text):
            if tag == "prd" and not reference_exists(root, reference):
                errors.append(f"{relative}: @prd 不存在：{reference}")
            elif tag == "task":
                task_file, separator, task_id = reference.partition("#")
                if not separator or safe_target(root, task_file) is None or not (root / task_file).is_file():
                    errors.append(f"{relative}: @task 文件不存在：{reference}")
                elif task_id not in tasks:
                    warnings.append(f"{relative}: @task 未出现在活跃 Java task 中：{reference}")
                elif tasks[task_id].get("filePath") not in {relative, relative.removeprefix("workspace/")}:
                    warnings.append(f"{relative}: @task 的 filePath 与当前文件不一致：{reference} → {tasks[task_id].get('filePath')}")
            elif tag == "api" and not reference_exists(root, reference):
                errors.append(f"{relative}: @api 不存在：{reference}")
        if path in java_files and rule_count(text) == 0:
            errors.append(f"{relative}: 缺少可解析的 @rules")

    for task_id, task in tasks.items():
        file_path = task.get("filePath")
        if not isinstance(file_path, str):
            continue
        target = root / file_path
        if task.get("status") == "done" and not target.exists():
            errors.append(f"{task.get('_manifest')}#{task_id}: done 文件不存在：{file_path}")
        prd_ref = task.get("prdRef", "")
        if not reference_exists(root, prd_ref):
            errors.append(f"{task.get('_manifest')}#{task_id}: prdRef 不存在：{prd_ref}")

    for source in java_files:
        expected = root / source.relative_to(root).as_posix().replace("workspace/src/main/", "workspace/src/test/").replace(".java", "Test.java")
        if not expected.exists():
            warnings.append(f"缺少同名测试（仅提示）：{source.relative_to(root)} → {expected.relative_to(root)}")
    return errors, warnings, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="覆盖工作流根目录")
    args = parser.parse_args()
    root = (args.root or Path(os.environ.get("WORKFLOW_ROOT", str(root_dir())))).resolve()
    errors, warnings, applicable = validate(root)
    status = "NOT_APPLICABLE" if not applicable else ("FAIL" if errors else "PASS")
    print(f"{status} check-traceability: {root}")
    for error in errors:
        print(f"- ERROR {error}")
    for warning in warnings:
        print(f"- WARN {warning}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
