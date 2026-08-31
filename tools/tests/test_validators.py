"""Tests for the standard-library workflow validators."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"


class ValidatorTestCase(unittest.TestCase):
    def run_tool(self, tool: str, *arguments: str, root: Path | None = None) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        if root is not None:
            environment["WORKFLOW_ROOT"] = str(root)
        return subprocess.run(
            [sys.executable, str(TOOLS / tool), *arguments],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def write_prd(self, root: Path, content: str) -> Path:
        path = root / "docs/prds/module.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_tasks(self, root: Path, tasks: list[dict]) -> Path:
        path = root / "docs/tasks/tasks-module.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "domain": "java-backend",
                    "moduleName": "模块",
                    "moduleCode": "module",
                    "prdRef": "docs/prds/module.md",
                    "createdAt": "2026-08-31",
                    "tasks": tasks,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return path

    def valid_prd_content(self) -> str:
        return """# Java 后端能力需求书

## 元信息

| domain | java-backend |

## 背景与目标

实现一个后端能力。

## 能力点 1：连接

### 调用与边界

调用方通过 WebSocket 连接。

### 数据与协议

消息使用版本化 JSON。

### 业务规则

1. 当身份有效时，应允许建立连接。
2. 当身份无效时，应拒绝建立连接。

### 可靠性与异常

连接失败需可追踪。

## 配置项

| 配置键 | 默认/环境 |
|---|---|
| websocket.path | profile |

## 验收清单

- [ ] 有对应测试
"""

    def task(self, task_id: str, task_type: str, file_path: str, dependencies: list[str] | None = None) -> dict:
        return {
            "taskId": task_id,
            "type": task_type,
            "name": task_id,
            "filePath": file_path,
            "description": "实现任务",
            "prdRef": "docs/prds/module.md#能力点-1-连接",
            "apiRef": "",
            "businessRules": ["当身份有效时，应允许建立连接。"] if task_type not in {"config", "contract"} else [],
            "acceptanceCriteria": ["有可验证结果"],
            "dependencies": dependencies or [],
            "status": "pending",
        }

    def test_valid_prd_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_prd(root, self.valid_prd_content())
            result = self.run_tool("validate-prd.py", str(path), root=root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_prd_placeholders_and_conflict_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = self.valid_prd_content().replace("domain | java-backend", "domain | java-backend\n\n[待确认] 认证来源") + "\n## 冲突待决\n"
            path = self.write_prd(root, content)
            result = self.run_tool("validate-prd.py", str(path), root=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("[待确认]", result.stdout)
            self.assertIn("冲突待决", result.stdout)

    def test_valid_tasks_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_prd(root, self.valid_prd_content())
            path = self.write_tasks(
                root,
                [
                    self.task("T001", "contract", "docs/contracts/websocket/module.json"),
                    self.task("T002", "service", "workspace/src/main/java/example/Service.java", ["T001"]),
                    self.task("T003", "unit-test", "workspace/src/test/java/example/ServiceTest.java", ["T002"]),
                ],
            )
            result = self.run_tool("validate-tasks.py", str(path), root=root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_task_graph_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_prd(root, self.valid_prd_content())
            path = self.write_tasks(
                root,
                [
                    self.task("T001", "service", "workspace/src/main/java/example/Service.java", ["T002"]),
                    self.task("T002", "service", "workspace/src/main/java/example/Other.java", ["T001"]),
                ],
            )
            result = self.run_tool("validate-tasks.py", str(path), root=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("循环", result.stdout)

    def test_empty_traceability_is_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_tool("check-traceability.py", root=Path(directory))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("NOT_APPLICABLE", result.stdout)

    def test_traceability_checks_java_doc_and_task_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_prd(root, self.valid_prd_content())
            source = root / "workspace/src/main/java/example/Handler.java"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(
                """/**
 * @prd docs/prds/module.md#能力点-1-连接
 * @task docs/tasks/tasks-module.json#T001
 * @rules
 * - 当身份有效时，应允许建立连接。
 */
public class Handler {}
""",
                encoding="utf-8",
            )
            test_file = root / "workspace/src/test/java/example/HandlerTest.java"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("class HandlerTest {}\n", encoding="utf-8")
            tasks = self.write_tasks(root, [self.task("T001", "service", "workspace/src/main/java/example/Handler.java")])
            data = json.loads(tasks.read_text(encoding="utf-8"))
            data["tasks"][0]["status"] = "done"
            tasks.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            result = self.run_tool("check-traceability.py", root=root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("ERROR", result.stdout)


if __name__ == "__main__":
    unittest.main()
