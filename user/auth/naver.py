import requests
from django.conf import settings
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
        return Response({"naver_login_url": naver_login_url}, status=status.HTTP_200_OK)


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

        # 사용자 정보 요청
        profile_url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = requests.get(profile_url, headers=headers)
        profile_data = profile_response.json()

        if profile_data.get("message") != "success":
            return Response({"error": "Failed to retrieve user profile"}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자 정보 반환
        user_info = profile_data["response"]
        email = user_info.get("email")
        nickname = user_info.get("nickname")
        gender_map = {"M": "male", "F": "female"}
        gender = gender_map.get(user_info.get("gender"), None)  # 변환 실패 시 None
        birth = user_info.get("birth")

        # 데이터베이스에 사용자 저장 또는 업데이트
        user, created = User.objects.update_or_create(
            email=email,
            defaults={
                "social_type": "NAVER",
                "nickname": nickname,
                "gender": gender,
                "birth": birth,
                "is_active": True,
            },
        )

        refresh = RefreshToken.for_user(user)

        # 응답 반환
        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
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
