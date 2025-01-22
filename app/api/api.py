from fastapi import APIRouter

from app.api.endpoints import (
    getTitleRecTask,
    sendTitleCrawlTask,
    test
)

api_router = APIRouter()

api_router.include_router(getTitleRecTask.router, tags=["getTitleRecTask"])
api_router.include_router(sendTitleCrawlTask.router, tags=["sendTitleCrawlTask"])
api_router.include_router(test.router, tags = ["test"])