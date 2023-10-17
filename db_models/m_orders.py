"""
Author: G
Time: 2023 2023/10/17 13:43
File: m_orders.py
"""
from db_models.base import ModelBase

from sqlalchemy import UniqueConstraint, Column, Integer, String, BigInteger, Enum, Numeric, DateTime, Date, JSON, Text, \
    Boolean


class WechatOrder(ModelBase):
    __tablename__ = "wechat_order"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    out_trade_no = Column(String(255), index=True, unique=True, nullable=False, comment='商户订单号')
    description = Column(String(255), nullable=True, comment='订单描述')
    amount = Column(Integer, nullable=True, comment='订单金额(分)')
    openid = Column(String(255), index=True, nullable=True, comment='payer微信用户openid')
    trade_state = Column(String(64), nullable=True, default="pending", index=True)
    trade_state_desc = Column(String(255), nullable=True, comment='订单状态描述')

    transaction_id = Column(String(255), nullable=True, comment='微信支付订单号')
    response_info = Column(JSON, nullable=True, comment='微信支付回调信息')
