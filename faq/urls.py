from django.urls import path

from faq.views import faq_detail_update_delete, faq_list_or_create

urlpatterns = [
    path("", faq_list_or_create, name="review-list-create"),
    path("<int:faq_id>/", faq_detail_update_delete, name="review-detail-update-delete"),
]
