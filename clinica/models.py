from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Cria e retorna um usuário comum (cliente, atendente ou veterinário)."""
        if not email:
            raise ValueError("O usuário precisa ter um e-mail válido")
        
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e retorna um superusuário com acesso ao admin."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

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
    """Modelo para informações específicas de veterinários."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'veterinario'})
    crmv = models.CharField(max_length=10, unique=True, verbose_name="CRMV")

    def __str__(self):
        return f"CRMV: {self.crmv} - {self.user.get_full_name()}"

    class Meta:
        verbose_name = "Informação do Veterinário"
        verbose_name_plural = "Informações dos Veterinários"

class ClientePerfil(models.Model):
    """
    Modelo para informações adicionais e opcionais do cliente.
    """
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

    user = models.OneToOneField(
        'CustomUser', 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'cliente'}
    )
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

# --- Modelos relacionados a pets e consultas ---

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
    data = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('MARCADA', 'Marcada'),
            ('CANCELADA', 'Cancelada'),
            ('REALIZADA', 'Realizada'),
        ],
        default='MARCADA'
    )
    data_hora = models.DateTimeField()
    motivo = models.TextField()

    def __str__(self):
        return f"Consulta {self.pet.nome} - {self.veterinario.get_full_name()} ({self.data})"

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"

class Prontuario(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE)
    
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

class HorarioDisponivel(models.Model):
    veterinario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'veterinario'})
    data = models.DateTimeField()
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.veterinario.get_full_name()} - {self.data}"

    class Meta:
        verbose_name = "Horário Disponível"
        verbose_name_plural = "Horários Disponíveis"

class Ausencia(models.Model):
    veterinario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'veterinario'})
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    motivo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Ausência {self.veterinario.get_full_name()} de {self.inicio} até {self.fim}"

    class Meta:
        verbose_name = "Ausência"
        verbose_name_plural = "Ausências"

class Notificacao(models.Model):
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'cliente'})
    mensagem = models.TextField()
    criada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificação para {self.tutor.get_full_name()} - {self.mensagem[:30]}"

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-criada_em']

class Agendamento(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'veterinario'})
    data_hora = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDENTE', 'Pendente'),
            ('CONFIRMADO', 'Confirmado'),
            ('CANCELADO', 'Cancelado'),
            ('REALIZADO', 'Realizado'),
        ],
        default='PENDENTE'
    )

    def __str__(self):
        return f"Agendamento {self.pet.nome} - {self.veterinario.get_full_name()} ({self.data_hora})"

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['data_hora']