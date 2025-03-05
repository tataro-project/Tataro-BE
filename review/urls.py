from django.urls import path

from review.views import review_detail_update_delete, review_list_or_create

urlpatterns = [
    path("", review_list_or_create, name="review-list-create"),
    path("<int:review_id>/", review_detail_update_delete, name="review-detail-update-delete"),
]
