from django.db import models

class Veterinario(models.Model):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11)
    crmv = models.CharField(max_length=10)
    gmail = models.EmailField(max_length=100)
    senha = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} {self.sobrenome}"