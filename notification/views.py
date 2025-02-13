from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from user.models import User

from .models import Notification
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
        notification = serializer.save(user=request.user)

        # 웹소켓을 통해 사용자에게 알림 전송
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{request.user.id}",
            {
                "type": "send_notification",
                "data": {
                    "title": notification.title,
                    "content": notification.content,
                    "created_at": notification.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                },
            },
        )
        print(f"📡 WebSocket 메시지 전송됨: {notification.title}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
