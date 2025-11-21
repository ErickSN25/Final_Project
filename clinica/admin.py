from django.contrib import admin
from .models import (
    CustomUser,
    VeterinarioInfo,
    ClientePerfil,
    Pet,
    Consulta,
    Prontuario,
    HorarioDisponivel,
)
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html


if CustomUser in admin.site._registry:
    admin.site.unregister(CustomUser)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ("email", "nome", "sobrenome", "user_type", "is_active", "is_staff")
    list_filter = ("user_type", "is_active", "is_staff")
    ordering = ("email",)
    search_fields = ("email", "nome", "sobrenome", "cpf")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informações Pessoais", {"fields": ("nome", "sobrenome", "cpf", "user_type")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas Importantes", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "nome",
                    "sobrenome",
                    "cpf",
                    "user_type",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


class VeterinarioInfoAdmin(admin.ModelAdmin):
    list_display = ("user", "crmv")
    search_fields = ("user__nome", "user__sobrenome", "crmv")


class ClientePerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "telefone", "endereco")
    search_fields = ("user__nome", "user__sobrenome", "telefone", "endereco")


class PetAdmin(admin.ModelAdmin):
    list_display = ("nome", "especie", "tutor")
    list_filter = ("especie",)
    search_fields = ("nome", "tutor__nome", "tutor__sobrenome")


class ConsultaAdmin(admin.ModelAdmin):
    list_display = (
        "pet",
        "veterinario",
        "get_data_hora",
        "status",
    )
    list_filter = ("status", "horario_agendado__data")
    ordering = ("horario_agendado__data",)
    search_fields = ("pet__nome", "veterinario__nome", "veterinario__sobrenome")

    @admin.display(description="Data e Hora")
    def get_data_hora(self, obj):
        return obj.horario_agendado.data.strftime("%d/%m/%Y às %H:%M")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "horario_agendado":
            queryset_base = HorarioDisponivel.objects.filter(disponivel=True, data__gte=timezone.now())
            kwargs["queryset"] = queryset_base

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProntuarioAdmin(admin.ModelAdmin):
    list_display = ("consulta", "diagnostico", "criada_em")
    search_fields = (
        "consulta__pet__nome",
        "consulta__veterinario__nome",
        "diagnostico",
    )
    list_filter = ("criada_em",)


class HorarioDisponivelAdmin(admin.ModelAdmin):
    list_display = ("veterinario", "data", "disponivel")
    list_filter = ("disponivel",)
    search_fields = ("veterinario__nome", "veterinario__sobrenome")
    ordering = ("data",)


admin.site.register(VeterinarioInfo, VeterinarioInfoAdmin)
admin.site.register(ClientePerfil, ClientePerfilAdmin)
admin.site.register(Pet, PetAdmin)
admin.site.register(Consulta, ConsultaAdmin)
admin.site.register(Prontuario, ProntuarioAdmin)
admin.site.register(HorarioDisponivel, HorarioDisponivelAdmin)
