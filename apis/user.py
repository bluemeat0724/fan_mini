from fastapi import APIRouter, Depends
from pydantic import BaseModel

from config.connections import get_db
from services.user_service import WechatUserService

router = APIRouter()

class RequestToken(BaseModel):
    code: str

@router.post('/login')
def get_wechat_token(param: RequestToken, db=Depends(get_db)):
    token = WechatUserService(db).get_user_token(param.code)
    return token