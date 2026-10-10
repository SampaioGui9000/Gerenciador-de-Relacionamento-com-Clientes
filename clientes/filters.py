import django_filters

from .models import Cliente, Nota


class ClienteFilter(django_filters.FilterSet):
    """Filtros parciais e case-insensitive: ?nome=ana&email=@exemplo&telefone=9999"""

    nome = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    telefone = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Cliente
        fields = ["nome", "email", "telefone"]


class NotaFilter(django_filters.FilterSet):
    class Meta:
        model = Nota
        fields = ["cliente"]
