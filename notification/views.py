import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from user.models import User

from .models import Notification, NotiUser
from .serializers import NotificationSerializer


@swagger_auto_schema(
    method="post",
    operation_summary="알림 생성 및 전송",
    operation_description="새로운 알림을 생성하고 실시간으로 웹소켓을 통해 사용자에게 전송합니다.",
    request_body=NotificationSerializer,
    responses={201: NotificationSerializer, 400: "잘못된 요청"},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_notification(request: Request) -> Response:
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():  # 트랜잭션 시작
            notification = serializer.save(user=request.user)

            # NotiUser 생성
            NotiUser.objects.create(notification=notification)

        # 웹소켓을 통해 사용자에게 알림 전송
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{request.user.id}_notifications",
            {
                "type": "new_notification",
                "notification": json.dumps(
                    {
                        "id": notification.id,
                        "title": notification.title,
                        "url": notification.content,
                        "category": notification.category if notification.category else None,
                        "created_at": notification.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                    ensure_ascii=False,
                ),
            },
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request):  # type: ignore
    notification_id = request.data.get("notification_id")
    if not notification_id:
        return Response({"error": "notification_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        notiuser = NotiUser.objects.get(notification_id=notification_id)
        if request.user.id not in notiuser.read_users:
            notiuser.read_users.append(request.user.id)
            notiuser.save()
            return Response({"status": "marked_as_read", "notification_id": notification_id}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "already_read", "notification_id": notification_id}, status=status.HTTP_200_OK)
    except NotiUser.DoesNotExist:
        return Response({"error": "NotiUser not found"}, status=status.HTTP_404_NOT_FOUND)
