from django.contrib import admin
from .models import (
    CustomUser,
    VeterinarioInfo,
    ClientePerfil,
    Pet,
    Consulta,
    Prontuario,
    HorarioDisponivel,
    ValorPagamento,
    PagamentoCliente,
    GerenciamentoPagamento,
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
        "status_pagamento",
    )  # NOVO CAMPO
    list_filter = ("status", "status_pagamento", "horario_agendado__data")
    ordering = ("horario_agendado__data",)
    search_fields = ("pet__nome", "veterinario__nome", "veterinario__sobrenome")

    @admin.display(description="Data e Hora")
    def get_data_hora(self, obj):
        return obj.horario_agendado.data.strftime("%d/%m/%Y às %H:%M")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "horario_agendado":
            queryset_base = HorarioDisponivel.objects.filter(
                disponivel=True, data__gte=timezone.now()
            )
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


class ValorPagamentoAdmin(admin.ModelAdmin):
    list_display = ("consulta", "valor", "data_definicao")
    list_filter = ("data_definicao",)
    search_fields = ("consulta__cliente",)
    ordering = ("-data_definicao",)


class PagamentoClienteAdmin(admin.ModelAdmin):
    list_display = ("consulta", "comprovante", "data_envio")
    list_filter = ("data_envio",)
    search_fields = ("consulta__cliente",)
    ordering = ("-data_envio",)


class GerenciamentoPagamentoAdmin(admin.ModelAdmin):
    list_display = (
        "consulta_link",
        "comprovante_link",
        "atendente",
        "status",
        "data_atualizacao",
    )
    list_filter = ("status", "atendente")
    search_fields = ("consulta__pet__nome", "atendente__email", "observacao")
    ordering = ("-data_atualizacao",)
    readonly_fields = ("consulta_link", "comprovante_link", "data_atualizacao")
    fields = ("consulta_link", "comprovante_link", "atendente", "status", "observacao")
    autocomplete_fields = ("atendente",)

    @admin.display(description="Consulta")
    def consulta_link(self, obj):
        return f"Consulta {obj.consulta.id} - Pet: {obj.consulta.pet.nome} ({obj.consulta.get_status_pagamento_display()})"

    @admin.display(description="Comprovante")
    def comprovante_link(self, obj):
        pagamentos = obj.consulta.pagamentos_cliente.all().order_by("-data_envio")
        if pagamentos.exists():
            ultimo_pagamento = pagamentos[0]
            if ultimo_pagamento.comprovante:
                return format_html(
                    '<a href="{}" target="_blank">Ver Comprovante</a>',
                    ultimo_pagamento.comprovante.url,
                )
        return "Sem comprovante"

    def has_add_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "atendente":
            kwargs["queryset"] = CustomUser.objects.filter(user_type="atendente")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(VeterinarioInfo, VeterinarioInfoAdmin)
admin.site.register(ClientePerfil, ClientePerfilAdmin)
admin.site.register(Pet, PetAdmin)
admin.site.register(Consulta, ConsultaAdmin)
admin.site.register(Prontuario, ProntuarioAdmin)
admin.site.register(HorarioDisponivel, HorarioDisponivelAdmin)
admin.site.register(ValorPagamento, ValorPagamentoAdmin)
admin.site.register(PagamentoCliente, PagamentoClienteAdmin)
admin.site.register(GerenciamentoPagamento, GerenciamentoPagamentoAdmin)
