from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from conftest import SENHA

pytestmark = pytest.mark.django_db


def test_login_retorna_access_e_refresh(anon_client, vendedor1):
    resp = anon_client.post(reverse("login"), {"username": "vendedor1", "password": SENHA})
    assert resp.status_code == 200
    assert "access" in resp.data and "refresh" in resp.data


def test_login_com_senha_errada(anon_client, vendedor1):
    resp = anon_client.post(reverse("login"), {"username": "vendedor1", "password": "errada"})
    assert resp.status_code == 401


def test_rota_protegida_sem_token(anon_client):
    assert anon_client.get(reverse("cliente-list")).status_code == 401
    assert anon_client.post(reverse("cliente-list"), {}).status_code == 401


def test_fluxo_completo_com_token_real(anon_client, vendedor1):
    login = anon_client.post(reverse("login"), {"username": "vendedor1", "password": SENHA})
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    assert client.get(reverse("cliente-list")).status_code == 200


def test_token_invalido(anon_client):
    anon_client.credentials(HTTP_AUTHORIZATION="Bearer token.invalido.aqui")
    assert anon_client.get(reverse("cliente-list")).status_code == 401


def test_token_expirado(anon_client, vendedor1):
    token = AccessToken.for_user(vendedor1)
    token.set_exp(lifetime=-timedelta(seconds=1))
    anon_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    assert anon_client.get(reverse("cliente-list")).status_code == 401


def test_refresh_gera_novo_access(anon_client, vendedor1):
    login = anon_client.post(reverse("login"), {"username": "vendedor1", "password": SENHA})
    resp = anon_client.post(reverse("token_refresh"), {"refresh": login.data["refresh"]})
    assert resp.status_code == 200
    assert "access" in resp.data


def test_usuario_sem_perfil_recebe_403(sem_perfil_client):
    assert sem_perfil_client.get(reverse("cliente-list")).status_code == 403


def test_tempos_de_expiracao_configurados():
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] == timedelta(minutes=5)
    assert settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] == timedelta(days=1)


def test_cors_nao_libera_todas_as_origens():
    assert settings.CORS_ALLOW_ALL_ORIGINS is False
    assert "*" not in settings.CORS_ALLOWED_ORIGINS


def test_cors_aceita_origem_autorizada_e_bloqueia_outras(anon_client):
    origem_ok = settings.CORS_ALLOWED_ORIGINS[0]
    ok = anon_client.options(reverse("cliente-list"), HTTP_ORIGIN=origem_ok)
    assert ok.headers.get("access-control-allow-origin") == origem_ok
    ruim = anon_client.options(reverse("cliente-list"), HTTP_ORIGIN="http://site-malicioso.com")
    assert "access-control-allow-origin" not in ruim.headers
