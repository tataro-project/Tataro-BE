from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지 크기
    page_size_query_param = "size"  # 쿼리 파라미터로 페이지 크기 조절 가능 (예: ?size=20)
    max_page_size = 100  # 최대 페이지 크기 제한

    def get_paginated_response(self, data) -> Response:  # type: ignore
        return Response(
            {
                "page": self.page.number,  # type: ignore # 현재 페이지 번호
                "size": self.page.paginator.per_page,  # type: ignore # 페이지당 아이템 개수
                "total_pages": self.page.paginator.num_pages,  # type: ignore # 전체 페이지 수
                "total_count": self.page.paginator.count,  # type: ignore # 전체 아이템 개수
                "results": data,  # 실제 데이터 리스트
            }
        )
