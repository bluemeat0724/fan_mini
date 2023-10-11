from fastapi import APIRouter, Depends
from starlette.requests import Request

from config.connections import get_db
from services.user_service import WechatUserService, get_current_user, UserUpdateSchema, UserType, UserInfoSchema

router = APIRouter()


@router.get('/login/info')
@router.get('/login/')
def login(code: str, request: Request, db=Depends(get_db)):
    info = True if request.url.path.endswith('info') else False
    user_info = WechatUserService(db).get_token(code, info=info)
    return user_info


@router.get('/info',
            response_model=UserInfoSchema)
def userinfo(current_user: get_current_user = Depends(), db=Depends(get_db)):
    user = WechatUserService(db).load_user(openid=current_user.openid)
    return user


@router.post('/update',
             response_model=UserInfoSchema
             )
def update_userinfo(userinfo: UserUpdateSchema, current_user: get_current_user = Depends(), db=Depends(get_db)):
    if userinfo.mobile and current_user.type_code == UserType.logged:  # 如果用户提供手机号，且当前用户是未验证用户，则将当前用户升级为验证用户
        userinfo.type_code = UserType.validated
    else:
        userinfo.type_code = current_user.type_code

    user = WechatUserService(db).update_user(openid=current_user.openid, userinfo=userinfo)
    return user
