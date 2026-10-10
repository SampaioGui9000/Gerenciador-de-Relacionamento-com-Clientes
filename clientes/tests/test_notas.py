import pytest
from django.urls import reverse

from clientes.models import Nota

pytestmark = pytest.mark.django_db


def test_adicionar_nota_associa_cliente_e_autor(vendedor1_client, cliente_v1, vendedor1):
    resp = vendedor1_client.post(reverse("cliente-notas", args=[cliente_v1.id]), {"texto": "Ligou hoje"})
    assert resp.status_code == 201
    nota = Nota.objects.get()
    assert nota.cliente == cliente_v1
    assert nota.autor == vendedor1
    assert resp.data["criado_em"] is not None


def test_listar_notas_em_ordem_cronologica(vendedor1_client, cliente_v1, vendedor1):
    url = reverse("cliente-notas", args=[cliente_v1.id])
    for texto in ["primeira", "segunda", "terceira"]:
        vendedor1_client.post(url, {"texto": texto})
    resp = vendedor1_client.get(url)
    assert resp.status_code == 200
    assert [n["texto"] for n in resp.data["results"]] == ["primeira", "segunda", "terceira"]


def test_notas_de_um_cliente_nao_vazam_para_outro(admin_client, cliente_v1, cliente_v2, nota_v1, nota_v2):
    resp = admin_client.get(reverse("cliente-notas", args=[cliente_v1.id]))
    assert [n["texto"] for n in resp.data["results"]] == ["Primeiro contato"]


def test_nota_para_cliente_inexistente(vendedor1_client):
    resp = vendedor1_client.post(reverse("cliente-notas", args=[9999]), {"texto": "x"})
    assert resp.status_code == 404


@pytest.mark.parametrize("texto", ["", "   "])
def test_nota_com_texto_vazio(vendedor1_client, cliente_v1, texto):
    resp = vendedor1_client.post(reverse("cliente-notas", args=[cliente_v1.id]), {"texto": texto})
    assert resp.status_code == 400


def test_notas_exigem_autenticacao(anon_client, cliente_v1):
    url = reverse("cliente-notas", args=[cliente_v1.id])
    assert anon_client.get(url).status_code == 401
    assert anon_client.post(url, {"texto": "x"}).status_code == 401


def test_editar_e_remover_propria_nota(vendedor1_client, nota_v1):
    url = reverse("nota-detail", args=[nota_v1.id])
    assert vendedor1_client.patch(url, {"texto": "editada"}).status_code == 200
    nota_v1.refresh_from_db()
    assert nota_v1.texto == "editada"
    assert vendedor1_client.delete(url).status_code == 204


def test_listar_notas_global_filtrando_por_cliente(vendedor1_client, nota_v1, cliente_v1):
    resp = vendedor1_client.get(reverse("nota-list"), {"cliente": cliente_v1.id})
    assert resp.status_code == 200
    assert resp.data["count"] == 1
