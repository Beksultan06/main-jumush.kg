from django.contrib import admin
from apps.users.models import User, UserRegion

admin.site.register(UserRegion)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", 'first_name','last_name', 'email', 'phone', 'role']
    list_filter = ["username", 'first_name', 'last_name','email', 'phone']
    search_fields = ["username", 'first_name', 'last_name','email', 'phone']