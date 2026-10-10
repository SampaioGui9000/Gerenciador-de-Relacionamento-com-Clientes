from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Cliente, Nota
from .permissions import is_admin

User = get_user_model()


class ClienteSerializer(serializers.ModelSerializer):
    responsavel = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Cliente
        fields = ["id", "nome", "email", "telefone", "responsavel", "criado_em"]
        read_only_fields = ["id", "criado_em"]

    def validate_email(self, value):
        """Normaliza o e-mail e impede duplicidade ignorando maiúsculas/minúsculas."""
        value = value.strip().lower()
        duplicados = Cliente.objects.filter(email__iexact=value)
        if self.instance is not None:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise serializers.ValidationError("Já existe um cliente com este e-mail.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        # Só administradores podem definir outro responsável; os demais sempre são o dono.
        if not (is_admin(user) and validated_data.get("responsavel")):
            validated_data["responsavel"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not is_admin(self.context["request"].user):
            validated_data.pop("responsavel", None)
        return super().update(instance, validated_data)


class NotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nota
        fields = ["id", "cliente", "texto", "autor", "criado_em"]
        read_only_fields = ["id", "cliente", "autor", "criado_em"]

    def validate_texto(self, value):
        if not value.strip():
            raise serializers.ValidationError("O texto da nota não pode ficar vazio.")
        return value
