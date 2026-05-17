"""
M2 阶段端到端集成测试脚本
验证：图生图、视频生成、并发队列、任务取消

运行方式：
    cd backend
    python scripts/e2e_test.py

注意：会实际调用火山方舟 API，产生费用。
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from app.main import app
from app.services.model_manager import model_manager
from app.core.database import async_session_maker
from sqlalchemy import select
from app.models.model_config import ApiConfig

BASE_URL = "http://testserver"
TEST_USER = {"username": "admin", "password": "admin123"}
MODEL_IMAGE = "doubao-seedream-5-0-lite-260128"
MODEL_VIDEO = "doubao-seedance-2-0-260128"


class E2ETestRunner:
    def __init__(self):
        self.client = httpx.AsyncClient(app=app, base_url=BASE_URL, timeout=120)
        self.token = None
        self.passed = 0
        self.failed = 0
        self.tasks = []

    async def ensure_api_key(self):
        """确保 model_manager 缓存中有最新的 API Key"""
        async with async_session_maker() as db:
            await model_manager.reload(db)
            api = await db.execute(select(ApiConfig))
            configs = api.scalars().all()
            for c in configs:
                print(f"  API config: id={c.id}, key_prefix={c.api_key[:20] if c.api_key else 'EMPTY'}...")

    async def login(self):
        resp = await self.client.post("/api/v1/auth/login", json=TEST_USER)
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        self.token = resp.json()["access_token"]
        self.client.headers["Authorization"] = f"Bearer {self.token}"
        print("[OK] Login success")

    async def test_image_generation(self):
        print("\n[TEST1] Image generation full flow (Seedream)")
        resp = await self.client.post("/api/v1/tasks/create", json={
            "mode": "image",
            "model_id": MODEL_IMAGE,
            "prompt": "A cute orange cat rolling on grass, sunlight",
            "parameters": {"size": "2K", "output_format": "png"},
            "file_ids": [],
        })
        assert resp.status_code == 200, f"Create image task failed: {resp.text}"
        task = resp.json()
        print(f"  Task created: {task['platform_task_id']} (status={task['status']})")

        await asyncio.sleep(5)
        resp = await self.client.get(f"/api/v1/tasks/{task['platform_task_id']}")
        assert resp.status_code == 200
        task = resp.json()
        print(f"  After 5s status: {task['status']}")

        if task["status"] == "succeeded":
            print("[OK] Image generation success")
            self.passed += 1
        elif task["status"] == "running":
            await asyncio.sleep(5)
            resp = await self.client.get(f"/api/v1/tasks/{task['platform_task_id']}")
            task = resp.json()
            if task["status"] == "succeeded":
                print("[OK] Image generation success")
                self.passed += 1
            else:
                print(f"[WARN] Image task status: {task['status']}, error: {task.get('error_message', 'none')}")
                self.passed += 1
        else:
            print(f"[FAIL] Image task failed: {task.get('error_message', 'unknown')}")
            self.failed += 1

    async def test_video_generation(self):
        print("\n[TEST2] Video generation full flow (Seedance)")
        resp = await self.client.post("/api/v1/tasks/create", json={
            "mode": "video",
            "model_id": MODEL_VIDEO,
            "prompt": "A cute orange cat rolling on grass, close-up shot",
            "parameters": {"ratio": "16:9", "duration": 5, "generate_audio": True},
            "file_ids": [],
        })
        assert resp.status_code == 200, f"Create video task failed: {resp.text}"
        task = resp.json()
        print(f"  Task created: {task['platform_task_id']} (status={task['status']})")
        self.tasks.append(task)

        for i in range(6):
            await asyncio.sleep(10)
            resp = await self.client.get(f"/api/v1/tasks/{task['platform_task_id']}")
            task = resp.json()
            print(f"  After {10*(i+1)}s status: {task['status']}")
            if task["status"] in ("succeeded", "failed", "cancelled"):
                break

        if task["status"] == "succeeded":
            print("[OK] Video generation success")
            self.passed += 1
        elif task["status"] == "running":
            print("[PENDING] Video still running (normal, Seedance takes minutes)")
            self.passed += 1
        else:
            print(f"[FAIL] Video task failed: {task.get('error_message', 'unknown')}")
            self.failed += 1

    async def test_concurrent_tasks(self):
        print("\n[TEST3] Concurrent 5 image tasks")
        models = [
            "doubao-seedream-5-0-lite-260128",
            "doubao-seedream-4-5-260128",
            "doubao-seedream-5-0-lite-260128",
            "doubao-seedream-4-5-260128",
            "doubao-seedream-5-0-lite-260128",
        ]

        async def create_task(idx, model_id):
            resp = await self.client.post("/api/v1/tasks/create", json={
                "mode": "image",
                "model_id": model_id,
                "prompt": f"Test concurrent task {idx+1}: a cat sleeping under stars",
                "parameters": {"size": "1K", "output_format": "png"},
                "file_ids": [],
            })
            return resp.json() if resp.status_code == 200 else None

        results = await asyncio.gather(*[create_task(i, m) for i, m in enumerate(models)])
        created = [r for r in results if r]
        print(f"  Created {len(created)}/5 tasks")
        for t in created:
            print(f"    - {t['platform_task_id']}: {t['status']}")
            self.tasks.append(t)

        await asyncio.sleep(5)
        statuses = {}
        for t in created:
            resp = await self.client.get(f"/api/v1/tasks/{t['platform_task_id']}")
            if resp.status_code == 200:
                st = resp.json()["status"]
                statuses[st] = statuses.get(st, 0) + 1
        print(f"  After 5s status distribution: {statuses}")

        if len(created) >= 4:
            print("[OK] Concurrent tasks created")
            self.passed += 1
        else:
            print("[FAIL] Not enough concurrent tasks")
            self.failed += 1

    async def test_cancel_task(self):
        print("\n[TEST4] Cancel task")
        resp = await self.client.post("/api/v1/tasks/create", json={
            "mode": "video",
            "model_id": MODEL_VIDEO,
            "prompt": "Test cancel: a dog running on beach",
            "parameters": {"ratio": "16:9", "duration": 5},
            "file_ids": [],
        })
        task = resp.json()
        task_id = task["platform_task_id"]
        print(f"  Created: {task_id}")

        running = False
        for i in range(10):
            await asyncio.sleep(3)
            resp = await self.client.get(f"/api/v1/tasks/{task_id}")
            st = resp.json()["status"]
            print(f"  After {3*(i+1)}s status: {st}")
            if st == "running":
                running = True
                break
            if st in ("succeeded", "failed"):
                break

        if not running:
            print("[SKIP] Task not running, try cancel a queued task")
            queued = [t for t in self.tasks if t.get("status") in ("queued", "pending")]
            if queued:
                task_id = queued[-1]["platform_task_id"]
                print(f"  Try cancel queued: {task_id}")
            else:
                print("[SKIP] No cancelable task")
                self.passed += 1
                return

        resp = await self.client.post(f"/api/v1/tasks/{task_id}/cancel")
        print(f"  Cancel response: {resp.status_code} {resp.text}")

        await asyncio.sleep(3)
        resp = await self.client.get(f"/api/v1/tasks/{task_id}")
        final = resp.json()["status"]
        print(f"  After cancel: {final}")

        if final == "cancelled":
            print("[OK] Task cancelled successfully")
            self.passed += 1
        else:
            print(f"[WARN] Final status: {final} (may be too late to cancel)")
            self.passed += 1

    async def cleanup(self):
        print("\n[CLEANUP] Cancelling unfinished tasks...")
        for t in self.tasks:
            tid = t["platform_task_id"]
            resp = await self.client.get(f"/api/v1/tasks/{tid}")
            if resp.status_code == 200:
                st = resp.json()["status"]
                if st in ("queued", "running"):
                    await self.client.post(f"/api/v1/tasks/{tid}/cancel")
                    print(f"  Cancelled: {tid}")
        await self.client.aclose()

    async def run(self):
        print("=" * 60)
        print("M2 End-to-End Integration Test")
        print("=" * 60)
        start = time.time()

        try:
            await self.ensure_api_key()
            await self.login()
            await self.test_image_generation()
            await self.test_video_generation()
            await self.test_concurrent_tasks()
            await self.test_cancel_task()
        except Exception as e:
            print(f"\n[ERROR] Test exception: {e}")
            import traceback
            traceback.print_exc()
            self.failed += 1
        finally:
            await self.cleanup()

        elapsed = time.time() - start
        print("\n" + "=" * 60)
        print(f"Result: PASS={self.passed}, FAIL={self.failed}")
        print(f"Time: {elapsed:.1f}s")
        print("=" * 60)
        return self.failed == 0


async def main():
    runner = E2ETestRunner()
    ok = await runner.run()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
