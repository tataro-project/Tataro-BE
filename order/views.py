from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from order.models import Order
from order.serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related("user", "product")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 현재 로그인한 사용자의 주문 목록만 조회
        return self.queryset.filter(user=self.request.user)

    @swagger_auto_schema(request_body=OrderSerializer)
    def perform_create(self, serializer):
        # 주문 생성 시 현재 로그인한 사용자 정보 추가
        serializer.save(user=self.request.user)

    @swagger_auto_schema(responses={204: "No Content", 400: "Bad Request"})
    def destroy(self, request, *args, **kwargs):
        # 주문 삭제 (주문 상태가 결제 완료가 아닌 경우만 가능)
        order = self.get_object()
        if order.status == Order.StatusChoices.PAID:
            return Response({"error": "결제 완료된 주문은 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(method='post', responses={200: "Order canceled", 400: "Bad Request"})
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        # 주문 취소 기능 (결제 완료된 주문만 취소 가능)
        order = self.get_object()
        if order.status != Order.StatusChoices.PAID:
            return Response({"error": "결제 완료된 주문만 취소할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = Order.StatusChoices.CANCELED
        order.save()
        return Response({"message": "주문이 취소되었습니다."}, status=status.HTTP_200_OK)
