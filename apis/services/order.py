"""
Author: G
Time: 2023 2023/10/17 15:43
File: order.py
"""
from random import sample
from string import ascii_letters, digits

from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from common.response import StructuredResponse
from db_models.m_orders import WechatOrder
from wechatlib.merchant import pay_miniprog, pay_callback


class WechatOrderService:
    out_trade_no = ''.join(sample(ascii_letters + digits, 8))

    @classmethod
    def create_order(cls, openid, amount, db: Session, description=''):
        out_trade_no = ''.join(sample(ascii_letters + digits, 8))

        order = WechatOrder(out_trade_no=out_trade_no,
                            amount=amount,
                            openid=openid,
                            description=description)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @classmethod
    def make_payment(cls, out_trade_no, openid, amount, description):
        success, data = pay_miniprog(out_trade_no=out_trade_no, openid=openid, amount=amount, description=description)
        return success, data

    @classmethod
    def simple_pay(cls, openid, amount, db: Session, description=''):
        """
        简单支付流程，创建订单并支付
        """
        order = cls.create_order(openid=openid, amount=amount, db=db, description=description)
        success, data = cls.make_payment(out_trade_no=order.out_trade_no, openid=openid, amount=amount,
                                         description=description)
        if success:
            return data
        else:
            order.trade_state = 'failed'
            order.trade_state_desc = data['reason']
            db.commit()
            return StructuredResponse(content=data['reason'], success=False, status_code=200)

    @classmethod
    async def pay_notify(cls, request: Request, db: Session):
        result = await pay_callback(request)
        if result and result.get('event_type') == 'TRANSACTION.SUCCESS':
            resp = result.get('resource')
            out_trade_no = resp.get('out_trade_no')
            transaction_id = resp.get('transaction_id')
            trade_state = resp.get('trade_state')
            trade_state_desc = resp.get('trade_state_desc')

            order = db.query(WechatOrder).filter(WechatOrder.out_trade_no == out_trade_no).first()
            if order:
                order.trade_state = trade_state
                order.trade_state_desc = trade_state_desc
                order.transaction_id = transaction_id
                order.response_info = result
                db.commit()

            return {'code': 'SUCCESS', 'message': '成功'}
        else:
            return StructuredResponse(content='支付失败', success=False, status_code=status.HTTP_204_NO_CONTENT)

    def get_order_by_id(self, order_id, db: Session):
        order = db.query(WechatOrder).filter(WechatOrder.id == order_id).first()
        return order
