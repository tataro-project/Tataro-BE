from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        try:
            return Response({"message": "로그아웃 성공", "status": "success"}, status=200)
        except Exception:
            return Response({"message": "로그아웃 처리 시도에서 에러", "status": "failed"}, status=401)
