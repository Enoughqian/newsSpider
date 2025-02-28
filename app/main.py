from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.config.env_config import settings
from app.config.log_init import log_init

import sys

app = FastAPI(docs_url="/news_server/_internal_doc", title=settings.PROJECT_NAME)

app.include_router(api_router, prefix=settings.API_STR)

@app.on_event("startup")
def on_startup():
    log_init()