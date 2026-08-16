# Q5 — API REST de criação de usuário

## O que foi implementado
Foi criada uma API FastAPI em `application/app.py` com o endpoint:

- `POST /v1/users`

Campos tratados:
- Obrigatórios: `name`, `email`, `role_id`.
- Opcional: `password`.

Comportamento:
1. Valida formato de entrada via Pydantic.
2. Verifica se e-mail já existe.
3. Verifica se `role_id` existe.
4. Se a senha não vier, gera automaticamente.
5. Faz hash seguro da senha com PBKDF2-HMAC-SHA256.
6. Persiste usuário e retorna resposta com indicação se a senha foi gerada automaticamente.

## Organização por responsabilidade
- `application/database.py`: engine, sessão e inicialização de schema.
- `application/models.py`: entidades ORM (`User` e `Role`).
- `application/schemas.py`: contratos de request/response.
- `application/services/password_service.py`: geração e hash de senha.
- `application/service/user_service.py`: regra de negócio de criação de usuário.
- `application/service/role_service.py`: regra de negócio de criação de funções.
- `application/repository.py`: acesso a dados (consultas e criação).
- `application/settings.py`: variáveis de ambiente e padrões de segurança.
- `application/app.py`: rota HTTP e composição de dependências.

## Requisitos
- `requirements.txt`: `fastapi`, `pydantic`, `email-validator`, `sqlalchemy`, `uvicorn`.
- **Python recomendado:** 3.11+

## Instalação e execução
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn application.app:app --reload
```

## Variáveis de ambiente
- `USER_API_TOKEN`
- `USER_DATABASE_URL`
- `USER_PASSWORD_ITERATIONS`
- `USER_PASSWORD_SALT_BYTES`
- `USER_GENERATED_PASSWORD_LENGTH`

Exemplo:
```bash
export USER_API_TOKEN="token-fixo-da-api"
export USER_DATABASE_URL="sqlite:///users.db"
export USER_PASSWORD_ITERATIONS="200000"
```

## Autenticação
- Envie o header `Authorization: Bearer <token>`.
- O token é fixo e deve ser definido em `USER_API_TOKEN`.

## Escolhas técnicas e por quê
- **Service + Repository**: separa regra de negócio da persistência.
- **Validação na borda (Pydantic)**: evita propagar dados inválidos.
- **Hash com PBKDF2 + salt**: prática de segurança para armazenamento de senha.
- **Resposta sem expor senha**: preserva segurança e minimiza vazamento.
- **Entrypoint fino** no arquivo legado (`create_user_api.py`): mantém compatibilidade e melhora organização.

## Testes
- `application/tests/unit/test_password_service.py`
- `application/tests/unit/test_repository.py`
- `application/tests/unit/test_role.py`
- `application/tests/api/test_create_role_user_api.py`

```bash
pytest
```

## Decisões de design
- Uso de `409` para e-mail duplicado.
- Uso de `400` para `role_id` inválido.
- Campo `auto_generated_password` para transparência de comportamento.


## Exemplos de uso (curl)

### Criação de role e usuário

```bash
curl -X POST http://localhost:8000/v1/roles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token-fixo-da-api" \
  -d '{"id": 1, "description": "Admin"}'
```

```bash
curl -X POST http://localhost:8000/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token-fixo-da-api" \
  -d '{"name": "Maria", "email": "maria@example.com", "role_id": 1}'
```