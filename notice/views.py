from typing import cast

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from helpers.models import Category
from helpers.pagination import CustomPageNumberPagination
from helpers.utils import delete_from_ncp, upload_to_ncp
from user.models import User

from .models import Notice
from .serializers import CategorySerializer, NoticeSerializer


class CategoryViewSet(viewsets.ModelViewSet):  # type: ignore
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


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
        paginator = CustomPageNumberPagination()  # 커스텀 페이지네이터 사용
        paginated_notices = paginator.paginate_queryset(notices, request)  # 페이지네이션 적용
        serializer = NoticeSerializer(paginated_notices, many=True)
        return paginator.get_paginated_response(serializer.data)  # 커스텀 응답 반환

    elif request.method == "POST":
        data = request.data.copy()
        file = request.FILES.get("image")  # 프론트에서 "image" 필드로 파일을 전송해야 함
        cate = "review"
        if file and isinstance(file, InMemoryUploadedFile):
            img_url = upload_to_ncp(cate, file)  # 네이버 클라우드에 업로드 후 URL 반환
            data["img_url"] = img_url

        serializer = NoticeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=cast(User, request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="카테고리 목록 조회",
    operation_description="모든 카테고리 목록을 조회합니다.",
    responses={200: CategorySerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def category_list(request: Request) -> Response:
    """카테고리 목록 조회"""
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


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
        if cast(User, request.user) != notice.user:
            return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        # 공지에 이미지 URL이 있는 경우 NCP에서 삭제
        if notice.img_url:  # 이미지 URL 필드가 있다고 가정
            try:
                delete_from_ncp(notice.img_url)
            except Exception as e:
                return Response(
                    {"error": f"이미지 삭제 중 오류 발생: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        # 공지 삭제
        notice.delete()
        return Response({"message": "공지가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
