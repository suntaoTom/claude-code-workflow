#!/usr/bin/env python3
"""Validate Java backend task manifest structure and dependency graph."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

DOMAIN = "java-backend"
VALID_STATUS = {"pending", "in-progress", "done", "blocked"}
VALID_TYPES = {
    "contract", "schema", "config", "migration", "domain", "dao", "service", "controller",
    "websocket", "messaging", "cache", "observability", "security", "unit-test", "integration-test",
    "contract-test", "docker", "ci", "deploy", "runbook", "docs", "precondition",
}
INFRA_TYPES = {"contract", "schema", "config", "migration", "observability", "security", "docker", "ci", "deploy", "runbook", "docs", "precondition"}
JAVA_TYPES = {"domain", "dao", "service", "controller", "websocket", "messaging", "cache"}
TEST_TYPES = {"unit-test", "integration-test", "contract-test"}
ANCHOR_RE = re.compile(r"^#{2,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_anchor(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9一-龥]+", "-", value)
    return value.strip("-")


def safe_target(root: Path, relative: str) -> Path | None:
    if not isinstance(relative, str):
        return None
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        return None
    return root / path


def reference_exists(root: Path, reference: str) -> bool:
    if not isinstance(reference, str) or "#" not in reference:
        return False
    relative, anchor = reference.split("#", 1)
    path = safe_target(root, relative)
    if path is None or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return normalize_anchor(anchor) in {normalize_anchor(item) for item in ANCHOR_RE.findall(text)}


def validate(data: object, root: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["顶层必须是 JSON object"]
    if data.get("domain") != DOMAIN:
        errors.append("顶层 domain 必须为 java-backend")
    for field in ("moduleCode", "prdRef", "tasks", "createdAt"):
        if field not in data:
            errors.append(f"缺少顶层字段：{field}")
    if not isinstance(data.get("moduleCode"), str) or not data.get("moduleCode"):
        errors.append("moduleCode 必须是非空字符串")
    if not isinstance(data.get("createdAt"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data.get("createdAt", "")):
        errors.append("createdAt 必须是 YYYY-MM-DD 字符串")
    if not isinstance(data.get("prdRef"), str) or safe_target(root, data.get("prdRef", "")) is None:
        errors.append("顶层 prdRef 必须是安全的仓库相对路径")
    if not isinstance(data.get("tasks"), list):
        return errors + ["tasks 必须是数组"]
    if isinstance(data.get("prdRef"), str):
        prd_path = safe_target(root, data["prdRef"])
        if prd_path is not None and not prd_path.is_file():
            errors.append(f"顶层 prdRef 文件不存在：{data['prdRef']}")

    tasks = data["tasks"]
    ids: list[str] = []
    positions: dict[str, int] = {}
    by_id: dict[str, dict] = {}
    for index, task in enumerate(tasks):
        prefix = f"任务 {index + 1}"
        if not isinstance(task, dict):
            errors.append(f"{prefix} 必须是 object")
            continue
        required = ("taskId", "type", "name", "filePath", "description", "prdRef", "businessRules", "acceptanceCriteria", "dependencies", "status")
        for field in required:
            if field not in task:
                errors.append(f"{prefix} 缺少字段：{field}")
        task_id = task.get("taskId")
        if not isinstance(task_id, str) or not task_id:
            continue
        if task_id in by_id:
            errors.append(f"重复 taskId：{task_id}")
        ids.append(task_id)
        positions[task_id] = index
        by_id[task_id] = task
        if task.get("type") not in VALID_TYPES:
            errors.append(f"{task_id} type 不合法：{task.get('type')}")
        if task.get("status") not in VALID_STATUS:
            errors.append(f"{task_id} status 不合法：{task.get('status')}")
        file_path = task.get("filePath")
        if not isinstance(file_path, str) or Path(file_path).is_absolute() or ".." in Path(file_path).parts:
            errors.append(f"{task_id} filePath 必须是安全的仓库相对路径")
        elif not file_path.startswith(("workspace/", "docs/", "tools/", ".github/")):
            errors.append(f"{task_id} filePath 不在允许目录：{file_path}")
        task_type = task.get("type")
        if task_type in JAVA_TYPES and isinstance(file_path, str) and not file_path.startswith("workspace/src/main/"):
            errors.append(f"{task_id} Java 生产任务必须写入 workspace/src/main：{file_path}")
        if task_type in TEST_TYPES and isinstance(file_path, str) and not file_path.startswith("workspace/src/test/"):
            errors.append(f"{task_id} 测试任务必须写入 workspace/src/test：{file_path}")
        for field in ("businessRules", "acceptanceCriteria", "dependencies"):
            if not isinstance(task.get(field), list):
                errors.append(f"{task_id} {field} 必须是数组")
        if isinstance(task.get("acceptanceCriteria"), list) and not task["acceptanceCriteria"]:
            errors.append(f"{task_id} acceptanceCriteria 不能为空")
        if task_type not in INFRA_TYPES and isinstance(task.get("businessRules"), list) and not task["businessRules"]:
            errors.append(f"{task_id} 业务任务 businessRules 不能为空")
        if isinstance(task.get("businessRules"), list) and any("[待确认]" in str(rule) or "TODO" in str(rule) or "???" in str(rule) for rule in task["businessRules"]):
            errors.append(f"{task_id} businessRules 含占位符")
        if not reference_exists(root, task.get("prdRef", "")):
            errors.append(f"{task_id} prdRef 文件或锚点不存在：{task.get('prdRef')}")

    shared_paths = {"workspace/pom.xml", "workspace/src/main/resources/application.yml", "workspace/README.md"}
    for shared in shared_paths:
        owners = [task_id for task_id, task in by_id.items() if task.get("filePath") == shared]
        if len(owners) > 1:
            errors.append(f"共享文件被多个任务拥有：{shared}（{', '.join(owners)}）")

    graph: dict[str, list[str]] = {task_id: [] for task_id in by_id}
    for task_id, task in by_id.items():
        dependencies = task.get("dependencies", [])
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if dependency not in by_id:
                errors.append(f"{task_id} 依赖不存在的任务：{dependency}")
            else:
                graph[dependency].append(task_id)
                if positions[dependency] >= positions[task_id]:
                    errors.append(f"{task_id} 存在前向依赖：{dependency}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            errors.append(f"依赖图存在循环：{task_id}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for child in graph[task_id]:
            visit(child)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tasks", type=Path)
    args = parser.parse_args()
    root = Path(os.environ.get("WORKFLOW_ROOT", str(root_dir()))).resolve()
    path = args.tasks if args.tasks.is_absolute() else root / args.tasks
    if not path.is_file():
        print(f"FAIL validate-tasks: 文件不存在：{path}")
        return 1
    if path.name.startswith("_template"):
        print(f"NOT_APPLICABLE validate-tasks: 模板文件不参与任务校验：{path}")
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"FAIL validate-tasks: 无法读取 JSON：{error}")
        return 1
    errors = validate(data, root)
    if errors:
        print(f"FAIL validate-tasks: {path}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS validate-tasks: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
