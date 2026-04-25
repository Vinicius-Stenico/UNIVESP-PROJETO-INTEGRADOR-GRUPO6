# 🗄️ Database

## 📌 O que é esta pasta?
Esta pasta reúne tudo relacionado à estrutura do banco de dados do projeto.

## 📂 O que deve ser colocado aqui?
- Scripts SQL
- Modelagem do banco
- Criação de tabelas
- Dados iniciais
- Seeds
- Diagrama entidade-relacionamento
- Migrações, se houver

### Exemplos de arquivos:
- `schema.sql`
- `seed.sql`
- `modelagem-bd.png`
- `usuarios.sql`
- `solicitacoes.sql`

## 🧠 Boas práticas
- Manter a estrutura do banco documentada.
- Nomear tabelas e colunas de forma clara.
- Evitar duplicidade de dados desnecessária.
- Versionar alterações importantes no esquema.
- Guardar scripts separados por finalidade.
- Testar os comandos antes de aplicar em produção.

## 📁 Estrutura sugerida
```bash
database/
├── schema.sql
├── seeds.sql
├── diagrams/
└── migrations/
