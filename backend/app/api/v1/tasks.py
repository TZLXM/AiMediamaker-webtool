"""
任务路由 - 创建、查询、取消任务
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.task import Task, TaskMode, TaskStatus
from ...models.user import User
from ...schemas.task import TaskCreate, TaskResponse, TaskCancel, TaskHistoryFilter
from ...services.task_queue import task_queue
from ...api.deps import get_db, get_current_user

router = APIRouter()


@router.post("/create", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建生成任务"""
    mode = TaskMode.IMAGE if data.mode == "image" else TaskMode.VIDEO
    
    task = await task_queue.enqueue(
        db=db,
        user_id=user.id,
        mode=mode,
        model_id=data.model_id,
        prompt=data.prompt,
        parameters=data.parameters.model_dump(exclude_none=True) if data.parameters else {},
        file_ids=data.file_ids or [],
    )
    
    # 启动异步处理
    from ...core.database import async_session_maker
    await task_queue.start_task_processing(async_session_maker, task.platform_task_id)
    
    return TaskResponse.model_validate(task)


@router.get("/{platform_task_id}", response_model=TaskResponse)
async def get_task(
    platform_task_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """查询单个任务状态 (仅限自己的任务)"""
    result = await db.execute(
        select(Task).where(
            and_(
                Task.platform_task_id == platform_task_id,
                Task.user_id == user.id,
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse.model_validate(task)


@router.post("/{platform_task_id}/cancel")
async def cancel_task(
    platform_task_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """取消任务 (仅限自己的任务)"""
    success = await task_queue.cancel_task(db, platform_task_id, user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel task")
    return {"success": True, "message": "Task cancelled"}


@router.get("/history/list", response_model=List[TaskResponse])
async def list_history(
    mode: str = None,
    search: str = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取历史任务列表 (仅限自己的已结束任务)"""
    query = select(Task).where(
        and_(
            Task.user_id == user.id,
            Task.status.in_([TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELLED]),
        )
    )
    
    if mode:
        query = query.where(Task.mode == mode)
    if search:
        query = query.where(Task.prompt.contains(search))
    
    query = query.order_by(Task.created_at)  # 升序：最晚生成的在最下方
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return [TaskResponse.model_validate(t) for t in tasks]
