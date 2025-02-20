import environ
import portone_server_sdk as portone
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from portone_server_sdk._generated.payment.client import PaymentClient

env = environ.Env(DEBUG=(bool, False))  # DEBUG 기본값은 False

# PortOne 클라이언트 초기화..
portone_client = PaymentClient(secret=env("PORTONE_API_SECRET") or "")


class VerifyPaymentView(View):
    def post(self, request):  # type: ignore
        """결제 검증 API"""
        imp_uid = request.POST.get("imp_uid")  # 클라이언트에서 전달한 결제 고유번호

        if not imp_uid:
            return JsonResponse({"error": "결제 정보가 없습니다."}, status=400)

        try:
            # 결제 정보 조회
            payment_data = portone_client.get_payment(imp_uid)  # type: ignore

            if not payment_data:
                return JsonResponse({"error": "결제 정보를 찾을 수 없습니다."}, status=400)

            # 데이터베이스에서 주문 정보와 비교 (예: 주문 금액 검증)
            order_amount = 10000  # 실제 DB에서 주문 금액을 가져와야 함
            if payment_data.amount != order_amount:  # type: ignore
                return JsonResponse({"error": "결제 금액 불일치"}, status=400)

            # 결제 성공 처리 (DB 업데이트 등)
            return JsonResponse({"message": "결제 검증 완료", "data": payment_data.dict()})  # type: ignore

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
            # 결제 정보 가져오기
            payment_data = portone_client.get_payment(imp_uid)  # type: ignore

            if not payment_data:
                return JsonResponse({"error": "결제 정보를 찾을 수 없습니다."}, status=400)

            # 결제 상태 업데이트 (DB 반영)
            # 예: Order.objects.filter(imp_uid=imp_uid).update(status=status)

            return JsonResponse({"message": "결제 상태 업데이트 완료"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
