from django.urls import path

from content.consumers import NotificationConsumer
from faq.views import faq_detail_update_delete, faq_list_or_create
from notice.views import notice_detail_update_delete, notice_list_or_create
from review.views import review_detail_update_delete, review_list_or_create

urlpatterns = [
    path("notices/", notice_list_or_create, name="notice-list-create"),
    path("notices/<int:notice_id>/", notice_detail_update_delete, name="notice-detail-update-delete"),
    path("reviews/", review_list_or_create, name="review-list-create"),
    path("reviews/<int:review_id>/", review_detail_update_delete, name="review-detail-update-delete"),
    path("faq/", faq_list_or_create, name="review-list-create"),
    path("faq/<int:faq_id>/", faq_detail_update_delete, name="review-detail-update-delete"),
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
