from fastapi import APIRouter

from app.api.endpoints import (
    getTask,
    recallTask,
    test
)

api_router = APIRouter()

api_router.include_router(getTask.router, tags=["getTask"])
api_router.include_router(recallTask.router, tags=["recallTask"])
api_router.include_router(test.router, tags = ["test"])