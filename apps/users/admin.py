from django.contrib import admin
from apps.users.models import User, UserRegion, UserSubRegion


@admin.register(UserRegion)
class UserRegionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    search_fields = ['title']


@admin.register(UserSubRegion)
class UserSubRegionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'region']
    list_filter = ['region']
    search_fields = ['title', 'region__title']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username", "first_name", "last_name", "email", "phone", "role",
        "get_region", "get_subregion", "is_active", "is_verified"
    ]
    list_filter = [
        "role", "is_active", "is_verified", "subregion__region", "subregion"
    ]
    search_fields = [
        "username", "first_name", "last_name", "email", "phone",
        "subregion__title", "subregion__region__title"
    ]

    def get_region(self, obj):
        if obj.subregion and obj.subregion.region:
            return obj.subregion.region.title
        return "-"
    get_region.short_description = "Регион"

    def get_subregion(self, obj):
        return obj.subregion.title if obj.subregion else "-"
    get_subregion.short_description = "Подрегион (район)"
