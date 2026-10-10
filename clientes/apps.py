from django.apps import AppConfig
from django.db.models.signals import post_migrate


def criar_grupos(sender, **kwargs):
    """Garante que os perfis existam após qualquer migrate (inclusive no banco de testes)."""
    from django.contrib.auth.models import Group

    from .permissions import ADMIN_GROUP, VENDEDOR_GROUP

    for nome in (ADMIN_GROUP, VENDEDOR_GROUP):
        Group.objects.get_or_create(name=nome)


class ClientesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "clientes"

    def ready(self):
        post_migrate.connect(criar_grupos, sender=self)
