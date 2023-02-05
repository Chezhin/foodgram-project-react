from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('email',)
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email')
    ordering = ('email',)
    empty_value_display = '-пусто-'
