from typing import cast

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from helpers.pagination import CustomPageNumberPagination
from helpers.utils import delete_from_ncp, upload_to_ncp
from user.models import User

from .models import Review
from .serializers import ReviewSerializer


@swagger_auto_schema(
    method="get",
    operation_summary="리뷰 목록 조회",
    operation_description="모든 리뷰 목록을 최신순으로 조회합니다.",
    responses={200: ReviewSerializer(many=True)},
)
@swagger_auto_schema(
    method="post",
    operation_summary="리뷰 생성",
    operation_description="새로운 리뷰를 생성합니다. 로그인 필요.",
    request_body=ReviewSerializer,
    responses={201: ReviewSerializer, 400: "잘못된 요청"},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def review_list_or_create(request: Request) -> Response:  # type: ignore
    if request.method == "GET":
        sort_by = request.query_params.get("sort_by", "views")  # 기본값은 views(인기순)

        if sort_by == "date":
            reviews = Review.objects.select_related("user").order_by("-created_at")
        else:
            reviews = Review.objects.select_related("user").order_by("-view_count")
        paginator = CustomPageNumberPagination()  # 커스텀 페이지네이터 사용
        paginated_reviews = paginator.paginate_queryset(reviews, request)  # 페이지네이션 적용
        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)  # 커스텀 응답 반환

    elif request.method == "POST":
        data = request.data.copy()
        file = request.FILES.get("image")  # 프론트에서 "image" 필드로 파일을 전송해야 함
        print(file)
        cate = "review"
        if file and isinstance(file, InMemoryUploadedFile):
            print(file)
            img_url = upload_to_ncp(cate, file)  # 네이버 클라우드에 업로드 후 URL 반환
            data["img_url"] = img_url
            print(img_url)
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=cast(User, request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="리뷰 상세 조회",
    operation_description="특정 리뷰의 상세 정보를 조회합니다.",
    responses={200: ReviewSerializer, 404: "리뷰를 찾을 수 없음"},
)
@swagger_auto_schema(
    method="put",
    operation_summary="리뷰 수정",
    operation_description="특정 리뷰의 내용을 수정합니다. 작성자만 가능.",
    request_body=ReviewSerializer,
    responses={200: ReviewSerializer, 403: "권한 없음", 404: "리뷰를 찾을 수 없음"},
)
@swagger_auto_schema(
    method="delete",
    operation_summary="리뷰 삭제",
    operation_description="특정 리뷰를 삭제합니다. 작성자만 가능.",
    responses={204: "삭제됨", 403: "권한 없음", 404: "리뷰를 찾을 수 없음"},
)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def review_detail_update_delete(request: Request, review_id: int) -> Response:  # type: ignore
    review = get_object_or_404(Review.objects.select_related("user"), id=review_id)

    if request.method == "GET":
        review.increase_view_count()
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "PUT":
        if cast(User, request.user) != review.user:
            return Response({"error": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 이미지 파일이 요청에 포함되어 있는지 확인
        new_image = request.FILES.get("image")

        if new_image:
            # 기존 이미지가 있는지 확인
            if review.img_url:
                try:
                    # 기존 이미지 삭제
                    delete_from_ncp(review.img_url)
                except Exception as e:
                    return Response(
                        {"error": f"기존 이미지 삭제 중 오류 발생: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            # 새 이미지 업로드
            try:
                cate = "review"
                new_img_url = upload_to_ncp(cate, new_image)
                request.data["img_url"] = new_img_url
            except Exception as e:
                return Response(
                    {"error": f"새 이미지 업로드 중 오류 발생: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":

        if cast(User, request.user) != review.user:
            return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 리뷰에 이미지 URL이 있는 경우 NCP에서 삭제
        if review.img_url:  # 이미지 URL 필드가 있다고 가정
            try:
                delete_from_ncp(review.img_url)
            except Exception as e:
                return Response(
                    {"error": f"이미지 삭제 중 오류 발생: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # 리뷰 삭제
        review.delete()
        return Response({"message": "리뷰가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
