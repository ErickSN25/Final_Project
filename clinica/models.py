from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone


# --- Modelos usuarios ---

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O usuário precisa ter um e-mail válido")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário precisa ter is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('veterinario', 'Veterinário'),
        ('cliente', 'Cliente'),
        ('atendente', 'Atendente'),
        ('administrador', 'Administrador'),
    )
    
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=30)
    sobrenome = models.CharField(max_length=30)
    cpf = models.CharField(max_length=11, unique=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'sobrenome', 'cpf', 'user_type']

    def __str__(self):
        return f"{self.nome} ({self.user_type})"

    def get_full_name(self):
        return f"{self.nome} {self.sobrenome}"

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

class VeterinarioInfo(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'veterinario'})
    crmv = models.CharField(max_length=10, unique=True, verbose_name="CRMV")
    foto_veterinario = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    def __str__(self):
        return f"CRMV: {self.crmv} - {self.user.get_full_name()}"

    class Meta:
        verbose_name = "Informação do Veterinário"
        verbose_name_plural = "Informações dos Veterinários"

class ClientePerfil(models.Model):
    UF_CHOICES = [
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]

    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, limit_choices_to={'user_type': 'cliente'})
    foto_user = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, choices=UF_CHOICES, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"

    class Meta:
        verbose_name = "Perfil do Cliente"
        verbose_name_plural = "Perfis dos Clientes"

# --- Modelos cliente ---

class Pet(models.Model):
    especieChoices = [
        ('CACHORRO', 'Cachorro'),
        ('GATO', 'Gato'),
        ('COELHO', 'Coelho'),
        ('PAPAGAIO', 'Papagaio'),
        ('HAMSTER', 'Hamster'),
        ('CALOPSITA', 'Calopsita'),
        ('FURAO', 'Furão'),
        ('JABUTI', 'Jabuti'),
        ('PEIXE', 'Peixe'),
        ('PIRIQUITO', 'Periquito'),
    ]
    
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'cliente'})
    foto_pet = models.ImageField(upload_to='fotos_pet/', blank=True, null=True)
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=50, choices=especieChoices)
    raca = models.CharField(max_length=50, blank=True, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    vacinas_em_dia = models.BooleanField(default=False)
    alergias = models.TextField(blank=True, null=True)
    doencas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.especie}) - Tutor: {self.tutor.get_full_name()}"

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"

class Consulta(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'veterinario'},
        related_name="consultas_como_veterinario"
    )

    horario_agendado = models.OneToOneField(
        'HorarioDisponivel', 
        on_delete=models.PROTECT, 
        verbose_name="Horário Agendado",
        limit_choices_to={'disponivel': True} 
    )
    
    motivo = models.TextField(verbose_name="Motivo da Consulta")
    STATUS_CHOICES = [
        ('MARCADA', 'Marcada'),        
        ('CANCELADA', 'Cancelada'),    
        ('EM_ANDAMENTO', 'Em Andamento'), 
        ('REALIZADA', 'Realizada'),    
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='MARCADA',
        verbose_name="Status da Consulta"
    )
    
    STATUS_PAGAMENTO_CHOICES = [
        ('PENDENTE', 'Pendente de Pagamento'),              
        ('AGUARDANDO_VALOR', 'Aguardando Definição de Valor'), 
        ('AGUARDANDO_PAGAMENTO', 'Aguardando Pagamento do Cliente'), 
        ('EM_ANALISE', 'Comprovante em Análise'),          
        ('APROVADO', 'Pagamento Aprovado/Concluído'),      
        ('RECUSADO', 'Pagamento Recusado'),                 
    ]
    status_pagamento = models.CharField(
        max_length=25,
        choices=STATUS_PAGAMENTO_CHOICES,
        default='PENDENTE',
        verbose_name="Status do Pagamento"
    )

    def __str__(self):
        data_formatada = self.horario_agendado.data.strftime("%d/%m/%Y às %H:%M") 
        return f"Consulta {self.pet.nome} - {self.veterinario.get_full_name()} ({data_formatada})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        
        if self.veterinario != self.horario_agendado.veterinario:
            raise ValidationError(
                "O veterinário da consulta deve ser o mesmo cadastrado no Horário Disponível selecionado."
            )
        if is_new:
            self.horario_agendado.disponivel = False
            self.horario_agendado.save()
            
        elif self.status == 'CANCELADA' and not self.horario_agendado.disponivel:
            self.horario_agendado.disponivel = True
            self.horario_agendado.save()

        if self.pk:
            antiga = type(self).objects.filter(pk=self.pk).values('status', 'status_pagamento').first()
            status_antigo = antiga['status'] if antiga else None
            status_pagamento_antigo = antiga['status_pagamento'] if antiga else None
        else:
            status_antigo = None
            status_pagamento_antigo = None

        if self.status == 'FINALIZADA' and self.status_pagamento == 'PENDENTE':
            self.status_pagamento = 'AGUARDANDO_VALOR'

        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ['horario_agendado__data']

# --- Modelos atendente ---

class HorarioDisponivel(models.Model):
    veterinario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'veterinario'})
    data = models.DateTimeField()
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.veterinario.get_full_name()} - {self.data}"

    class Meta:
        verbose_name = "Horário Disponível"
        verbose_name_plural = "Horários Disponíveis"


# --- Modelos veterinario ---

class Prontuario(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE)
    finalizado = models.BooleanField(default=False)
    sinais_clinicos = models.TextField(verbose_name="Sinais Clínicos")
    diagnostico = models.TextField(verbose_name="Diagnóstico")
    exames_realizados = models.TextField(blank=True, null=True, verbose_name="Exames Realizados")
    imunizacao_aplicada = models.TextField(blank=True, null=True, verbose_name="Imunização Aplicada")
    receita_prescrita = models.FileField(upload_to='receitas/', blank=True, null=True, verbose_name="Receita Prescrita")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações Adicionais")
    criada_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prontuário - {self.consulta.pet.nome}"

    class Meta:
        verbose_name = "Prontuário" 
        verbose_name_plural = "Prontuários"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.finalizado:
            consulta = self.consulta
            consulta.status = 'REALIZADA'
            consulta.save(update_fields=['status'])


class Ausencia(models.Model):
    veterinario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'veterinario'})
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    motivo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Ausência {self.veterinario.get_full_name()} de {self.inicio.strftime('%d/%m/%Y %H:%M')} até {self.fim.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            consultas_afetadas = Consulta.objects.filter(
                veterinario=self.veterinario,
                horario_agendado__data__gte=self.inicio, 
                horario_agendado__data__lte=self.fim,
                status__in=['MARCADA', 'EM_ANDAMENTO']
            )
            for consulta in consultas_afetadas:
                consulta.status = 'CANCELADA'
                consulta.save(update_fields=['status']) 
                mensagem = (
                    f"Sua consulta com {self.veterinario.get_full_name()} em "
                    f"{consulta.horario_agendado.data.strftime('%d/%m/%Y às %H:%M')} foi cancelada devido a uma ausência do veterinário. "
                    f"Motivo: {self.motivo or 'Motivo não especificado.'} Por favor, use a opção 'Remarcar' no seu painel."
                )
                Notificacao.objects.create(
                    tutor=consulta.pet.tutor,
                    mensagem=mensagem,
                    consulta_afetada=consulta
                )

    class Meta:
        verbose_name = "Ausência"
        verbose_name_plural = "Ausências"


# --- Modelos gerais ---


class Notificacao(models.Model):
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'cliente'})
    consulta_afetada = models.ForeignKey(
        'Consulta', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    ) 
    mensagem = models.TextField()
    criada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificação para {self.tutor.get_full_name()} - {self.mensagem[:30]}"

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-criada_em']

class ValorPagamento(models.Model):
    consulta = models.OneToOneField(
        'Consulta',
        on_delete=models.CASCADE,
        related_name='valor_pagamento'
    )
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    data_definicao = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            consulta = self.consulta
            if consulta.status_pagamento in ['AGUARDANDO_VALOR', 'PENDENTE']:
                consulta.status_pagamento = 'AGUARDANDO_PAGAMENTO'
                consulta.save(update_fields=['status_pagamento'])

    def __str__(self):
        return f"Valor - {self.consulta} ({self.valor} R$)"

    class Meta:
        verbose_name = "Valor de Pagamento"
        verbose_name_plural = "Valores de Pagamento"

class PagamentoCliente(models.Model):
    consulta = models.ForeignKey(
        'Consulta',
        on_delete=models.CASCADE,
        related_name='pagamentos_cliente'
    )
    comprovante = models.FileField(upload_to='comprovantes_pagamento/')
    data_envio = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        consulta = self.consulta

        if is_new:
            if consulta.status_pagamento == 'AGUARDANDO_PAGAMENTO':
                consulta.status_pagamento = 'EM_ANALISE'
                consulta.save(update_fields=['status_pagamento'])

            GerenciamentoPagamento.objects.get_or_create(
                consulta=consulta,
                defaults={'atendente': None}
            )

    def __str__(self):
        return f"Pagamento - {self.consulta}"

    class Meta:
        verbose_name = "Pagamento do Cliente"
        verbose_name_plural = "Pagamentos dos Clientes"


class GerenciamentoPagamento(models.Model):
    STATUS_GERENCIAMENTO = [
        ('EM_ANALISE', 'Em análise'),
        ('APROVADO', 'Aprovado'),
        ('RECUSADO', 'Recusado'),
    ]

    consulta = models.OneToOneField(
        'Consulta',
        on_delete=models.CASCADE,
        related_name='gerenciamento_pagamento'
    )

    atendente = models.ForeignKey(
    CustomUser,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    limit_choices_to={'user_type': 'atendente'}
)

    status = models.CharField(max_length=20, choices=STATUS_GERENCIAMENTO, default='EM_ANALISE')
    observacao = models.TextField(blank=True, null=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        consulta = self.consulta
        if self.status == 'APROVADO' and consulta.status_pagamento != 'APROVADO':
            consulta.status_pagamento = 'APROVADO'
        elif self.status == 'RECUSADO' and consulta.status_pagamento != 'RECUSADO':
            consulta.status_pagamento = 'RECUSADO'
        elif self.status == 'EM_ANALISE' and consulta.status_pagamento != 'EM_ANALISE':
            consulta.status_pagamento = 'EM_ANALISE'

        consulta.save(update_fields=['status_pagamento'])

    def __str__(self):
        return f"Gerenciamento - Consulta {self.consulta.id} ({self.status})"

    class Meta:
        verbose_name = "Gerenciamento de Pagamento"
        verbose_name_plural = "Gerenciamento de Pagamentos"

