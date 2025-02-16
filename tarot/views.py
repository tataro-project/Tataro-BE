import re
from typing import Any

from django.core.cache import cache
from django.db.models import Prefetch
from drf_yasg import openapi
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from tarot.constants import tarot_cards
from tarot.models import TaroCardContents, TaroChatContents, TaroChatRooms
from tarot.serializers import (
    TaroChatAllRoomResponseSerializer,
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
    def init_create(self, request: Request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        chat_content = None
        serializer = None

        # room_id가 없으면 tarochatroom 객체 생성
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

    @swagger_auto_schema(
        operation_summary="(두번째 질문부터) 타로 AI 카드 뽑기 멘트 응답",
        operation_description="사용자 질문에 대하여 타로 AI가 카드 뽑기 멘트를 응답합니다.",
    )
    def after_create(self, request: Request, room_id: int, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        chat_content = None
        serializer = None

        # room_id가 있으면 tarochatroom 객체 생성 안해도됨
        serializer = self.get_serializer(data=request.data, context={"room_id": room_id})
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
        contents_list = chat_room.contents_list
        chat_log_list = []
        card_list = TaroCardContents.objects.filter(room_id=chat_room.id).order_by("created_at")
        # question,answer 쌍으로 데이터가 필요함으로 idx 2씩 증가
        for idx in range(0, len(contents_list) - 1, 2):
            question = contents_list[idx].content
            answer = contents_list[idx + 1].content
            # 제일 마지막 q&a 쌍이면 타로 ai 응답 생성
            if idx == len(contents_list) - 2:
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
                TaroCardContents(
                    room=chat_room, card_name=card_name, card_content=prompt, card_direction=card_direction
                ).save()

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
                    chat_log_list.append(chat_log.data)
            else:
                # 이미 생성된 타로 응답 데이터가 있을때
                card = card_list[idx // 2]
                chat_log = TaroChatLogSerializer(
                    data={
                        "question": question,
                        "content": answer,
                        "card_name": card.card_name,
                        "card_url": tarot_cards[card.card_name],
                        "card_content": card.card_content,
                        "card_direction": card.card_direction,
                    }
                )
                if chat_log.is_valid(raise_exception=True):
                    chat_log_list.append(chat_log.data)

        serializer = self.get_serializer(data={"room_id": chat_room.id, "chat_log": chat_log_list})
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class TarotLogViewSet(viewsets.GenericViewSet):  # type: ignore
    # 필요한 참조 테이블 미리 가져오기
    queryset = TaroChatRooms.objects.prefetch_related(
        Prefetch("tarochatcontents_set", to_attr="contents_list")
    ).all()  # path parameter default pk임
    serializer_class = TaroChatRoomResponseSerializer

    @swagger_auto_schema(  # type:ignore
        operation_summary="가장 최신 채팅 로그",
        operation_description="제일 최근에 했던 채팅을 불러옵니다.",
        request_body=no_body,
        responses={200: TaroChatRoomResponseSerializer},
    )
    def get_newest_log(self, request: Request, *args: list[Any], **kwargs: dict[str, Any]) -> Response | None:
        chat_room = self.get_queryset().order_by("-created_at").first()
        if not chat_room:
            raise ValidationError("채팅방을 찾을 수 없습니다")
        contents_list = chat_room.contents_list
        chat_log_list = []
        card_list = TaroCardContents.objects.filter(room_id=chat_room.id).order_by("created_at")
        # question,answer 쌍으로 데이터가 필요함으로 idx 2씩 증가
        for idx in range(0, len(contents_list) - 1, 2):
            question = contents_list[idx].content
            answer = contents_list[idx + 1].content
            # 나중에 함수화 시키기
            card = card_list[idx // 2]
            chat_log = TaroChatLogSerializer(
                data={
                    "question": question,
                    "content": answer,
                    "card_name": card.card_name,
                    "card_url": tarot_cards[card.card_name],
                    "card_content": card.card_content,
                    "card_direction": card.card_direction,
                }
            )
            if chat_log.is_valid(raise_exception=True):
                chat_log_list.append(chat_log.data)

        serializer = self.get_serializer(data={"room_id": chat_room.id, "chat_log": chat_log_list})
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(  # type:ignore
        operation_summary="바로 전 채팅 로그",
        operation_description="주어진 room_id로 부터 바로 전에 했던 채팅을 불러옵니다.",
        request_body=no_body,
        responses={200: TaroChatRoomResponseSerializer},
    )
    def get_before_log(self, request: Request, *args: list[Any], **kwargs: dict[str, Any]) -> Response | None:
        current_chat_room = self.get_object()
        # created_at으로 비교하여 바로 전 채팅 로그 찾기
        chat_room = (
            self.get_queryset().filter(created_at__lt=current_chat_room.created_at).order_by("-created_at").first()
        )
        if not chat_room:
            raise ValidationError("채팅방을 찾을 수 없습니다")
        contents_list = chat_room.contents_list
        chat_log_list = []
        card_list = TaroCardContents.objects.filter(room_id=chat_room.id).order_by("created_at")
        # question,answer 쌍으로 데이터가 필요함으로 idx 2씩 증가
        for idx in range(0, len(contents_list) - 1, 2):
            question = contents_list[idx].content
            answer = contents_list[idx + 1].content
            # 나중에 함수화 시키기
            card = card_list[idx // 2]
            chat_log = TaroChatLogSerializer(
                data={
                    "question": question,
                    "content": answer,
                    "card_name": card.card_name,
                    "card_url": tarot_cards[card.card_name],
                    "card_content": card.card_content,
                    "card_direction": card.card_direction,
                }
            )
            if chat_log.is_valid(raise_exception=True):
                chat_log_list.append(chat_log.data)

        serializer = self.get_serializer(data={"room_id": chat_room.id, "chat_log": chat_log_list})
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(  # type:ignore
        operation_summary="모든 채팅 로그 페이지네이션",
        operation_description="모든 채팅 로그를 페이지네이션을 통해 해당 페이지의 로그 내역을 응답합니다.",
        manual_parameters=[
            openapi.Parameter(
                "page", openapi.IN_QUERY, description="페이지 번호", type=openapi.TYPE_INTEGER, required=True
            ),
            openapi.Parameter(
                "size", openapi.IN_QUERY, description="페이지 당 게시글 개수", type=openapi.TYPE_INTEGER, required=True
            ),
        ],
        request_body=no_body,
        responses={200: TaroChatAllRoomResponseSerializer},
    )
    # PageNumberPagination의 기능을 거의 안쓸거같아서 사용하지않고 직접 페이지네이션
    def get_all_log(self, request: Request, *args: list[Any], **kwargs: dict[str, Any]) -> Response | None:
        page = int(self.request.query_params.get("page", 1))
        size = int(self.request.query_params.get("size", 2))
        queryset = self.get_queryset()
        # 캐시 키 생성
        cache_key = f"taro_chat_rooms_count_{request.user.id}"
        # 캐시된 count 확인
        total_count = cache.get(cache_key)
        if total_count is None:
            total_count = queryset.count()
            # count 결과를 캐시에 5분간 저장
            cache.set(cache_key, total_count, 300)

        start = (page - 1) * size
        paginated_queryset = queryset[start : start + size]
        chat_contents = []

        for chat_room in paginated_queryset:
            contents_list = chat_room.contents_list
            chat_log_list = []
            card_list = TaroCardContents.objects.filter(room_id=chat_room.id).order_by("created_at")
            # question,answer 쌍으로 데이터가 필요함으로 idx 2씩 증가
            for idx in range(0, len(contents_list) - 1, 2):
                question = contents_list[idx].content
                answer = contents_list[idx + 1].content
                # 나중에 함수화 시키기
                card = card_list[idx // 2]
                chat_log = TaroChatLogSerializer(
                    data={
                        "question": question,
                        "content": answer,
                        "card_name": card.card_name,
                        "card_url": tarot_cards[card.card_name],
                        "card_content": card.card_content,
                        "card_direction": card.card_direction,
                    }
                )
                if chat_log.is_valid(raise_exception=True):
                    chat_log_list.append(chat_log.data)

            serializer = self.get_serializer(data={"room_id": chat_room.id, "chat_log": chat_log_list})
            if serializer.is_valid(raise_exception=True):
                # 또 result_list에 append해줘야함 response말고
                chat_contents.append(serializer.data)
        # total_pages 반올림 구현
        all_room_serializer = TaroChatAllRoomResponseSerializer(
            data={
                "page": page,
                "size": size,
                "total_count": total_count,
                "total_pages": (total_count + size - 1) // size,
                "chat_contents": chat_contents,
            }
        )
        if all_room_serializer.is_valid(raise_exception=True):
            return Response(all_room_serializer.data, status=status.HTTP_200_OK)


# 로그 생성시에 캐쉬 재생성 (유저별로 캐쉬 다르게 해야함)
