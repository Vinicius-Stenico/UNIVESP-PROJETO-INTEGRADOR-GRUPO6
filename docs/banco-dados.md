# 🗃️ Modelo de Dados

> Este documento descreve o modelo relacional do sistema **após a fusão do PR `feature/frontend-bootstrap-jinja`**, que introduz as entidades Categoria, Material, Comentario e Evento e estende a entidade Chamado.
>
> Banco utilizado em desenvolvimento: **SQLite** (arquivo `backend/instance/chamados.db`, ignorado pelo Git).
> Banco previsto para produção: **MySQL** (configurável via variável de ambiente `DATABASE_URI`).

---

## Visão geral

O sistema possui **6 tabelas** organizadas em torno da entidade central `chamados` (solicitações):

```
                            ┌──────────────┐
                            │  usuarios    │
                            ├──────────────┤
                            │ id (PK)      │
                            │ nome         │
                            │ email (UK)   │
                            │ senha        │
                            │ tipo         │  ← professor / secretaria / admin
                            └──────┬───────┘
                                   │
       ┌───────────────────────────┼───────────────────────────────┐
       │                           │                               │
       │ usuario_id                │ usuario_id                    │ usuario_id
       │ atualizado_por            │                               │
       │                           │                               │
┌──────▼──────────────┐    ┌───────▼─────────────┐    ┌────────────▼────────┐
│  chamados           │    │  comentarios        │    │  eventos            │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ id (PK)             │◄───┤ chamado_id (FK)     │    │ id (PK)             │
│ titulo              │    │ id (PK)             │    │ chamado_id (FK)     │──► chamados
│ descricao           │    │ usuario_id (FK)     │    │ usuario_id (FK)     │
│ status              │    │ texto               │    │ tipo                │
│ usuario_id (FK)     │    │ data_criacao        │    │ descricao           │
│ atualizado_por (FK) │    └─────────────────────┘    │ status_novo         │
│ categoria_id (FK)   │──┐                            │ data_criacao        │
│ anexo_path          │  │                            └─────────────────────┘
│ anexo_nome          │  │
│ data_criacao        │  │
│ data_atualizacao    │  │
└─────────────────────┘  │
                         │
                         ▼
                 ┌──────────────┐         ┌─────────────────────┐
                 │ categorias   │◄────────┤  materiais          │
                 ├──────────────┤         ├─────────────────────┤
                 │ id (PK)      │         │ id (PK)             │
                 │ nome (UK)    │         │ nome                │
                 │ ativo        │         │ categoria_id (FK)   │
                 └──────────────┘         │ unidade             │
                                          │ ativo               │
                                          └─────────────────────┘
```

---

## Tabelas

### `usuarios`
Cadastro único de quem usa o sistema.

| Campo | Tipo | Restrições | Observação |
|---|---|---|---|
| id | INTEGER | PK, auto-increment | |
| nome | VARCHAR(100) | NOT NULL | |
| email | VARCHAR(120) | UNIQUE, NOT NULL | usado no login |
| senha | VARCHAR(255) | NOT NULL | hash via `werkzeug.security.generate_password_hash` |
| tipo | VARCHAR(20) | NOT NULL, default `professor` | enum implícito |

**Valores válidos de `tipo`:** `professor`, `secretaria`, `admin`.

> ⚠️ **Pendência (RF02 / RF11):** O escopo prevê o perfil **Direção** (leitor read-only de todas as solicitações). Ainda não implementado — a tabela `usuarios` aceita apenas os 3 tipos acima.

---

### `categorias`
Categorias possíveis para classificar uma solicitação.

| Campo | Tipo | Restrições | Observação |
|---|---|---|---|
| id | INTEGER | PK | |
| nome | VARCHAR(100) | UNIQUE, NOT NULL | |
| ativo | BOOLEAN | NOT NULL, default `TRUE` | desativar em vez de excluir |

**Categorias padrão (seed inicial, conforme RF04):**
- Material Escolar
- Material de Saúde
- Impressão/Pesquisa
- Outros

---

### `materiais`
Catálogo administrativo de itens que podem ser referenciados em uma solicitação.

| Campo | Tipo | Restrições | Observação |
|---|---|---|---|
| id | INTEGER | PK | |
| nome | VARCHAR(150) | NOT NULL | |
| categoria_id | INTEGER | FK → `categorias.id` | nullable |
| unidade | VARCHAR(20) | nullable | ex: `un`, `cx`, `frasco` |
| ativo | BOOLEAN | NOT NULL, default `TRUE` | |

> Materiais não compunham o escopo original do MVP, mas foram adicionados para alimentar o seletor de itens no formulário de Nova Solicitação. A relação `chamados ↔ materiais` é informal — o item escolhido é serializado dentro do campo `descricao` do chamado (formato `Item: <nome>`).

---

### `chamados`
Entidade central — representa uma solicitação interna.

| Campo | Tipo | Restrições | Observação |
|---|---|---|---|
| id | INTEGER | PK | |
| titulo | VARCHAR(100) | NOT NULL | |
| descricao | TEXT | NOT NULL | pode incluir `Item: <X>` no início |
| status | VARCHAR(20) | default `Aberto` | enum implícito |
| usuario_id | INTEGER | FK → `usuarios.id` | autor da solicitação |
| atualizado_por | INTEGER | FK → `usuarios.id` | quem fez a última alteração de status |
| categoria_id | INTEGER | FK → `categorias.id` | nullable |
| anexo_path | VARCHAR(255) | nullable | nome único do arquivo no FS |
| anexo_nome | VARCHAR(255) | nullable | nome original (para download) |
| data_criacao | DATETIME | default `now (America/Sao_Paulo)` | |
| data_atualizacao | DATETIME | onupdate automático | |

**Valores válidos de `status` e transições:**

```
   Aberto ──► Em andamento ──► Resolvido
      │                │
      └────────────────┴──────► Cancelado
```

- **Aberto**: criado pela professora; ela pode editar enquanto estiver neste estado
- **Em andamento**: secretaria assumiu o atendimento (bloqueia edição da professora)
- **Resolvido**: atendimento concluído (read-only total)
- **Cancelado**: cancelado pela secretaria/admin ou pelo próprio dono enquanto ativo (read-only total)

**Regras de permissão atuais** (controlador `chamados_controller.atualizar_status`):
- `secretaria` ou `admin`: pode mover para qualquer status válido
- `professor`: só pode mover para `Cancelado` se for o autor e o chamado estiver em `Aberto` ou `Em andamento`

**Anexos:**
Arquivos são salvos em `backend/uploads/` (ignorada pelo Git) com nome único `<uuid>_<nome-original>`. O download é servido por `GET /api/chamados/<id>/anexo`. Tipos aceitos: `pdf`, `png`, `jpg`, `jpeg`, `gif`, `doc`, `docx`, `xls`, `xlsx`, `txt`. Limite de upload: 10 MB.

---

### `comentarios`
Comentários textuais associados a uma solicitação.

| Campo | Tipo | Restrições | Observação |
|---|---|---|---|
| id | INTEGER | PK | |
| chamado_id | INTEGER | FK → `chamados.id`, NOT NULL | |
| usuario_id | INTEGER | FK → `usuarios.id`, NOT NULL | autor do comentário |
| texto | TEXT | NOT NULL | |
| data_criacao | DATETIME | | |

**Regras:**
- Qualquer usuário autenticado pode comentar enquanto o chamado estiver em `Aberto` ou `Em andamento`
- `Resolvido` e `Cancelado`: comentários ficam bloqueados (somente leitura)
- Adicionar um comentário registra automaticamente um `Evento` do tipo `comentario`

---

### `eventos`
Histórico/auditoria de tudo que acontece em cada solicitação. Cobre o RF09.

| Campo | Tipo | Restrições | Observação |
|---|---|---|---|
| id | INTEGER | PK | |
| chamado_id | INTEGER | FK → `chamados.id`, NOT NULL | |
| usuario_id | INTEGER | FK → `usuarios.id`, nullable | quem causou o evento |
| tipo | VARCHAR(30) | NOT NULL | enum implícito |
| descricao | TEXT | NOT NULL | texto formatado para exibição |
| status_novo | VARCHAR(30) | nullable | preenchido em `criacao` e `status` |
| data_criacao | DATETIME | | |

**Valores válidos de `tipo`:**

| tipo | Quando é gerado | `status_novo` |
|---|---|---|
| `criacao` | ao criar a solicitação | `Aberto` |
| `status` | a cada mudança de status | novo status |
| `comentario` | a cada novo comentário | (nulo) |
| `edicao` | quando o conteúdo do chamado é alterado | (nulo) |

---

## Relacionamentos (resumo)

| De → Para | Tipo | Cardinalidade |
|---|---|---|
| `chamados.usuario_id` → `usuarios.id` | autor | 1:N |
| `chamados.atualizado_por` → `usuarios.id` | última alteração | 1:N (nullable) |
| `chamados.categoria_id` → `categorias.id` | classificação | 1:N (nullable) |
| `materiais.categoria_id` → `categorias.id` | agrupamento | 1:N (nullable) |
| `comentarios.chamado_id` → `chamados.id` | comentários | 1:N |
| `comentarios.usuario_id` → `usuarios.id` | autor do comentário | 1:N |
| `eventos.chamado_id` → `chamados.id` | histórico | 1:N |
| `eventos.usuario_id` → `usuarios.id` | quem causou | 1:N (nullable) |

---

## Comparação com o escopo (MVP PI1.pdf)

| Tabela proposta no escopo | Estado atual | Observação |
|---|---|---|
| `usuarios` | ✅ implementada | |
| `perfis` | ❌ não criada | Tipo armazenado como string em `usuarios.tipo`. Pode ser refatorada para tabela separada se a Direção for adicionada com permissões granulares. |
| `categorias` | ✅ implementada | |
| `solicitacoes` | ✅ → `chamados` | Renomeada para alinhar com a nomenclatura usada no código original do projeto. |
| `historico_status` | ✅ → `eventos` | Generalizada para suportar mais tipos de evento (criação, status, edição, comentário) — cobre o RF09 com mais flexibilidade. |
| (extra) `materiais` | ➕ adicionada | Catálogo administrativo, alimenta o seletor de itens no formulário. |
| (extra) `comentarios` | ➕ adicionada | Não está no escopo formal, mas está previsto na tela de detalhes do Figma. |

### Diferenças intencionais em relação ao documento original

- **`solicitacoes.bloqueada` (BOOLEAN)** não foi implementado. A regra equivalente é checada via `status != 'Aberto'`, com mesma efetividade.
- **`historico_status.observacao` (TEXT)** não tem campo separado. Para mudanças de status, a observação é omitida (a UI deixa o campo de comentário separado, gerando entrada em `comentarios` quando necessário).
- **`historico_status.status_anterior`** não é persistido. Pode ser inferido do evento imediatamente anterior do mesmo `chamado_id`.
- **`solicitacoes.responsavel_id`** virou **`atualizado_por`** — semanticamente equivalente.

---

## Migrações e seed

O projeto **não usa Flask-Migrate / Alembic**. Mudanças de schema são aplicadas em duas etapas:
1. `db.create_all()` (chamado em `app.py`) cria as tabelas que ainda não existem
2. Para adicionar **colunas** em tabelas já existentes, é necessário rodar `ALTER TABLE` manualmente via shell SQLAlchemy

Exemplo de migração manual (já aplicada):
```python
from sqlalchemy import text, inspect
with app.app_context():
    cols = [c['name'] for c in inspect(db.engine).get_columns('chamados')]
    if 'categoria_id' not in cols:
        db.session.execute(text(
            'ALTER TABLE chamados ADD COLUMN categoria_id INTEGER REFERENCES categorias(id)'
        ))
        db.session.commit()
```

**Seed inicial** (categorias do RF04 + usuário admin) — executar uma vez após o primeiro `db.create_all()`:
```python
from controllers.usuarios_controller import criar_usuario
from models.categoria import Categoria

CATEGORIAS = ['Material Escolar', 'Material de Saúde', 'Impressão/Pesquisa', 'Outros']

with app.app_context():
    db.create_all()
    if not Categoria.query.first():
        for nome in CATEGORIAS:
            db.session.add(Categoria(nome=nome))
        db.session.commit()
    if not Usuario.query.filter_by(email='admin@admin.com').first():
        criar_usuario('admin', 'admin@admin.com', 'mude123', 'admin')
```

---

## Pendências e melhorias previstas

- Adicionar perfil **Direção** (read-only) — tabela `usuarios` precisa aceitar o novo `tipo` e a camada de permissões precisa expor visualização sem ações
- Refatorar `usuarios.tipo` em tabela `perfis` separada (permite permissões mais ricas)
- Adicionar `historico_status.observacao` para mudanças de status que não exigem comentário separado
- Migrar para **MySQL** em produção (configurável via `DATABASE_URI`)
- Avaliar adoção de **Flask-Migrate / Alembic** quando a quantidade de migrações justificar
