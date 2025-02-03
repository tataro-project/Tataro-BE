from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from content.models import Notice
from content.serializers import NoticeSerializer

User = get_user_model()


@swagger_auto_schema(
    method="get",
    operation_summary="공지 목록 조회",
    operation_description="모든 공지 목록을 최신순으로 조회합니다.",
    responses={200: NoticeSerializer(many=True)},
)
@swagger_auto_schema(
    method="post",
    operation_summary="공지 생성",
    operation_description="새로운 공지를 생성합니다. 로그인 필요.",
    request_body=NoticeSerializer,
    responses={201: NoticeSerializer, 400: "잘못된 요청"},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def notice_list_or_create(request: Request) -> Response:  # type: ignore
    """공지사항 목록 조회 (GET) 및 공지사항 생성 (POST)"""
    if request.method == "GET":  # 공지사항 목록 조회
        notices = Notice.objects.all().order_by("-order", "-created_at")  # order 순 정렬, 최신순
        serializer = NoticeSerializer(notices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":  # 공지사항 생성
        serializer = NoticeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # 작성자 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="공지 상세 조회",
    operation_description="특정 공지의 상세 정보를 조회합니다.",
    responses={200: NoticeSerializer, 404: "공지를 찾을 수 없음"},
)
@swagger_auto_schema(
    method="put",
    operation_summary="공지 수정",
    operation_description="특정 공지의 내용을 수정합니다. 작성자만 가능.",
    request_body=NoticeSerializer,
    responses={200: NoticeSerializer, 403: "권한 없음", 404: "공지를 찾을 수 없음"},
)
@swagger_auto_schema(
    method="delete",
    operation_summary="공지 삭제",
    operation_description="특정 공지를 삭제합니다. 작성자만 가능.",
    responses={204: "삭제됨", 403: "권한 없음", 404: "공지를 찾을 수 없음"},
)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def notice_detail_update_delete(request: Request, notice_id: int) -> Response:  # type: ignore
    """공지사항 조회 (GET), 수정 (PUT), 삭제 (DELETE)"""
    notice = get_object_or_404(Notice, id=notice_id)

    if request.method == "GET":
        serializer = NoticeSerializer(notice)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "PUT":
        if not isinstance(request.user, User) or not isinstance(notice.user, User) or request.user.id != notice.user.id:
            return Response({"error": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer = NoticeSerializer(notice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        if not isinstance(request.user, User) or not isinstance(notice.user, User) or request.user.id != notice.user.id:
            return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        notice.delete()
        return Response({"message": "공지사항이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
