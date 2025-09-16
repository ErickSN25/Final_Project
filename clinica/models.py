from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O usuário precisa ter um e-mail")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password) 
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário precisa ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_type_choices = (
        ('veterinario', 'Veterinário'),
        ('cliente', 'Cliente'),
        ('atendente', 'Atendente'),
    )
    
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=30)
    sobrenome = models.CharField(max_length=30)
    cpf = models.CharField(max_length=11, unique=True)
    crmv = models.CharField(max_length=10, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    type = models.CharField(max_length=20, choices=user_type_choices)
    
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'sobrenome', 'cpf', 'type']

    def __str__(self):
        return self.email

