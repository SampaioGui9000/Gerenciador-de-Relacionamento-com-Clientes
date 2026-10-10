import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from clientes.models import Cliente
from clientes.permissions import is_admin, is_vendedor

pytestmark = pytest.mark.django_db


# ---------- vendedor x vendedor ----------
def test_vendedor_lista_somente_seus_clientes(vendedor1_client, cliente_v1, cliente_v2):
    resp = vendedor1_client.get(reverse("cliente-list"))
    assert [c["id"] for c in resp.data["results"]] == [cliente_v1.id]


@pytest.mark.parametrize("metodo", ["get", "patch", "delete"])
def test_vendedor_nao_acessa_cliente_de_outro(vendedor1_client, cliente_v2, metodo):
    url = reverse("cliente-detail", args=[cliente_v2.id])
    resp = getattr(vendedor1_client, metodo)(url, {"nome": "hack"}) if metodo == "patch" else getattr(vendedor1_client, metodo)(url)
    assert resp.status_code == 404
    cliente_v2.refresh_from_db()
    assert cliente_v2.nome == "Bruno Lima"


def test_vendedor_nao_ve_nem_cria_notas_de_cliente_alheio(vendedor1_client, cliente_v2, nota_v2):
    url = reverse("cliente-notas", args=[cliente_v2.id])
    assert vendedor1_client.get(url).status_code == 404
    assert vendedor1_client.post(url, {"texto": "intruso"}).status_code == 404


@pytest.mark.parametrize("metodo", ["get", "patch", "delete"])
def test_vendedor_nao_acessa_nota_de_outro(vendedor1_client, nota_v2, metodo):
    url = reverse("nota-detail", args=[nota_v2.id])
    if metodo == "patch":
        resp = vendedor1_client.patch(url, {"texto": "hack"})
    else:
        resp = getattr(vendedor1_client, metodo)(url)
    assert resp.status_code == 404


def test_listagem_global_de_notas_so_mostra_as_proprias(vendedor1_client, nota_v1, nota_v2):
    resp = vendedor1_client.get(reverse("nota-list"))
    assert [n["id"] for n in resp.data["results"]] == [nota_v1.id]


def test_vendedor_nao_consegue_se_passar_por_outro_responsavel(vendedor1_client, vendedor1, vendedor2):
    resp = vendedor1_client.post(
        reverse("cliente-list"),
        {"nome": "X", "email": "x@x.com", "telefone": "1", "responsavel": vendedor2.id},
    )
    assert resp.status_code == 201
    assert resp.data["responsavel"] == vendedor1.id


def test_vendedor_nao_transfere_cliente_para_outro(vendedor1_client, cliente_v1, vendedor1, vendedor2):
    resp = vendedor1_client.patch(reverse("cliente-detail", args=[cliente_v1.id]), {"responsavel": vendedor2.id})
    assert resp.status_code == 200
    cliente_v1.refresh_from_db()
    assert cliente_v1.responsavel == vendedor1


# ---------- administrador ----------
def test_admin_lista_todos_os_clientes(admin_client, cliente_v1, cliente_v2):
    resp = admin_client.get(reverse("cliente-list"))
    assert resp.data["count"] == 2


def test_admin_edita_e_remove_qualquer_cliente(admin_client, cliente_v1, cliente_v2):
    resp = admin_client.patch(reverse("cliente-detail", args=[cliente_v2.id]), {"nome": "Editado"})
    assert resp.status_code == 200
    assert admin_client.delete(reverse("cliente-detail", args=[cliente_v1.id])).status_code == 204


def test_admin_acessa_e_edita_qualquer_nota(admin_client, nota_v1, nota_v2):
    assert admin_client.get(reverse("nota-list")).data["count"] == 2
    resp = admin_client.patch(reverse("nota-detail", args=[nota_v2.id]), {"texto": "revisada"})
    assert resp.status_code == 200


def test_admin_adiciona_nota_em_cliente_de_vendedor(admin_client, cliente_v1, admin):
    resp = admin_client.post(reverse("cliente-notas", args=[cliente_v1.id]), {"texto": "nota do admin"})
    assert resp.status_code == 201
    assert resp.data["autor"] == admin.id


def test_admin_pode_definir_responsavel(admin_client, vendedor2):
    resp = admin_client.post(
        reverse("cliente-list"),
        {"nome": "Y", "email": "y@y.com", "telefone": "2", "responsavel": vendedor2.id},
    )
    assert resp.status_code == 201
    assert Cliente.objects.get().responsavel == vendedor2


def test_admin_sem_responsavel_vira_responsavel(admin_client, admin):
    resp = admin_client.post(reverse("cliente-list"), {"nome": "Z", "email": "z@z.com", "telefone": "3"})
    assert resp.data["responsavel"] == admin.id


def test_admin_transfere_cliente(admin_client, cliente_v1, vendedor2):
    resp = admin_client.patch(reverse("cliente-detail", args=[cliente_v1.id]), {"responsavel": vendedor2.id})
    assert resp.status_code == 200
    cliente_v1.refresh_from_db()
    assert cliente_v1.responsavel == vendedor2


# ---------- funções auxiliares ----------
def test_helpers_de_perfil(admin, vendedor1, sem_perfil, django_user_model):
    superuser = django_user_model.objects.create_superuser("root", "r@r.com", "x")
    assert is_admin(admin) and is_admin(superuser)
    assert not is_admin(vendedor1) and is_vendedor(vendedor1)
    assert not is_admin(sem_perfil) and not is_vendedor(sem_perfil)
    assert not is_admin(AnonymousUser()) and not is_vendedor(AnonymousUser())


def test_grupos_sao_criados_automaticamente(db):
    from django.contrib.auth.models import Group

    assert set(Group.objects.values_list("name", flat=True)) >= {"administrador", "vendedor"}
