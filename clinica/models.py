from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.exceptions import ValidationError


# =====================
# USERS MODELS
# =====================


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
        ("veterinario", "Veterinário"),
        ("cliente", "Cliente"),
        ("atendente", "Atendente"),
        ("administrador", "Administrador"),
    )

    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=30)
    sobrenome = models.CharField(max_length=30)
    cpf = models.CharField(max_length=11, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "sobrenome", "cpf", "user_type"]

    def __str__(self):
        return f"{self.nome} ({self.user_type})"

    def get_full_name(self):
        return f"{self.nome} {self.sobrenome}"

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


class VeterinarioInfo(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "veterinario"},
    )
    crmv = models.CharField(max_length=10, unique=True, verbose_name="CRMV")

    def __str__(self):
        return f"CRMV: {self.crmv} - {self.user.get_full_name()}"

    class Meta:
        verbose_name = "Informação do Veterinário"
        verbose_name_plural = "Informações dos Veterinários"


class ClientePerfil(models.Model):
    UF_CHOICES = [
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Amazonas"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
    ]

    user = models.OneToOneField(
        "CustomUser",
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "cliente"},
    )
    foto_user = models.ImageField(upload_to="fotos_perfil/", blank=True, null=True)
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


# =====================
# PETS MODELS
# =====================


class Pet(models.Model):
    especieChoices = [
        ("CACHORRO", "Cachorro"),
        ("GATO", "Gato"),
        ("COELHO", "Coelho"),
        ("PAPAGAIO", "Papagaio"),
        ("HAMSTER", "Hamster"),
        ("CALOPSITA", "Calopsita"),
        ("FURAO", "Furão"),
        ("JABUTI", "Jabuti"),
        ("PEIXE", "Peixe"),
        ("PIRIQUITO", "Periquito"),
    ]

    tutor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, limit_choices_to={"user_type": "cliente"}
    )
    foto_pet = models.ImageField(upload_to="fotos_pet/", blank=True, null=True)
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=50, choices=especieChoices)
    raca = models.CharField(max_length=50, blank=True, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    vacinas_em_dia = models.BooleanField(default=False)
    alergias = models.TextField(blank=True, null=True)
    doencas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.especie})"

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"


class Consulta(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "veterinario"},
        related_name="consultas_como_veterinario",
    )

    horario_agendado = models.OneToOneField(
        "HorarioDisponivel",
        on_delete=models.PROTECT,
        verbose_name="Horário Agendado",
        limit_choices_to={"disponivel": True},
    )

    motivo = models.TextField(verbose_name="Motivo da Consulta")

    STATUS_CHOICES = [
        ("MARCADA", "Marcada"),
        ("CANCELADA", "Cancelada"),
        ("EM_ANDAMENTO", "Em Andamento"),
        ("REALIZADA", "Realizada"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="MARCADA",
        verbose_name="Status da Consulta",
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

        elif self.status == "CANCELADA" and not self.horario_agendado.disponivel:
            self.horario_agendado.disponivel = True
            self.horario_agendado.save()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ["horario_agendado__data"]


# =====================
# ATTENDANT MODELS
# =====================


class HorarioDisponivel(models.Model):
    veterinario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "veterinario"},
    )
    data = models.DateTimeField()
    disponivel = models.BooleanField(default=True)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        status = "Disponível" if self.disponivel else "Indisponível"
        return f"{self.veterinario} - {self.data.strftime('%d/%m/%Y %H:%M')} ({status})"

    class Meta:
        verbose_name = "Horário Disponível"
        verbose_name_plural = "Horários Disponíveis"


# =====================
# VETS MODELS
# =====================


class Prontuario(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE)
    finalizado = models.BooleanField(default=False)
    sinais_clinicos = models.TextField(verbose_name="Sinais Clínicos")
    diagnostico = models.TextField(verbose_name="Diagnóstico")
    exames_realizados = models.TextField(
        blank=True, null=True, verbose_name="Exames Realizados"
    )
    imunizacao_aplicada = models.TextField(
        blank=True, null=True, verbose_name="Imunização Aplicada"
    )
    receita_prescrita = models.FileField(
        upload_to="receitas/", blank=True, null=True, verbose_name="Receita Prescrita"
    )
    observacoes = models.TextField(
        blank=True, null=True, verbose_name="Observações Adicionais"
    )
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
            consulta.status = "REALIZADA"
            consulta.save(update_fields=["status"])
