from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')

    # صفحه‌ی ویرایش کاربر
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات اضافی', {'fields': ('phone',)}),
    )

    # صفحه‌ی ساخت کاربر جدید
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات اضافی', {'fields': ('email', 'phone')}),
    )
