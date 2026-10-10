# CRM API – Gerenciador de Relacionamento com Clientes

API REST em Django + Django REST Framework para gerenciar clientes e o histórico de interações (notas), com autenticação JWT, perfis de acesso, testes automatizados e Docker.

## Stack
Django 5.2 · DRF · SimpleJWT · django-cors-headers · django-filter · drf-yasg · PostgreSQL · pytest · Docker · GitHub Actions

## Rodando localmente
```bash
python -m venv venv && source venv/bin/activate      # Windows: .\venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser                      # superusuário já é "administrador"
python manage.py runserver
```
Documentação interativa: http://localhost:8000/swagger/

## Rodando com Docker
```bash
docker-compose up --build
```
Sobe a API (porta 8000) + PostgreSQL; as migrações rodam automaticamente no `entrypoint.sh`.

## Testes
```bash
pytest          # já mede cobertura e falha se ficar abaixo de 85%
```

## Endpoints
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/login/` | Login → `access` (5 min) e `refresh` (1 dia) |
| POST | `/api/auth/refresh/` | Renova o access token |
| GET/POST | `/api/clientes/` | Lista (com filtros) / cadastra |
| GET/PUT/PATCH/DELETE | `/api/clientes/{id}/` | Detalhe, edição, remoção |
| GET/POST | `/api/clientes/{id}/notas/` | Lista / adiciona notas do cliente |
| GET | `/api/notas/` | Lista notas (`?cliente=<id>`) |
| GET/PUT/PATCH/DELETE | `/api/notas/{id}/` | Detalhe, edição, remoção |

Envie o token no header `Authorization: Bearer <access>`.

**Filtros** (parciais e case-insensitive): `?nome=ana&email=@exemplo&telefone=9999`  
**Ordenação**: `?ordering=nome` ou `?ordering=-criado_em` · **Paginação**: `?page=2`

## Decisões técnicas
- **Perfis**: grupos `administrador` e `vendedor`, criados automaticamente via sinal `post_migrate`. Para criar um vendedor, crie o usuário no `/admin/` e adicione-o ao grupo `vendedor`. Usuários sem perfil recebem 403.
- **Ownership** direto na query (`get_queryset`): vendedores só enxergam `Cliente.objects.filter(responsavel=user)` e notas dos seus clientes. Recursos de terceiros retornam **404** (não vazam a existência do registro).
- **Responsável**: definido automaticamente como quem cadastrou; só administradores podem atribuir/transferir.
- **E-mail** único, normalizado em minúsculas e validado sem diferenciar maiúsculas.
- **JWT** com expiração curta e **CORS** restrito às origens em `CORS_ALLOWED_ORIGINS`.
- **CI** (`.github/workflows/ci.yml`): roda pytest com cobertura (artefato `coverage.xml`) e faz o build da imagem Docker.

## Estrutura
```
crm_api/            configurações, urls, wsgi/asgi
clientes/           models, serializers, views, filters, permissions, admin
clientes/tests/     testes de clientes, auth, notas, permissões e filtros
conftest.py         fixtures (admin, vendedores, clientes, notas)
Dockerfile · docker-compose.yml · entrypoint.sh · .dockerignore
```
