# Sistema de Portaria — Atividade A3

UC **Teoria da Computação e Compiladores** · Profª Cíntia Silvana de Souza

Sistema desktop em Python (Tkinter + SQLite) para controle de acesso de pessoas
numa portaria: login, cadastro de pessoas, controle de entrada/saída, relatórios
com gráficos e, como desafio extra, **cadastro de veículos** e **registro de ocorrências**.

## Como executar

Requer Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

python main.py          # banco vazio
python main.py --demo   # com dados de exemplo (só se o banco estiver vazio)
```

**Usuário padrão:** `admin` · **senha:** `admin123` (criado na primeira execução).

O banco fica em `data/portaria.db`; apague o arquivo para recomeçar do zero.

Para rodar os testes: `python -m pytest`

## Telas e funcionalidades

| Tela | Principais regras |
|---|---|
| **Login** | Valida usuário/senha (hash PBKDF2), bloqueia campos vazios, mensagem de erro, mostrar/ocultar senha, abre a tela principal. |
| **Cadastro** | Campos obrigatórios, CPF validado pelos dígitos verificadores, CPF duplicado bloqueado, gera código (`001`), grava a 1ª entrada e confirma. |
| **Controle de Acesso** | Pesquisa por nome/CPF, filtro Todos/Dentro/Saiu, registra entrada/saída com a hora atual, impede 2ª entrada sem saída, atualiza a tabela. |
| **Início** | Contadores (dentro agora, entradas hoje, cadastrados) e lista de quem está dentro. |
| **Relatórios** | Movimentações por período, gráficos Matplotlib (por dia / por tipo), agregações com Pandas, exportação CSV. |
| **Veículos** *(extra)* | Placa no padrão antigo (`ABC-1234`) ou Mercosul (`ABC1D23`), sem duplicidade, vínculo com a pessoa. |
| **Ocorrências** *(extra)* | Tipo, descrição, pessoa envolvida (opcional), data/hora e usuário que registrou. |

## Arquitetura

```
main.py                  ponto de entrada (--demo, --db)
portaria/
  config.py              constantes, caminhos e paleta de cores
  exceptions.py          erros de domínio (ValidacaoError, AcessoError, ...)
  bootstrap.py           monta banco → repositórios → serviços
  database/              conexão SQLite, schema, dados de demonstração
  models/                dataclasses tipadas (Pessoa, Movimentacao, ...)
  repositories/          SQL parametrizado; nenhuma regra de negócio
  services/              regras de negócio; não dependem do Tkinter
  utils/                 validadores, formatadores/máscaras, hash de senha
  ui/                    Tkinter: app, login, janela principal, telas (views/)
tests/                   pytest para validadores e serviços
```

As telas só conversam com os **serviços**; os serviços lançam exceções de domínio
que a interface captura (`try/except`) e mostra em `messagebox`.

### Onde estão os requisitos técnicos

- **Tkinter / Entry / Button / Label / Combobox / Checkbutton / Treeview** — `portaria/ui/`
- **IF/ELSE** — validações em `services/` (ex.: bloqueio de 2ª entrada em `acesso_service.py`)
- **FOR/WHILE** — cálculo do CPF em `utils/validators.py`, preenchimento das tabelas nas views
- **Funções** — toda a lógica organizada em funções/métodos com type hints
- **TRY/EXCEPT** — `BaseView._rodar`, `LoginFrame._entrar`, repositórios (`sqlite3.IntegrityError`)
- **SQLite** — `portaria/database/` e `portaria/repositories/`

## Personalização

Coloque `assets/logo.png` e/ou `assets/fachada.png` (largura ~330 px) para substituir
o logotipo em texto e a ilustração da tela de login.
