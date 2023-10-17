from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.requests import Request

from apis.services.order import WechatOrderService
from config.connections import get_db
from services.user_service import WechatUserService, get_current_user, UserUpdateSchema, UserType, UserInfoSchema

router = APIRouter()


@router.get('/login/info', summary='登录 小程序code获取用户信息与token ')
@router.get('/login/', summary='登录 小程序code获取token')
def login(code: str, request: Request, db=Depends(get_db)):
    info = True if request.url.path.endswith('info') else False
    user_info = WechatUserService(db).get_token(code, info=info)
    return user_info


@router.get('/info',
            response_model=UserInfoSchema, summary='查看用户信息', description='请求头 Authorization: Bearer token')
def userinfo(current_user: get_current_user = Depends(), db=Depends(get_db)):
    user = WechatUserService(db).load_user(openid=current_user.openid)
    return user


@router.post('/update',
             response_model=UserInfoSchema,
             summary='更新用户信息 昵称 头像 手机号'
             )
def update_userinfo(userinfo: UserUpdateSchema, current_user: get_current_user = Depends(), db=Depends(get_db)):
    if userinfo.mobile and current_user.type_code == UserType.logged:  # 如果用户提供手机号，且当前用户是未验证用户，则将当前用户升级为验证用户
        userinfo.type_code = UserType.validated
    else:
        userinfo.type_code = current_user.type_code

    user = WechatUserService(db).update_user(openid=current_user.openid, userinfo=userinfo)
    return user


class Payment(BaseModel):
    amount: Optional[int] = 1
    description: Optional[str] = '测试'


@router.post('/pay/mini',
             summary='小程序下单支付')
def pay_mini(payment: Payment, current_user: get_current_user = Depends(), db=Depends(get_db)):
    openid = current_user.openid
    response = WechatOrderService.simple_pay(openid=openid, amount=payment.amount, description=payment.description,
                                             db=db)
    return response


@router.post('/pay/notify',
             summary='小程序支付通知回调')
async def pay_mini(request: Request, db=Depends(get_db)):
    response = await WechatOrderService.pay_notify(request, db)
    return response
