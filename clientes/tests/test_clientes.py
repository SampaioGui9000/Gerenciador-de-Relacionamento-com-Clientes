import pytest
from django.urls import reverse

from clientes.models import Cliente

pytestmark = pytest.mark.django_db

PAYLOAD = {"nome": "Carla Dias", "email": "carla@exemplo.com", "telefone": "31977770003"}


def test_cadastro_valido_define_responsavel_e_data(vendedor1_client, vendedor1):
    resp = vendedor1_client.post(reverse("cliente-list"), PAYLOAD)
    assert resp.status_code == 201
    assert resp.data["responsavel"] == vendedor1.id
    assert resp.data["criado_em"] is not None
    assert Cliente.objects.count() == 1


@pytest.mark.parametrize(
    "campo,valor",
    [("nome", ""), ("email", "nao-e-email"), ("telefone", ""), ("email", "")],
)
def test_cadastro_invalido(vendedor1_client, campo, valor):
    resp = vendedor1_client.post(reverse("cliente-list"), {**PAYLOAD, campo: valor})
    assert resp.status_code == 400
    assert campo in resp.data


def test_cadastro_sem_campos_obrigatorios(vendedor1_client):
    resp = vendedor1_client.post(reverse("cliente-list"), {})
    assert resp.status_code == 400
    assert {"nome", "email", "telefone"} <= set(resp.data)


def test_email_duplicado_rejeitado(vendedor1_client, cliente_v1):
    resp = vendedor1_client.post(reverse("cliente-list"), {**PAYLOAD, "email": cliente_v1.email})
    assert resp.status_code == 400
    assert "email" in resp.data


def test_email_duplicado_ignora_caixa(vendedor1_client, cliente_v1):
    resp = vendedor1_client.post(reverse("cliente-list"), {**PAYLOAD, "email": "ANA@Exemplo.com"})
    assert resp.status_code == 400


def test_email_e_normalizado_para_minusculas(vendedor1_client):
    resp = vendedor1_client.post(reverse("cliente-list"), {**PAYLOAD, "email": "CARLA@Exemplo.COM"})
    assert resp.status_code == 201
    assert resp.data["email"] == "carla@exemplo.com"


def test_listagem_retorna_clientes(vendedor1_client, cliente_v1):
    resp = vendedor1_client.get(reverse("cliente-list"))
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["email"] == cliente_v1.email


def test_detalhe_e_atualizacao_proprio_cliente(vendedor1_client, cliente_v1):
    url = reverse("cliente-detail", args=[cliente_v1.id])
    assert vendedor1_client.get(url).status_code == 200
    resp = vendedor1_client.patch(url, {"telefone": "11000000000"})
    assert resp.status_code == 200
    cliente_v1.refresh_from_db()
    assert cliente_v1.telefone == "11000000000"


def test_atualizar_mantendo_proprio_email_e_permitido(vendedor1_client, cliente_v1):
    url = reverse("cliente-detail", args=[cliente_v1.id])
    resp = vendedor1_client.patch(url, {"email": cliente_v1.email, "nome": "Ana Maria"})
    assert resp.status_code == 200


def test_remocao_proprio_cliente(vendedor1_client, cliente_v1):
    resp = vendedor1_client.delete(reverse("cliente-detail", args=[cliente_v1.id]))
    assert resp.status_code == 204
    assert Cliente.objects.count() == 0


def test_str_dos_modelos(cliente_v1, nota_v1):
    assert "Ana Souza" in str(cliente_v1)
    assert str(nota_v1).startswith("Nota #")
