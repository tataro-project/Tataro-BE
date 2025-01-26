from typing import Optional

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Questionnaire
from .serializers import QuestionnaireSerializer


# 문진표 생성 및 수정을 처리하는 API View
class QuestionnaireView(APIView):
    # 문진표 생성을 처리하는 POST 메서드
    def post(self, request: Request) -> Response:
        # 요청 데이터로 시리얼라이저 인스턴스 생성
        serializer = QuestionnaireSerializer(data=request.data)

        # 데이터 유효성 검사
        if serializer.is_valid():
            # 유효한 데이터를 DB에 저장
            serializer.save()
            # 성공 응답 반환
            return Response({"message": "문진표 작성 완료되었습니다.", "status": "success"}, status=status.HTTP_200_OK)

        # 유효성 검사 실패시 에러 응답
        return Response({"message": "잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 문진표 수정을 처리하는 PUT 메서드
    def put(self, request: Request) -> Response:
        try:
            # 현재 로그인한 사용자 확인
            user_id: Optional[int] = request.user.id if request.user.is_authenticated else None

            # 인증되지 않은 사용자 처리
            if user_id is None:
                return Response({"message": "인증되지 않은 사용자입니다."}, status=status.HTTP_401_UNAUTHORIZED)

            # 현재 사용자의 문진표 조회
            questionnaire = Questionnaire.objects.get(user_id=str(user_id))

            # 부분 업데이트를 위해 partial=True 설정
            serializer = QuestionnaireSerializer(questionnaire, data=request.data, partial=True)

            # 데이터 유효성 검사
            if serializer.is_valid():
                # 유효한 데이터를 DB에 저장
                serializer.save()
                # 성공 응답 반환
                return Response({"message": "문진표가 수정되었습니다.", "status": "success"}, status=status.HTTP_200_OK)

            # 유효성 검사 실패시 에러 응답
            return Response({"message": "잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 문진표를 찾을 수 없는 경우 처리
        except Questionnaire.DoesNotExist:
            return Response({"message": "문진표를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
