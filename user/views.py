from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserUpdateSerializer


# 사용자 정보 조회 및 수정을 처리하는 API View
class UserView(APIView):
    # 인증된 사용자만 접근 가능하도록 설정
    permission_classes = [IsAuthenticated]

    # 사용자 정보 조회를 처리하는 GET 메서드
    def get(self, request: Request) -> Response:
        try:
            # 현재 로그인한 사용자 정보 조회
            user = User.objects.get(id=request.user.id)
            # 사용자 정보를 JSON으로 직렬화
            serializer = UserUpdateSerializer(user)
            # 직렬화된 데이터 반환
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 사용자를 찾을 수 없는 경우 처리
        except User.DoesNotExist:
            return Response({"message": "User Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    # 사용자 정보 수정을 처리하는 PUT 메서드
    def put(self, request: Request) -> Response:
        try:
            # 현재 로그인한 사용자 정보 조회
            user = User.objects.get(id=request.user.id)
            # 부분 업데이트를 위해 partial=True 설정
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)

            # 데이터 유효성 검사
            if serializer.is_valid():
                # 유효한 데이터를 DB에 저장
                serializer.save()
                # 성공 응답 반환
                return Response({"message": "회원 정보 수정 성공", "status": "success"}, status=status.HTTP_200_OK)

            # 유효성 검사 실패시 에러 응답
            return Response({"message": "올바르지 못한 시도입니다"}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자를 찾을 수 없는 경우 처리
        except User.DoesNotExist:
            return Response({"message": "User Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
