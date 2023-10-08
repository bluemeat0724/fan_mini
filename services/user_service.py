from common.token_service import TokenService
from common.wechat_service import WechatBaseService
from db_models.m_users import WechatUser


class WechatUserService(WechatBaseService):
    user_model = WechatUser

    def get_user_token(self, code: str):
        user = self.user_info(code)
        token = TokenService().create_access_token(data={'id': user.id})
        return token