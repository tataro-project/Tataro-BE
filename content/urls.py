from django.urls import path

from content.routes.review_router import (
    create_review,
    delete_review,
    review_detail,
    review_list,
    update_review,
)

urlpatterns = [
    path("reviews/", review_list, name="review-list"),
    path("reviews/", create_review, name="create-review"),
    path("reviews/<int:review_id>/", review_detail, name="review-detail"),
    path("reviews/<int:review_id>/", update_review, name="update-review"),
    path("reviews/<int:review_id>/", delete_review, name="delete-review"),
]
