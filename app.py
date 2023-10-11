import uvicorn
import os

if os.getenv("MODE", "dev") != "prod":
    from icecream import install
    install()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.config import settings
from common.response import StructuredResponse
from apis.user import router as userrouter
from common.middlewares import pub_exception_handler

app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
    default_response_class=StructuredResponse,
)


@app.exception_handler(Exception)
def pub_exception_handler(request, exc, code=400):
    return StructuredResponse(content=str(exc), success=False, status_code=code)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return StructuredResponse(content=str(exc.detail), success=False, status_code=exc.status_code)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(userrouter, prefix="/user", tags=["用户模块"])

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8009, workers=1)
