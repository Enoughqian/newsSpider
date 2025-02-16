from fastapi import APIRouter

from app.api.endpoints import (
    getTask,
    recallTask,
    getVec,
    filterList,
    getSingleInfo,
    setSingleInfo,
    test
)

api_router = APIRouter()

api_router.include_router(getTask.router, tags=["getTask"])
api_router.include_router(recallTask.router, tags=["recallTask"])
api_router.include_router(getVec.router, tags=["getVec"])
api_router.include_router(filterList.router, tags=["filterList"])
api_router.include_router(getSingleInfo.router, tags=["getSingleInfo"])
api_router.include_router(setSingleInfo.router, tags=["setSingleInfo"])
api_router.include_router(test.router, tags = ["test"])