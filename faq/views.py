from typing import cast

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from faq.models import FAQ
from faq.serializers import FAQSerializer

from content.pagination import CustomPageNumberPagination
from user.models import User


@swagger_auto_schema(
    method="get",
    operation_summary="FAQ 목록 조회",
    operation_description="모든 FAQ를 조회합니다.",
    responses={200: FAQSerializer(many=True)},
)
@swagger_auto_schema(
    method="post",
    operation_summary="FAQ 생성",
    operation_description="새로운 FAQ를 생성합니다. 로그인 필요.",
    request_body=FAQSerializer,
    responses={201: FAQSerializer, 400: "잘못된 요청"},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def faq_list_or_create(request) -> Response:  # type: ignore
    """FAQ 목록 조회 및 생성"""
    if request.method == "GET":
        faqs = FAQ.objects.all().order_by("-created_at")
        paginator = CustomPageNumberPagination()  # 커스텀 페이지네이터 사용
        paginated_faqs = paginator.paginate_queryset(faqs, request)  # 페이지네이션 적용
        serializer = FAQSerializer(paginated_faqs, many=True)
        return paginator.get_paginated_response(serializer.data)  # 커스텀 응답 반환

    elif request.method == "POST":
        serializer = FAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=cast(User, request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="FAQ 상세 조회",
    operation_description="특정 FAQ의 상세 정보를 조회합니다.",
    responses={200: FAQSerializer, 404: "FAQ를 찾을 수 없음"},
)
@swagger_auto_schema(
    method="put",
    operation_summary="FAQ 수정",
    operation_description="특정 FAQ의 내용을 수정합니다. 작성자만 가능.",
    request_body=FAQSerializer,
    responses={200: FAQSerializer, 403: "권한 없음", 404: "FAQ를 찾을 수 없음"},
)
@swagger_auto_schema(
    method="delete",
    operation_summary="FAQ 삭제",
    operation_description="특정 FAQ를 삭제합니다. 작성자만 가능.",
    responses={204: "삭제됨", 403: "권한 없음", 404: "FAQ를 찾을 수 없음"},
)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def faq_detail_update_delete(request, faq_id) -> Response:  # type: ignore
    """FAQ 상세 조회, 수정, 삭제"""
    faq = get_object_or_404(FAQ, id=faq_id)

    if request.method == "GET":
        serializer = FAQSerializer(faq)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        if cast(User, request.user) != faq.user:
            return Response({"error": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer = FAQSerializer(faq, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        if cast(User, request.user) != faq.user:
            return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        faq.delete()
        return Response({"message": "FAQ가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
