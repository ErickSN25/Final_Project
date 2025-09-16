from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('email', 'nome', 'sobrenome', 'cpf', 'crmv', 'is_staff', 'is_active', 'type')
    list_filter = ('is_staff', 'is_active', 'type')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'sobrenome', 'cpf', 'crmv', 'type')}),
        ('Permissões', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'sobrenome', 'cpf', 'crmv', 'type', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    search_fields = ('email', 'nome', 'sobrenome', 'cpf')
    ordering = ('email',)
