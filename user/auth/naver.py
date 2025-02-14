import logging

import requests
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from config.settings.base import env
from user.models import User


class NaverLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        # 네이버 로그인 URL 생성
        naver_login_url = (
            f"https://nid.naver.com/oauth2.0/authorize?"
            f"response_type=code&client_id={env("NAVER_CLIENT_ID")}"
            f"&redirect_uri={env("NAVER_REDIRECT_URI")}&state=random_state_string"
        )
        return Response({"auth_url": naver_login_url}, status=status.HTTP_200_OK)


class NaverCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        # 콜백으로 전달된 code와 state 파라미터 받기
        code = request.GET.get("code")
        state = request.GET.get("state")

        # 액세스 토큰 요청
        token_url = (
            f"https://nid.naver.com/oauth2.0/token?"
            f"grant_type=authorization_code&client_id={env("NAVER_CLIENT_ID")}"
            f"&client_secret={env("NAVER_CLIENT_SECRET")}&code={code}&state={state}"
        )
        token_response = requests.get(token_url)
        token_data = token_response.json()

        if "access_token" not in token_data:
            return Response({"error": "Failed to retrieve access token"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")

        # 사용자 정보 요청
        profile_url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = requests.get(profile_url, headers=headers)
        profile_data = profile_response.json()

        if profile_data.get("message") != "success":
            return Response({"error": "Failed to retrieve user profile"}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자 정보 추출
        user_info = profile_data["response"]
        email = user_info.get("email")

        # 기존 사용자 조회
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            # 기존 사용자의 경우, 네이버 정보로 업데이트하지 않음
            user = existing_user
            created = False
        else:
            # 새로운 사용자 생성
            gender_map = {"M": "male", "F": "female"}
            user = User.objects.create(
                email=email,
                nickname=user_info.get("nickname", ""),
                gender=gender_map.get(user_info.get("gender"), None),
                birth=user_info.get("birth", None),
                social_type="NAVER",
                is_active=True,
            )
            created = True

        refresh = RefreshToken.for_user(user)

        # 응답 반환
        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "naver_refresh_token": refresh_token,
                "message": "User information retrieved successfully",
                "user_id": user.id,
                "created": created,
                "user_data": {
                    "email": user.email,
                    "nickname": user.nickname,
                    "gender": user.gender,
                    "birthday": user.birth,
                },
            },
            status=status.HTTP_200_OK,
        )

logger = logging.getLogger(__name__)

class NaverReissueView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="네이버 토큰 재발급",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh_token"],
            properties={
                "refresh_token": openapi.Schema(type=openapi.TYPE_STRING, description="리프레시 토큰"),
            },
        ),
        responses={
            200: openapi.Response(
                description="토큰 재발급 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="새로운 액세스 토큰"),
                        "token_type": openapi.Schema(type=openapi.TYPE_STRING),
                        "expires_in": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "잘못된 요청",
        },
    )

    def post(self, request: Request) -> Response:
        # 클라이언트로부터 refresh 토큰을 받아옴
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 네이버 토큰 갱신 API 엔드포인트
        url = "https://nid.naver.com/oauth2.0/token"

        # 요청 데이터 설정
        data = {
            "grant_type": "refresh_token",
            "client_id": env("NAVER_CLIENT_ID"),
            "client_secret": env("NAVER_CLIENT_SECRET"),
            "refresh_token": refresh_token,
        }

        # 네이버 API에 POST 요청 보내기
        response = requests.post(url, data=data)
        response_data = response.json()

        # 응답 처리
        if "error" in response_data:
            error_message = response_data.get("error_description", "Unknown error")
            return Response(
                {"error": response_data["error"], "error_description": error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        if "access_token" in response_data:
            return Response(response_data, status=status.HTTP_200_OK)

        logger.error(f"Unexpected response. Status: {response.status_code}, Response: {response.text}")
        return Response(
            {"error": "Unexpected response from Naver API"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )