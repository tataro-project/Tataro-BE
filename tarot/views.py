import re
from typing import Any

from django.db.models import Prefetch
from drf_yasg import openapi
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from tarot.constants import tarot_cards
from tarot.models import TaroCardContents, TaroChatContents, TaroChatRooms
from tarot.serializers import (
    TaroChatContentsInitSerializer,
    TaroChatLogSerializer,
    TaroChatRoomResponseSerializer,
)


# Create your views here.
class TarotInitViewSet(viewsets.GenericViewSet["TaroChatContents"]):

    serializer_class = TaroChatContentsInitSerializer

    # 정규식 패턴을 사용하여 하나의 URL 패턴을 사용하여 room_id가 있는경우와 없는경우를 나눠 응답할수있음
    @swagger_auto_schema(
        operation_summary="타로 AI 카드 뽑기 멘트 응답",
        operation_description="사용자 질문에 대하여 타로 AI가 카드 뽑기 멘트를 응답합니다.",
    )
    def init_create(self, request: Request, room_id: int, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        chat_content = None
        serializer = None

        # room_id가 있으면 tarochatroom 객체 생성 안해도됨
        if room_id:
            serializer = self.get_serializer(data=request.data, context={"room_id": room_id})
        else:
            serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            chat_content = serializer.save()
        content = request.data.get("content")
        if isinstance(content, str) and chat_content:
            prompt = TaroChatContents.init_tarot_prompt(content)
            print("prompt=", prompt)
            init_serializer = self.get_serializer(
                data={"content": prompt}, context={"room_id": chat_content.room_id, "chat_id": chat_content.id}
            )
            if init_serializer.is_valid(raise_exception=True):
                init_serializer.save()
            return Response(init_serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError({"content": content})


class TarotAfterInitViewSet(viewsets.GenericViewSet["TaroChatContents"]):

    serializer_class = TaroChatContentsInitSerializer

    # 정규식 패턴을 사용하여 하나의 URL 패턴을 사용하여 room_id가 있는경우와 없는경우를 나눠 응답할수있음
    @swagger_auto_schema(
        operation_summary="(두번째 질문부터) 타로 AI 카드 뽑기 멘트 응답",
        operation_description="사용자 질문에 대하여 타로 AI가 카드 뽑기 멘트를 응답합니다.",
    )
    def after_create(self, request: Request, room_id: int, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        chat_content = None
        serializer = None

        # room_id가 있으면 tarochatroom 객체 생성 안해도됨
        if room_id:
            serializer = self.get_serializer(data=request.data, context={"room_id": room_id})
        else:
            serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            chat_content = serializer.save()
        content = request.data.get("content")
        if isinstance(content, str) and chat_content:
            prompt = TaroChatContents.init_tarot_prompt(content)
            print("prompt=", prompt)
            init_serializer = self.get_serializer(
                data={"content": prompt}, context={"room_id": chat_content.room_id, "chat_id": chat_content.id}
            )
            if init_serializer.is_valid(raise_exception=True):
                init_serializer.save()
            return Response(init_serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError({"content": content})


class TarotGenerateViewSet(viewsets.GenericViewSet):  # type: ignore
    # 필요한 참조 테이블 미리 가져오기
    queryset = TaroChatRooms.objects.prefetch_related(
        Prefetch("tarochatcontents_set", to_attr="contents_list")
    ).all()  # path parameter default pk임
    serializer_class = TaroChatRoomResponseSerializer

    @swagger_auto_schema(  # type:ignore
        operation_summary="질문에 대한 타로 AI 답변 응답",
        operation_description="타로 AI가 사용자의 질문과 뽑은 카드에 대한 답변을 생성하여 응답합니다",
        request_body=no_body,
        responses={201: TaroChatRoomResponseSerializer},
    )
    def create(self, request: Request, *args: list[Any], **kwargs: dict[str, Any]) -> Response | None:
        chat_room = self.get_object()
        question = chat_room.contents_list[0].content
        answer = chat_room.contents_list[1].content

        # 쿼리에서 id를 뽑아서 먼저 객체를 불러온뒤 질문을 얻어냄
        prompt = TaroCardContents.generate_tarot_prompt(question)
        print("질문:", question)
        print("prompt=", prompt)

        # 카드 이름 파싱
        first = prompt.index("🔮")
        second = prompt.index("🔮", first + 1)
        eng_list = re.findall(r"[a-zA-Z]+", prompt[first:second])
        card_name = " ".join(eng_list)

        # 카드 방향 파싱
        card_direction = prompt[second - 3 : second]

        # TaroCardContents 저장
        TaroCardContents(room=chat_room, card_name=card_name, card_content=prompt, card_direction=card_direction).save()

        # 클로바에 전송후 답변을 가져와서 시리얼라이저에담고 저장 후
        card_url = tarot_cards[card_name]
        chat_log = TaroChatLogSerializer(
            data={
                "question": question,
                "content": answer,
                "card_name": card_name,
                "card_url": card_url,
                "card_content": prompt,
                "card_direction": card_direction,
            }
        )
        if chat_log.is_valid(raise_exception=True):
            serializer = self.get_serializer(data={"room_id": chat_room.id, "chat_log": [chat_log.data]})
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.data, status=status.HTTP_201_CREATED)
