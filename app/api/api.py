from fastapi import APIRouter

from app.api.endpoints import (
    getTask,
    recallTask,
    getVec,
    filterList,
    getSingleInfo,
    setSingleInfo,
    showNews,
    filterUpload,
    filterTask,
    getCountry,
    getCountData,
    genWordFile,
    Login,
    getShowNews,
    test
)

api_router = APIRouter()

api_router.include_router(getTask.router, tags=["getTask"])
api_router.include_router(recallTask.router, tags=["recallTask"])
api_router.include_router(getVec.router, tags=["getVec"])
api_router.include_router(filterList.router, tags=["filterList"])
api_router.include_router(getSingleInfo.router, tags=["getSingleInfo"])
api_router.include_router(setSingleInfo.router, tags=["setSingleInfo"])
api_router.include_router(showNews.router, tags=["showNews"])
api_router.include_router(filterUpload.router, tags=["filterUpload"])
api_router.include_router(filterTask.router, tags=["filterTask"])
api_router.include_router(getCountry.router, tags=["getCountry"])
api_router.include_router(getCountData.router, tags=["getCountData"])
api_router.include_router(genWordFile.router, tags=["genWordFile"])
api_router.include_router(Login.router, tags=["Login"])
api_router.include_router(getShowNews.router, tags=["getShowNews"])
api_router.include_router(test.router, tags = ["test"])