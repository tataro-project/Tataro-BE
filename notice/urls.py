from django.urls import path

from notice.views import notice_detail_update_delete, notice_list_or_create

urlpatterns = [
    path("notices/", notice_list_or_create, name="notice-list-create"),
    path("notices/<int:notice_id>/", notice_detail_update_delete, name="notice-detail-update-delete"),
]
