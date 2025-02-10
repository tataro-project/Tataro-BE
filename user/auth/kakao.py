import requests
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import User


class KakaoLoginView(APIView):
    @swagger_auto_schema(operation_description="카카오 로그인 URL 반환", responses={200: "로그인 URL 반환 성공"})
    def get(self, request: Request) -> Response:
        kakao_auth_url = (
            f"https://kauth.kakao.com/oauth/authorize?"
            f"client_id={settings.KAKAO_REST_API_KEY}&"
            f"redirect_uri={settings.KAKAO_REDIRECT_URI}&"
            f"response_type=code"
        )
        return Response({"auth_url": kakao_auth_url})


class KakaoCallbackView(APIView):
    @swagger_auto_schema(
        operation_description="카카오 로그인 콜백 처리",
        responses={200: "사용자 정보 반환", 400: "Authorization code is missing"},
    )
    def get(self, request: Request) -> Response:
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "Authorization code is missing"}, status=400)

        # Access Token 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }

        token_response = requests.post(token_url, headers=headers, data=data)
        if token_response.status_code != 200:
            return Response(
                {"error": "Failed to get access token", "details": token_response.text},
                status=token_response.status_code,
            )

        access_token = token_response.json().get("access_token")

        # 사용자 정보 요청
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code != 200:
            return Response(
                {"error": "Failed to get user info", "details": user_info_response.text},
                status=user_info_response.status_code,
            )

        user_info = user_info_response.json()

        # 사용자 정보 반환 (또는 데이터베이스 처리)
        return Response(
            {
                "user_id": User.id,
                "nickname": User.nickname,
            }
        )
