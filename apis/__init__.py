from fastapi import APIRouter

from apis.user import router as user

api_router = APIRouter()

api_router.include_router(user, prefix="/user", tags=["user"],
                          # dependencies=[Depends(check_token_middleware)]
                          )