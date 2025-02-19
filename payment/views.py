import datetime
import hashlib

from django.shortcuts import render
from django.utils.crypto import get_random_string


def payment_request(request):
    merchant_key = "----"  # 상점키
    merchant_id = "----"  # 상점아이디
    goods_name = "코페이"  # 결제상품명
    price = "1004"  # 결제상품금액
    buyer_name = "코페이"  # 구매자명
    buyer_tel = "01000000000"  # 구매자연락처
    buyer_email = "test@korpay.com"  # 구매자메일주소
    moid = get_random_string(16)  # 상품주문번호 (unique하게 생성)
    return_url = "https://pgapi.korpay.com/returnUrlSample.do"  # 결과페이지(절대경로)

    edi_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 전문 생성일시
    hash_string = hashlib.sha256((merchant_id + edi_date + price + merchant_key).encode("utf-8")).hexdigest()  # Hash 값

    context = {
        "merchantKey": merchant_key,
        "merchantID": merchant_id,
        "goodsName": goods_name,
        "price": price,
        "buyerName": buyer_name,
        "buyerTel": buyer_tel,
        "buyerEmail": buyer_email,
        "moid": moid,
        "returnURL": return_url,
        "ediDate": edi_date,
        "hashString": hash_string,
    }

    return render(request, "payment/templates/payment_request.html", context)
