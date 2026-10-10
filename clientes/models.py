from django.conf import settings
from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    criado_em = models.DateTimeField(auto_now_add=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="clientes",
    )

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} <{self.email}>"


class Nota(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="notas")
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notas_criadas",
    )

    class Meta:
        ordering = ["criado_em", "id"]

    def __str__(self):
        return f"Nota #{self.pk} de {self.cliente_id}"
