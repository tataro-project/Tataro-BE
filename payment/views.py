import os
import uuid

import environ
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from portone_server_sdk._generated.payment.client import PaymentClient

from config.settings.base import BASE_DIR
from payment.models import Payment

env = environ.Env(DEBUG=(bool, False))  # DEBUG 기본값은 False

# PortOne 클라이언트 초기화..
portone_client = PaymentClient(secret=env("PORTONE_API_SECRET"))
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    environ.Env.read_env(env_path)


class VerifyPaymentView(View):
    def post(self, request):  # type: ignore
        """결제 검증 API"""
        imp_uid = request.POST.get("imp_uid")

        if not imp_uid:
            return JsonResponse({"error": "결제 정보가 없습니다."}, status=400)

        try:
            # PortOne에서 결제 정보 조회
            payment_data = portone_client.get_payment(imp_uid)  # type: ignore

            if not payment_data:
                return JsonResponse({"error": "결제 정보를 찾을 수 없습니다."}, status=400)

            # DB에서 해당 결제 조회
            try:
                payment = Payment.objects.get(imp_uid=imp_uid)
            except Payment.DoesNotExist:
                return JsonResponse({"error": "DB에서 결제 정보를 찾을 수 없습니다."}, status=400)

            # 결제 금액 검증
            if payment.amount != payment_data.amount:  # type: ignore
                return JsonResponse({"error": "결제 금액 불일치"}, status=400)

            # 결제 상태 업데이트
            payment.status = payment_data.status  # type: ignore
            payment.save()

            return JsonResponse({"message": "결제 검증 완료", "data": {"status": payment.status}})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class PaymentWebhookView(View):
    def post(self, request):  # type: ignore
        """PortOne 결제 웹훅 처리"""
        imp_uid = request.POST.get("imp_uid")
        status = request.POST.get("status")

        if not imp_uid or not status:
            return JsonResponse({"error": "잘못된 요청"}, status=400)

        try:
            # DB에서 결제 정보 조회
            try:
                payment = Payment.objects.get(imp_uid=imp_uid)
            except Payment.DoesNotExist:
                return JsonResponse({"error": "결제 정보를 찾을 수 없습니다."}, status=400)

            # 결제 상태 업데이트
            payment.status = status
            payment.save()

            return JsonResponse({"message": "결제 상태 업데이트 완료", "status": status})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class CreatePaymentView(View):
    def post(self, request):  # type: ignore
        """결제 요청 API"""
        merchant_uid = request.POST.get("merchant_uid")
        amount = request.POST.get("amount")
        buyer_email = request.POST.get("buyer_email")
        buyer_name = request.POST.get("buyer_name")
        buyer_tel = request.POST.get("buyer_tel")

        if not merchant_uid or not amount:
            return JsonResponse({"error": "주문번호와 결제 금액이 필요합니다."}, status=400)

        # DB에 결제 정보 저장
        payment = Payment.objects.create(
            merchant_uid=merchant_uid,
            amount=int(amount),
            status="pending",
        )

        return JsonResponse({"message": "결제 요청 생성 완료", "payment_id": payment.id})


def payment_page(request):  # type: ignore
    return render(request, "payment_request.html")
