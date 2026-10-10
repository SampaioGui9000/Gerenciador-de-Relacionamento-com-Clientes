from rest_framework.permissions import BasePermission

ADMIN_GROUP = "administrador"
VENDEDOR_GROUP = "vendedor"


def _in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def is_admin(user):
    """Administrador: superusuário ou membro do grupo 'administrador'."""
    return bool(user and user.is_authenticated and (user.is_superuser or _in_group(user, ADMIN_GROUP)))


def is_vendedor(user):
    return bool(user and _in_group(user, VENDEDOR_GROUP))


class IsAdminOrVendedor(BasePermission):
    """Só permite usuários com um dos perfis do CRM. Usuários sem perfil recebem 403."""

    message = "Seu usuário não possui um perfil (administrador ou vendedor) para acessar o CRM."

    def has_permission(self, request, view):
        return is_admin(request.user) or is_vendedor(request.user)
