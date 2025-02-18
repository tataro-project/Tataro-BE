from drf_yasg.utils import swagger_auto_schema
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

    @swagger_auto_schema(
        operation_summary="유저 정보를 응답합니다.",
        operation_description='"id", "nickname", "email", "gender", "birthday", "social_type" 를 응답합니다',
        responses={201: UserUpdateSerializer, 400: "잘못된 요청"},
    )
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
            return Response({"message": "User Unauthorized(정보 조회)"}, status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_summary="유저 정보 수정",
        operation_description='유저의 "nickname", "gender", "birthday"를 수정합니다.',
        request_body=UserUpdateSerializer,
        responses={201: UserUpdateSerializer, 400: "잘못된 요청"},
    )
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
            return Response({"message": "User Unauthorized(회원 정보 수정)"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request: Request) -> Response:
        try:
            # 현재 로그인한 사용자 정보 조회
            user = User.objects.get(id=request.user.id)

            # 사용자와 관련된 모든 데이터 삭제
            # 주의: 이 부분은 모델 관계에 따라 조정이 필요할 수 있습니다
            user.delete()

            # 성공 응답 반환
            return Response(
                {"message": "회원 탈퇴 성공. 모든 사용자 데이터가 삭제되었습니다.", "status": "success"},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            # 사용자를 찾을 수 없는 경우 처리
            return Response({"message": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # 기타 예외 처리
            return Response(
                {"message": f"회원 탈퇴 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
