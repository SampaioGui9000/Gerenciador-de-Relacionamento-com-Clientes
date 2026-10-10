import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from clientes.models import Cliente, Nota
from clientes.permissions import ADMIN_GROUP, VENDEDOR_GROUP

User = get_user_model()
SENHA = "senha-forte-123"


def _criar_usuario(username, grupo=None, **extra):
    user = User.objects.create_user(username=username, password=SENHA, **extra)
    if grupo:
        user.groups.add(Group.objects.get_or_create(name=grupo)[0])
    return user


def _client_para(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def anon_client():
    return APIClient()


@pytest.fixture
def admin(db):
    return _criar_usuario("admin", ADMIN_GROUP)


@pytest.fixture
def vendedor1(db):
    return _criar_usuario("vendedor1", VENDEDOR_GROUP)


@pytest.fixture
def vendedor2(db):
    return _criar_usuario("vendedor2", VENDEDOR_GROUP)


@pytest.fixture
def sem_perfil(db):
    return _criar_usuario("semperfil")


@pytest.fixture
def admin_client(admin):
    return _client_para(admin)


@pytest.fixture
def vendedor1_client(vendedor1):
    return _client_para(vendedor1)


@pytest.fixture
def vendedor2_client(vendedor2):
    return _client_para(vendedor2)


@pytest.fixture
def sem_perfil_client(sem_perfil):
    return _client_para(sem_perfil)


@pytest.fixture
def cliente_v1(vendedor1):
    return Cliente.objects.create(
        nome="Ana Souza", email="ana@exemplo.com", telefone="11999990001", responsavel=vendedor1
    )


@pytest.fixture
def cliente_v2(vendedor2):
    return Cliente.objects.create(
        nome="Bruno Lima", email="bruno@empresa.com", telefone="21988880002", responsavel=vendedor2
    )


@pytest.fixture
def nota_v1(cliente_v1, vendedor1):
    return Nota.objects.create(cliente=cliente_v1, texto="Primeiro contato", autor=vendedor1)


@pytest.fixture
def nota_v2(cliente_v2, vendedor2):
    return Nota.objects.create(cliente=cliente_v2, texto="Reunião agendada", autor=vendedor2)
