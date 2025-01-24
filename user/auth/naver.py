from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

class NaverTokenReissueView(APIView):
    def post(self, request: Request) -> Response:
        try:
            return Response({
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token"
            }, status=200)
        except Exception:
            return Response({
                "message": "재발급 실패"
            }, status=401)
