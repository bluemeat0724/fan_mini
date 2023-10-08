"""
Author: G
Time: 2023 2023/9/28 9:54
File: base.py
"""
import os
from pathlib import Path
from typing import Dict

from pydantic import Field, BaseModel, field_validator, model_validator, ConfigDict
import toml
from pydantic_settings import BaseSettings

HERE = Path(__file__).parent.absolute()


class BaseSchema(BaseModel):
    appid: str
    secret: str

    @model_validator(mode='before')
    def load_baseconfig(cls, values):
        if 'wechat_config' in globals():
            values['appid'] = wechat_config.appid
            values['secret'] = wechat_config.secret
        return values


class AuthSchema(BaseSchema):
    """
    微信授权schema
    """
    js_code: str
    grant_type: str = "authorization_code"


class AccessTokenSchema(BaseSchema):
    """
    access token schema
    """
    grant_type: str = "client_credential"


class PhoneInfoResponseSchema(BaseModel):
    phongNumber: str
    countryCode: str


class WechatUrl:
    # 微信授权相关url
    AccessTokenUrl = "cgi-bin/token"  # 获取access_token url
    AuthUrl = "sns/jscode2session"  # 微信授权openid等url
    AuthMobileUrl = "wxa/business/getuserphonenumber"  # 微信授权手机号url
    SecurityMediaUrl = "wxa/media_check_async"  # 微信内容安全监测相关url
    SecurityTextUrl = "wxa/msg_sec_check"
    SecurityImageUrl = "wxa/img_sec_check"
    MessagePushUrl = "cgi-bin/message/custom/send"  # 微信消息推送url
    ServiceNoticeUrl = "cgi-bin/message/subscribe/send"  # 微信服务通知url


class WechatConfig(BaseSettings):
    mode: str = Field('dev', exclude=True)
    appid: str = ''
    secret: str = ''
    baseurl: str = Field(default='https://api.weixin.qq.com/', exclude=True)

    @model_validator(mode='after')
    def load_app_config(cls, values):
        wechat = {}
        if "settings" in globals():
            if isinstance(settings, (Dict, BaseModel)):
                if hasattr(settings, 'wechat'):
                    wechat = settings.wechat
                if hasattr(settings, 'conf'):
                    wechat = settings.conf.get('wechat', {})
        if not wechat:
            wechat = toml.load(os.path.join(HERE, 'config.toml')).get(values.mode, {})
        values.appid = wechat.get('appid', '')
        values.secret = wechat.get('secret', '')
        values.baseurl = wechat.get('baseurl', '')


wechat_config = WechatConfig()

if __name__ == "__main__":
    print('c:', wechat_config)
