from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.response import Response

from helpers.utils import upload_to_ncp, delete_from_ncp

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):  # type: ignore
    """
    Product 관리 API
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        operation_description="상품 목록 조회",
        responses={200: ProductSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs) -> Response:  # type: ignore
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="상품 생성",
        request_body=ProductSerializer,
        responses={201: ProductSerializer()},
    )
    def create(self, request, *args, **kwargs) -> Response:  # type: ignore
        """
        상품을 생성할 때 이미지 파일이 있으면 NCP Object Storage에 업로드 후 URL만 저장
        """
        data = request.data.copy()

        # 이미지 파일이 있다면 업로드 처리
        if "image" in request.FILES:
            uploaded_url = upload_to_ncp("product", request.FILES["image"])
            data["img_url"] = uploaded_url  # 업로드된 이미지 URL 저장

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="상품 상세 조회",
        responses={200: ProductSerializer()},
    )
    def retrieve(self, request, *args, **kwargs) -> Response:  # type: ignore
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="상품 정보 수정 (전체 업데이트)",
        request_body=ProductSerializer,
        responses={200: ProductSerializer()},
    )
    def update(self, request, *args, **kwargs) -> Response:  # type: ignore
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="상품 정보 수정 (부분 업데이트)",
        request_body=ProductSerializer,
        responses={200: ProductSerializer()},
    )
    def partial_update(self, request, *args, **kwargs) -> Response:  # type: ignore
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="상품 삭제",
        responses={204: "삭제 성공"},
    )
    def destroy(self, request, *args, **kwargs) -> Response:  # type: ignore
        """
        상품 삭제 시 관련 이미지도 NCP Object Storage에서 삭제
        """
        product = get_object_or_404(Product, pk=kwargs["pk"])

        # 이미지가 있으면 NCP에서 삭제
        if product.img_url:
            delete_from_ncp(product.img_url)

        # 상품 삭제
        self.perform_destroy(product)
        return Response({"message": "상품 및 이미지 삭제 완료"}, status=status.HTTP_204_NO_CONTENT)
