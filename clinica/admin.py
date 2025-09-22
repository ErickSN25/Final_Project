from django.contrib import admin
from .models import CustomUser, VeterinarioInfo, ClientePerfil, Pet, Consulta, Prontuario, HorarioDisponivel


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'sobrenome', 'user_type', 'is_staff', 'get_crmv')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'nome', 'sobrenome', 'cpf')
    ordering = ('nome', 'sobrenome')

    def get_crmv(self, obj):
        if obj.user_type == 'veterinario':
            try:
                return obj.veterinarioinfo.crmv
            except VeterinarioInfo.DoesNotExist:
                return "CRMV não cadastrado"
        return "-"
    get_crmv.short_description = 'CRMV'

class VeterinarioInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'crmv')
    search_fields = ('user__nome', 'user__sobrenome', 'crmv')

class ClientePerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefone', 'endereco')
    search_fields = ('user__nome', 'user__sobrenome', 'telefone', 'endereco')
    
class PetAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie', 'tutor')
    list_filter = ('especie',)
    search_fields = ('nome', 'tutor__nome', 'tutor__sobrenome')
    
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('pet', 'veterinario', 'status')
    list_filter = ('status',)
    search_fields = ('pet__nome', 'veterinario__nome', 'veterinario__sobrenome')
    
class ProntuarioAdmin(admin.ModelAdmin):
    list_display = ('consulta', 'diagnostico', 'criada_em')
    search_fields = ('consulta__pet__nome', 'consulta__veterinario__nome', 'diagnostico')
    list_filter = ('criada_em',)

class HorarioDisponivelAdmin(admin.ModelAdmin):
    list_display = ('veterinario', 'data', 'disponivel')
    list_filter = ('disponivel',)
    search_fields = ('veterinario__nome', 'veterinario__sobrenome')
    ordering = ('data',)


# Registre os modelos no painel de administração
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(VeterinarioInfo, VeterinarioInfoAdmin)
admin.site.register(ClientePerfil, ClientePerfilAdmin)
admin.site.register(Pet, PetAdmin)
admin.site.register(Consulta, ConsultaAdmin)
admin.site.register(Prontuario, ProntuarioAdmin)
admin.site.register(HorarioDisponivel, HorarioDisponivelAdmin)
