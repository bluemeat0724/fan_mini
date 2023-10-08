from typing import Optional

from pydantic import BaseModel

from wechatlib.services import WeChatAPI


class WechatUserLog(BaseModel):
    openid: str
    unionid: Optional[str] = None

class WechatBaseService:
    user_model = None

    def __init__(self, db):
        self.db = db
        self.api_service = WeChatAPI()

    def create_user(self, openid: str, unionid: str):
        user = self.user_model(openid=openid, unionid=unionid)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def load_user(self, openid: str, unionid: str = None):
        user = self.db.query(self.user_model).filter(self.user_model.openid == openid).first()
        if not user:
            user = self.create_user(openid, unionid)
        return user

    def user_info(self, code: str):
        openid, unionid, _ = self.api_service.auth_info(code)
        user = self.load_user(openid, unionid)
        return user


