from typing import Dict

from common.token_service import TokenService
from common.wechat_service import WechatBaseService
from db_models.m_users import WechatUser


class WechatUserService(WechatBaseService):
    user_model = WechatUser

    def get_token(self, code: str) -> Dict[str, str]:
        user = self.user_info(code)
        service = TokenService()
        token = service.create_access_token(data={'id': user.id})
        return {"access_token": token, "token_type": service.token_type}

