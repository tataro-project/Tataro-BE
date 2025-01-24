from typing import Any
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        try:
            user = User.objects.get(id=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "message": "User Unauthorized"
            }, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request: Request) -> Response:
        try:
            user = User.objects.get(id=request.user.id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "회원 정보 수정 성공",
                    "status": "success"
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "올바르지 못한 시도입니다"
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                "message": "User Unauthorized"
            }, status=status.HTTP_401_UNAUTHORIZED)
