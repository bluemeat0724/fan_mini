"""
Author: G
Time: 2023 2023/10/9 14:11
File: merchant.py
"""
from random import sample
from string import ascii_letters, digits

import requests
import json
import logging
import os
import time
import uuid

from wechatpayv3 import WeChatPay, WeChatPayType, SignType

from wechatlib.base import wechat_config

# https://github.com/minibear2021/wechatpayv3

# 日志记录器，记录web请求和回调细节，便于调试排错。
logging.basicConfig(filename=os.path.join(os.getcwd(), 'demo.log'), level=logging.DEBUG, filemode='a',
                    format='%(asctime)s - %(process)s - %(levelname)s: %(message)s')
LOGGER = logging.getLogger("demo")
HERE = os.path.dirname(os.path.abspath(__file__))

wxpay = WeChatPay(
    wechatpay_type=WeChatPayType.NATIVE,
    **wechat_config.pay_dump(),
    logger=LOGGER, )


# 统一下单 小程序获得prepay_id
def pay(description, amount=0.01):
    out_trade_no = ''.join(sample(ascii_letters + digits, 8))
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount},
        pay_type=WeChatPayType.NATIVE)
    return {'code': code, 'message': message}


def pay_miniprog(out_trade_no, openid, amount=1, description='测试', ):
    """
    下单
         下单成功后，将prepay_id和其他必须的参数组合传递给小程序的wx.requestPayment接口唤起支付
    """

    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount},
        payer={
            'openid': openid
        },
        pay_type=WeChatPayType.MINIPROG
    )
    result = json.loads(message)
    if code in range(200, 300):
        prepay_id = result.get('prepay_id')
        timestamp = str(int(time.time()))
        noncestr = str(uuid.uuid4()).replace('-', '')
        package = 'prepay_id=' + prepay_id
        sign = wxpay.sign([wechat_config.appid, timestamp, noncestr, package])
        signtype = 'RSA'
        return True, {
            'timeStamp': timestamp,
            'nonceStr': noncestr,
            'package': 'prepay_id=%s' % prepay_id,
            'signType': signtype,
            'paySign': sign,
            'out_trade_no': out_trade_no
        }
    else:
        return False, {'reason': result.get('detail')}


async def pay_callback(request):
    headers = {
        'Wechatpay-Signature': request.headers.get('wechatpay-signature'),
        'Wechatpay-Timestamp': request.headers.get('wechatpay-timestamp'),
        'Wechatpay-Nonce': request.headers.get('wechatpay-nonce'),
        'Wechatpay-Serial': request.headers.get('wechatpay-serial')
    }
    result = wxpay.callback(headers=headers, body=await request.body())
    return result


# 订单查询
def query():
    code, message = wxpay.query(
        transaction_id='demo-transation-id'
    )
    print('code: %s, message: %s' % (code, message))


#
#
# # 关闭订单
# def close():
#     code, message = wxpay.close(
#         out_trade_no='demo-out-trade-no'
#     )
#     print('code: %s, message: %s' % (code, message))
#
#
# # 申请退款
# def refund():
#     code, message = wxpay.refund(
#         out_refund_no='demo-out-refund-no',
#         amount={'refund': 100, 'total': 100, 'currency': 'CNY'},
#         transaction_id='1217752501201407033233368018'
#     )
#     print('code: %s, message: %s' % (code, message))
#
#
# # 退款查询
# def query_refund():
#     code, message = wxpay.query_refund(
#         out_refund_no='demo-out-refund-no'
#     )
#     print('code: %s, message: %s' % (code, message))
#
#
# # 申请交易账单
# def trade_bill():
#     code, message = wxpay.trade_bill(
#         bill_date='2021-04-01'
#     )
#     print('code: %s, message: %s' % (code, message))


if __name__ == "__main__":
    print(wechat_config.appid)
    # 支付
    # class WePay(APIView):
    #     def get(self, request):
    #         # 创建系统订单
    #         openid = request.GET['openid']
    #         payment = request.GET['payment']  # 人民币 分
    #         order_id = str(uuid.uuid4())[:20]
    #         # 创建微信订单
    #         code, message = pay(tradeno=order_id, openid=openid, amount=int(payment))
    #         if code == 200:
    #             models.Orders.objects.create(status=1, openid=openid, order_id=order_id, payment=payment)
    #             return APIResponse(code=code, data_msg=f"下单", data=message)
    #         else:
    #             return APIResponse(code=code, data_msg=f"下单失败", data=message)
    #
    #
    # # 支付通知
    # class WePayNotify(APIView):
    #     def post(self, request):
    #         callback = pay_callback(request)
    #         paymentinfo = callback.get('resource')
    #         if paymentinfo:
    #             order_id = paymentinfo.get('out_trade_no')
    #             models.Orders.objects.filter(order_id=order_id).update(status=2)
    #             return APIResponse(code=200, data_msg='success')
    #         else:
    #             return APIResponse(code='400', data_msg='failed')
