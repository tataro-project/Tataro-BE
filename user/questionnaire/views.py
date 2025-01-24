from typing import Any, Optional
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from ..models import User, Questionnaire
from .serializers import QuestionnaireSerializer


class QuestionnaireView(APIView):
    def post(self, request: Request) -> Response:
        serializer = QuestionnaireSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "문진표 작성 완료되었습니다.",
                "status": "success"
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "잘못된 요청입니다."
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request) -> Response:
        try:
            user_id: Optional[int] = request.user.id if request.user.is_authenticated else None
            if user_id is None:
                return Response({
                    "message": "인증되지 않은 사용자입니다."
                }, status=status.HTTP_401_UNAUTHORIZED)

            questionnaire = Questionnaire.objects.get(user_id=str(user_id))
            serializer = QuestionnaireSerializer(questionnaire, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "문진표가 수정되었습니다.",
                    "status": "success"
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "잘못된 요청입니다."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Questionnaire.DoesNotExist:
            return Response({
                "message": "문진표를 찾을 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)
