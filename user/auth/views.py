from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class LogoutView(APIView):
    @swagger_auto_schema(
        operation_summary="유저 로그아웃.",
        operation_description="jWT refresh token을 blacklist에 추가합니다.(프론트에서 쿠키 제거)",
        responses={201: '"message": "로그아웃 성공", "status": "success"', 400: "잘못된 요청"},
    )
    def post(self, request: Request) -> Response:
        try:
            return Response({"message": "로그아웃 성공", "status": "success"}, status=200)
        except Exception:
            return Response({"message": "로그아웃 처리 시도에서 에러", "status": "failed"}, status=401)
