from typing import Any

from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from tarot.models import TaroCardContents, TaroChatContents
from tarot.serializers import TaroChatContentsInitSerializer


# Create your views here.
class TarotInitViewSet(viewsets.GenericViewSet["TaroChatContents"]):

    serializer_class = TaroChatContentsInitSerializer

    def create(self, request: Request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        content = request.data.get("content")
        if isinstance(content, str):
            prompt = TaroChatContents.init_tarot_prompt(content)
            init_serializer = self.get_serializer(data={"content": prompt})
            if init_serializer.is_valid(raise_exception=True):
                init_serializer.save()
            return Response(init_serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError({"content": content})


class TarotGenerateViewSet(viewsets.GenericViewSet):  # type: ignore

    serializer_class = TaroChatContentsInitSerializer

    def create(self, request: Request, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        serializer = self.get_serializer(data=request.data)
        # 쿼리에서 id를 뽑아서 먼저 객체를 불러온뒤 질문을 얻어냄
        # 클로바에 전송후 답변을 가져와서 시리얼라이저에담고 저장 후
        # serializer.data response 해줌
