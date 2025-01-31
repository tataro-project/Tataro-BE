from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


# 카카오 소셜 로그인 API
class KakaoSocialLoginView(APIView):
    def get(self, request: Request) -> Response:
        try:
            return Response({"access_token": "exampleToken", "refresh_token": "exampleRefreshToken"}, status=201)
        except Exception:
            return Response({"message": "사용자가 승인되지 않음"}, status=401)


# 카카오 토큰 재발급 API
class KakaoTokenReissueView(APIView):
    def post(self, request: Request) -> Response:
        try:
            return Response({"access_token": "new_access_token", "refresh_token": "new_refresh_token"}, status=200)
        except Exception:
            return Response({"message": "재발급 실패"}, status=401)
