"""
Author: G
Time: 2023 2023/10/9 14:11
File: merchant.py
"""
import requests
import json
import logging
import os
import time
import uuid


from wechatpayv3 import WeChatPay, WeChatPayType,SignType

# https://wechatpay-api.gitbook.io/wechatpay-api-v3/
APPID= 'wx86d99aa50962f24a'  # 小程序ID
APPSECRET= 'b8f4edd8d0870a4f0cfb1e0f780c7c65'  # 小程序SECRET
MCHID='1625210809'  # 商户号
MCH_KEY='qwe123rty456uio789asd123zxc456vb'

# 商户证书私钥
with open('./path_to_key/apiclient_key.pem') as f:
    PRIVATE_KEY = f.read()
# 商户证书序列号
CERT_SERIAL_NO = '683915C02A8494FB3EF463903781551042F6556E'
# API v3密钥， https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay3_2.shtml
APIV3_KEY = 'efe6487fcc7911ec836e5414ABCDabcd'
# 微信支付平台证书缓存目录
CERT_DIR = './cert'
# 回调地址
# NOTIFY_URL = 'https://www.weixin.qq.com/wxpay/pay.php'
NOTIFY_URL = 'https://locallife.zen-x.com.cn/apis/paynotify'
# 日志记录器，记录web请求和回调细节，便于调试排错
logging.basicConfig(filename=os.path.join(os.getcwd(), 'wepay.log'), level=logging.DEBUG, filemode='a', format='%(asctime)s - %(process)s - %(levelname)s: %(message)s')
LOGGER = logging.getLogger("wepay")

# 接入模式:False=直连商户模式，True=服务商模式
PARTNER_MODE = False
code2session_url="https://api.weixin.qq.com/sns/jscode2session?grant_type=authorization_code"
jsapi_create='https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi'

wxpay = WeChatPay(
    wechatpay_type=WeChatPayType.MINIPROG,
    mchid=MCHID,
    private_key=PRIVATE_KEY,
    cert_serial_no=CERT_SERIAL_NO,
    apiv3_key=APIV3_KEY,
    appid=APPID,
    notify_url=NOTIFY_URL,
    partner_mode=PARTNER_MODE,
    logger=LOGGER,
    cert_dir=CERT_DIR)



#登录信息
def getLoginInfo(code):
    url = code2session_url
    params = {'appid':APPID,'secret':APPSECRET,'js_code':code}
    re_data = requests.get(url,params=params)
    json_response = re_data.content.decode()  # 获取的文本 就是一个json字符串
    # 将json字符串转换成dic字典对象
    data = json.loads(json_response)
    if data.get('session_key'):
        return data
    return  False


# 统一下单 小程序获得prepay_id
def pay(tradeno,openid,amount=100):
    code, message = wxpay.pay(
        description='诚心拜一拜',
        out_trade_no=tradeno,
        amount={'total': amount},
        payer={'openid': openid}
    )
    result = json.loads(message)
    if code in range(200, 300):
        prepay_id = result.get('prepay_id')
        timestamp = str(int(time.time()))
        noncestr = str(uuid.uuid4())
        package = 'prepay_id=' + prepay_id
        paysign = wxpay.sign(data=[APPID, timestamp, noncestr, package], sign_type=SignType.RSA_SHA256)
        signtype = 'RSA'
        return code,{
            'appId': APPID,
            'timeStamp': timestamp,
            'nonceStr': noncestr,
            'package': 'prepay_id=%s' % prepay_id,
            'signType': signtype,
            'paySign': paysign
        }
    else:
        return code,message

def pay_callback(request):
    headers = {}
    headers.update({'Wechatpay-Signature': request.META.get('HTTP_WECHATPAY_SIGNATURE')})
    headers.update({'Wechatpay-Timestamp': request.META.get('HTTP_WECHATPAY_TIMESTAMP')})
    headers.update({'Wechatpay-Nonce': request.META.get('HTTP_WECHATPAY_NONCE')})
    headers.update({'Wechatpay-Serial': request.META.get('HTTP_WECHATPAY_SERIAL')})
    result = wxpay.callback(headers=headers, body=request.body)
    return result

# 订单查询
def query():
    code, message = wxpay.query(
        transaction_id='demo-transation-id'
    )
    print('code: %s, message: %s' % (code, message))

# 关闭订单
def close():
    code, message = wxpay.close(
        out_trade_no='demo-out-trade-no'
    )
    print('code: %s, message: %s' % (code, message))

# 申请退款
def refund():
    code, message=wxpay.refund(
        out_refund_no='demo-out-refund-no',
        amount={'refund': 100, 'total': 100, 'currency': 'CNY'},
        transaction_id='1217752501201407033233368018'
    )
    print('code: %s, message: %s' % (code, message))

# 退款查询
def query_refund():
    code, message = wxpay.query_refund(
        out_refund_no='demo-out-refund-no'
    )
    print('code: %s, message: %s' % (code, message))

# 申请交易账单
def trade_bill():
    code, message = wxpay.trade_bill(
        bill_date='2021-04-01'
    )
    print('code: %s, message: %s' % (code, message))


if __name__=="__main__":
    # 支付
    class WePay(APIView):
        def get(self, request):
            # 创建系统订单
            openid = request.GET['openid']
            payment = request.GET['payment']  # 人民币 分
            order_id = str(uuid.uuid4())[:20]
            # 创建微信订单
            code, message = pay(tradeno=order_id, openid=openid, amount=int(payment))
            if code == 200:
                models.Orders.objects.create(status=1, openid=openid, order_id=order_id, payment=payment)
                return APIResponse(code=code, data_msg=f"下单", data=message)
            else:
                return APIResponse(code=code, data_msg=f"下单失败", data=message)


    # 支付通知
    class WePayNotify(APIView):
        def post(self, request):
            callback = pay_callback(request)
            paymentinfo = callback.get('resource')
            if paymentinfo:
                order_id = paymentinfo.get('out_trade_no')
                models.Orders.objects.filter(order_id=order_id).update(status=2)
                return APIResponse(code=200, data_msg='success')
            else:
                return APIResponse(code='400', data_msg='failed')
