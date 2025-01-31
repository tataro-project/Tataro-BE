from typing import Any, cast

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from content.models import Review
from content.serializers import ReviewSerializer
from user.models import User


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter("page", openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
    ],
    responses={200: ReviewSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def review_list(request: Request) -> Response:
    """리뷰 목록 조회 (페이징 지원)"""
    page: str = request.query_params.get("page", "1")
    reviews = Review.objects.all().order_by("-created_at")
    paginator = Paginator(reviews, 10)  # 페이지당 10개씩

    try:
        paginated_reviews = paginator.page(int(page))
    except (EmptyPage, PageNotAnInteger):
        return Response({"error": "페이지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewSerializer(paginated_reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method="get", responses={200: ReviewSerializer()})
@api_view(["GET"])
@permission_classes([AllowAny])
def review_detail(request: Request, review_id: int) -> Response:
    """특정 리뷰 조회"""
    review = get_object_or_404(Review, id=review_id)
    review.view_count += 1
    review.save()
    serializer = ReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method="post", request_body=ReviewSerializer, responses={201: ReviewSerializer()})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request: Request) -> Response:
    """리뷰 작성 (로그인 필요)"""
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=cast(User, request.user))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="patch", request_body=ReviewSerializer(partial=True), responses={200: ReviewSerializer()})
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_review(request: Request, review_id: int) -> Response:
    """리뷰 수정 (작성자만 가능)"""
    review = get_object_or_404(Review, id=review_id)

    if cast(User, request.user) != review.user:
        return Response({"error": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    serializer = ReviewSerializer(review, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="delete", responses={204: "No Content"})
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_review(request: Request, review_id: int) -> Response:
    """리뷰 삭제 (작성자만 가능)"""
    review = get_object_or_404(Review, id=review_id)

    if cast(User, request.user) != review.user:
        return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    review.delete()
    return Response({"message": "리뷰가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
