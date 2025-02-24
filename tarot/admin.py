from django.contrib import admin

from .models import TaroCardContents, TaroChatContents, TaroChatRooms


class TaroChatRoomsAdmin(admin.ModelAdmin):  # type:ignore
    list_display = ("user", "created_at")


admin.site.register(TaroChatRooms, TaroChatRoomsAdmin)


class TaroChatContentsAdmin(admin.ModelAdmin):  # type:ignore
    list_display = ("room", "content", "created_at")
    readonly_fields = ("content", "created_at")


admin.site.register(TaroChatContents, TaroChatContentsAdmin)


class TaroCardContentsAdmin(admin.ModelAdmin):  # type:ignore
    list_display = ("room", "card_name", "card_direction", "created_at")
    readonly_fields = ("card_name", "card_direction", "card_content", "created_at")


admin.site.register(TaroCardContents, TaroCardContentsAdmin)
