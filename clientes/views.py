from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import ClienteFilter, NotaFilter
from .models import Cliente, Nota
from .permissions import IsAdminOrVendedor, is_admin
from .serializers import ClienteSerializer, NotaSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    """
    CRUD de clientes.

    Ownership: administradores veem tudo; vendedores veem apenas clientes
    em que são o `responsavel`. Registros de terceiros retornam 404.
    """

    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrVendedor]
    filterset_class = ClienteFilter
    ordering_fields = ["nome", "email", "criado_em"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Cliente.objects.none()
        queryset = Cliente.objects.select_related("responsavel")
        if is_admin(self.request.user):
            return queryset
        return queryset.filter(responsavel=self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="notas", serializer_class=NotaSerializer)
    def notas(self, request, pk=None):
        """GET: lista as notas do cliente. POST: adiciona uma nota ao cliente."""
        cliente = self.get_object()  # 404 se não existir ou não pertencer ao vendedor

        if request.method == "POST":
            serializer = NotaSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save(cliente=cliente, autor=request.user)
            return Response(serializer.data, status=201)

        queryset = cliente.notas.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(NotaSerializer(page, many=True).data)
        return Response(NotaSerializer(queryset, many=True).data)


class NotaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Consulta/edição/remoção de notas. A criação é feita em /clientes/{id}/notas/."""

    serializer_class = NotaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrVendedor]
    filterset_class = NotaFilter
    ordering_fields = ["criado_em"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Nota.objects.none()
        queryset = Nota.objects.select_related("cliente", "autor")
        if is_admin(self.request.user):
            return queryset
        return queryset.filter(cliente__responsavel=self.request.user)
