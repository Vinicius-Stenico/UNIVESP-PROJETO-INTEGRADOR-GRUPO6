# ⚙️ Backend

## 📌 O que é esta pasta?
Esta pasta contém a parte lógica da aplicação, responsável por processar dados, validar informações e fazer a comunicação com o banco de dados.

## 📂 O que deve ser colocado aqui?
- Rotas da aplicação
- Controllers
- Regras de negócio
- Autenticação e autorização
- Integração com banco de dados
- Serviços auxiliares
- Validações de dados

### Exemplos de arquivos:
- `app.py`
- `routes.py`
- `auth.py`
- `controllers/solicitacoes.py`
- `models/usuario.py`

## 🧠 Boas práticas
- Separar claramente rotas, regras e modelos.
- Manter funções pequenas e organizadas.
- Validar entradas do usuário.
- Evitar repetição de código.
- Usar nomes descritivos para arquivos e funções.
- Proteger informações sensíveis, como senhas e credenciais.

## 📁 Estrutura sugerida
```bash
backend/
├── controllers/
├── models/
├── routes/
├── services/
├── utils/
└── app.py
