import logging

import requests
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


class KakaoLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="카카오 로그인 URL 반환", responses={200: "로그인 URL 반환 성공"})
    def get(self, request: Request) -> Response:
        kakao_login_url = (
            f"https://kauth.kakao.com/oauth/authorize?"
            f"client_id={env("KAKAO_REST_API_KEY")}&"
            f"client_secret={env('KAKAO_CLIENT_SECRET')}&"
            f"redirect_uri={env("KAKAO_REDIRECT_URI")}&"
            f"response_type=code"
        )
        return Response({"auth_url": kakao_login_url}, status=status.HTTP_200_OK)


class KakaoCallbackView(APIView):
    permission_classes = [AllowAny]

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
            "client_id": env("KAKAO_REST_API_KEY"),
            "client_secret": env("KAKAO_CLIENT_SECRET"),
            "redirect_uri": env("KAKAO_REDIRECT_URI"),
            "code": code,
        }

        token_response = requests.post(token_url, headers=headers, data=data)
        if token_response.status_code != 200:
            return Response(
                {"error": "Failed to get access token", "details": token_response.text},
                status=token_response.status_code,
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")


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

        # 사용자 정보 추출
        kakao_account = user_info.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        email = kakao_account.get("email")
        # nickname = profile.get("nickname")
        # gender = kakao_account.get("gender")  # male 또는 female
        # birth = kakao_account.get("birth")  # MM-DD 형식 (예: 01-01)

        # 먼저 사용자를 조회합니다.
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            # 기존 사용자의 경우, 카카오 정보로 업데이트하지 않음
            user = existing_user
            created = False
        else:
            # 새로운 사용자 생성
            user = User.objects.create(
                email=email,
                nickname=profile.get("nickname", ""),
                gender=kakao_account.get("gender", ""),
                birth=kakao_account.get("birth", None),
                social_type="KAKAO",
                is_active=True,
            )
            created = True

        refresh = RefreshToken.for_user(user)

        # 응답 반환
        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "kakao_refresh_token": refresh_token,  # 카카오 리프레시 토큰
                "message": "User information retrieved successfully",
                "user_id": user.id,
                "created": created,
                "user_data": {
                    "nickname": user.nickname,
                    "email": user.email,
                    "gender": user.gender,
                    "birthday": user.birth,
                },
            },
            status=status.HTTP_200_OK,
        )


logger = logging.getLogger(__name__)


class KakaoReissueView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="카카오 토큰 재발급",
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

        # 카카오 토큰 갱신 API 엔드포인트
        url = "https://kauth.kakao.com/oauth/token"
        # 요청 데이터 설정
        data = {
            "grant_type": "refresh_token",
            "client_id": env("KAKAO_REST_API_KEY"),
            "refresh_token": refresh_token,
            "client_secret": env("KAKAO_CLIENT_SECRET")
        }

        # 헤더 설정
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # 카카오 API에 POST 요청 보내기
        response = requests.post(url, data=data, headers=headers)

        # 응답 처리
        if response.status_code == 200:
            new_tokens = response.json()
            return Response(new_tokens, status=status.HTTP_200_OK)
        elif response.status_code == 400 and "invalid_grant" in response.text:
            # 리프레시 토큰이 만료된 경우
            return Response(
                {"error": "Refresh token expired", "message": "Please log in again"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        else:
            logger.error(f"Failed to refresh token. Status: {response.status_code}, Response: {response.text}")
            return Response(
                {"error": "Failed to refresh token", "details": response.text},
                status=response.status_code,
            )
