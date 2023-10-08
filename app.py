import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from apis import api_router

if os.getenv("MODE", "dev") != "prod":
    from icecream import install
    install()

from config.config import settings
from common.response import StructuredResponse
import logging.config

app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
    default_response_class=StructuredResponse,
)

app.include_router(api_router)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8009, workers=1)
