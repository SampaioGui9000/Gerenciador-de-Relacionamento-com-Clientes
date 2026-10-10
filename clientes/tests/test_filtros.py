import pytest
from django.urls import reverse

from clientes.models import Cliente

pytestmark = pytest.mark.django_db


@pytest.fixture
def carteira(vendedor1):
    dados = [
        ("Ana Souza", "ana@exemplo.com", "11999990001"),
        ("Mariana Costa", "mari@empresa.com", "11988887777"),
        ("Bruno Lima", "bruno@exemplo.com", "21977776666"),
    ]
    return [Cliente.objects.create(nome=n, email=e, telefone=t, responsavel=vendedor1) for n, e, t in dados]


def nomes(resp):
    return sorted(c["nome"] for c in resp.data["results"])


def test_filtro_por_nome_parcial_e_case_insensitive(vendedor1_client, carteira):
    resp = vendedor1_client.get(reverse("cliente-list"), {"nome": "ANA"})
    assert nomes(resp) == ["Ana Souza", "Mariana Costa"]


def test_filtro_por_email(vendedor1_client, carteira):
    resp = vendedor1_client.get(reverse("cliente-list"), {"email": "@EXEMPLO"})
    assert nomes(resp) == ["Ana Souza", "Bruno Lima"]


def test_filtro_por_trecho_do_telefone(vendedor1_client, carteira):
    resp = vendedor1_client.get(reverse("cliente-list"), {"telefone": "7777"})
    assert nomes(resp) == ["Mariana Costa"]


def test_filtros_combinados(vendedor1_client, carteira):
    resp = vendedor1_client.get(reverse("cliente-list"), {"nome": "ana", "email": "empresa"})
    assert nomes(resp) == ["Mariana Costa"]


def test_filtro_sem_resultado(vendedor1_client, carteira):
    resp = vendedor1_client.get(reverse("cliente-list"), {"nome": "inexistente"})
    assert resp.data["count"] == 0


def test_filtro_exige_autenticacao(anon_client, carteira):
    assert anon_client.get(reverse("cliente-list"), {"nome": "ana"}).status_code == 401


def test_filtro_respeita_ownership(vendedor2_client, carteira):
    resp = vendedor2_client.get(reverse("cliente-list"), {"nome": "ana"})
    assert resp.data["count"] == 0


def test_ordenacao_por_nome(vendedor1_client, carteira):
    asc = vendedor1_client.get(reverse("cliente-list"), {"ordering": "nome"})
    assert [c["nome"] for c in asc.data["results"]] == ["Ana Souza", "Bruno Lima", "Mariana Costa"]
    desc = vendedor1_client.get(reverse("cliente-list"), {"ordering": "-nome"})
    assert desc.data["results"][0]["nome"] == "Mariana Costa"
