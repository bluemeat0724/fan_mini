from fastapi import APIRouter, Depends, Form, HTTPException

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from common.token_service import TokenService, get_current_user
from config.connections import get_db
from services.user_service import WechatUserService

router = APIRouter()


@router.get('/code')
def code(request: Request, db=Depends(get_db)):
    redirect = request.query_params
    print(type(redirect))
    print('redirect', redirect.get('redirect'))
    code = 1
    return RedirectResponse(f'http://localhost:8000/user/token?code={code}')


@router.get('/token')
def get_wechat_token(
        code: str,
        db=Depends(get_db)):
    token_info = WechatUserService(db).get_token(code)
    return token_info


@router.get('/info')
def userinfo(payload: get_current_user = Depends(), db=Depends(get_db)):
    return payload
