# Checklist de revisão técnica — WorkAttest

Guia operacional para confirmar o estado do MVP e registar a revisão.

- **Para:** R. Braga (@RBraga01)
- **De:** Miguel Santos / WorkAttest
- **Data da auditoria:** 16 de julho de 2026
- **Repositório:** `migmcc/WorkAttest` (privado)
- **Acesso:** colaborador aceite; leitura e escrita no modelo de conta pessoal

> **Resultado resumido:** o snapshot local e o GitHub coincidem no commit
> `2b0fb055dd9540870bfa57d4a1cb6847cbbd26d6`; a suite completa passou com 85
> testes; o ciclo ProjectPilot está em `done`. A documentação ainda contém
> referências históricas que devem ser lidas com atenção.

## Objetivo e resultado atual

Este checklist permite que o revisor confirme, a partir de um clone limpo, que o
código, os testes e o estado de lifecycle observados na auditoria continuam
alinhados. O documento separa factos confirmados de limites conhecidos; não é
uma declaração de release de produção nem uma garantia sobre a correção do
trabalho produzido por IA.

O acesso de @RBraga01 está operacional. Como o repositório é privado e pertence
a uma conta pessoal, o papel de colaborador aceite inclui pull (leitura) e push
(escrita); o GitHub não disponibiliza uma promoção adicional de função neste
modelo.

## Como verificar

Execute os passos seguintes num clone atualizado. Se o resultado diferir do
esperado, registe o comando, o output resumido e o commit analisado na secção
de registo do revisor.

**1. Confirmar a origem** — garante que o clone aponta para o repositório correto.

```bash
git remote -v
```

Esperado: deve mostrar `https://github.com/migmcc/WorkAttest.git` para fetch e push.

**2. Confirmar branch e limpeza** — evita misturar alterações locais com o baseline auditado.

```bash
git status --short --branch
```

Esperado: branch `master` e working tree sem alterações de utilizador.

**3. Confirmar o commit** — identifica exatamente o snapshot que está a ser revisto.

```bash
git rev-parse HEAD
```

Esperado: `2b0fb055dd9540870bfa57d4a1cb6847cbbd26d6`.

**4. Comparar o tip remoto** — confirma que o commit local corresponde ao master publicado.

```bash
git ls-remote origin refs/heads/master
```

Esperado: a referência remota deve começar por `2b0fb055dd9540870bfa57d4a1cb6847cbbd26d6`.

**5. Executar a suite** — reproduz a verificação funcional do MVP no ambiente local.

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Esperado: exit code 0 e `85 passed` (ou um resultado posterior claramente explicado).

**6. Ler a evidência** — confirma o âmbito e as exclusões sem transformar o relatório num claim de produção.

```powershell
Get-Content -Raw docs\TEST-REPORT.md
```

Esperado: o relatório deve manter explícitos os limites — mercado, T-1 a T-12
completo, segunda máquina, OIDC/SSO e transparency log.

## Matriz de resultados

Resultado observado em 16 de julho de 2026. O revisor deve atualizar apenas o
campo de observações se repetir a auditoria num commit diferente.

| Verificação | Critério | Resultado observado | Estado |
|---|---|---|---|
| Acesso | Colaborador aceite | @RBraga01 aparece como Collaborator no repositório privado; nesse modelo, o acesso inclui leitura e escrita. | PASS |
| Snapshot | Commit local = GitHub | `master` identificado como `2b0fb055dd9540870bfa57d4a1cb6847cbbd26d6`. | PASS |
| Git local | Working tree limpo | A auditoria encontrou a cópia local sem alterações de utilizador. | PASS |
| Testes | Exit code 0 | Suite completa: 85 passed em 3.82s (Python 3.13.14 / pytest 9.1.1). | PASS |
| Lifecycle | ProjectPilot `done` | `status.json` regista `current_phase=done` e aprovação manual do MVP core. | PASS |
| GitHub | Topologia e CI | Só existe `master`; não havia PRs nem checks de commit configurados no momento da auditoria. | PASS |
| Documentação | Estado coerente | `INIT.md`, `docs/BUILD-EVIDENCE.md` e marcações da `ROADMAP` ainda têm referências históricas não reconciliadas. | ATENÇÃO |

## Limites conhecidos

- A suite verde valida o ambiente testado; não prova ausência de bugs nem
  correção semântica do código.
- A cobertura adversarial T-1 a T-12 ainda não está completa; os casos
  implementados estão verdes.
- A verificação noutra máquina, entrevistas de mercado e willingness-to-pay
  continuam fora da evidência técnica local.
- Não há neste snapshot transparency log, OIDC/SSO, GitHub App completa ou
  control plane enterprise.

## Inconsistências documentais

Estas diferenças não invalidam o commit auditado, mas devem ser reconciliadas
numa próxima atualização documental:

- `INIT.md` — ainda descreve o estágio como planning / Fase 0–1, apesar de o
  estado ProjectPilot posterior estar em `done`.
- `docs/BUILD-EVIDENCE.md` — termina dizendo que os gates humanos permanecem não
  aprovados, em conflito com `done_approval` no `status.json`.
- `docs/ROADMAP.md` — mantém checkboxes pendentes para artefactos que já existem
  no repositório; deve distinguir existência de aprovação completa.

## Registo do revisor

Preencha depois de repetir os passos. Se houver divergência, anexe o output
relevante ou abra uma issue/PR com o commit e o comando que reproduzem o
problema.

- **Revisor:** @RBraga01
- **Data da revisão:**
- **Commit verificado:**
- **Decisão:**
  - [ ] Confirmado
  - [ ] Confirmado com observações
  - [ ] Bloqueado
- **Observações:**
- **Próxima ação:**

## Fontes consultadas

`README.md` · `docs/TEST-REPORT.md` · `docs/BUILD-EVIDENCE.md` · `TASKS.md` ·
`INIT.md` · `.project-pilot/status.json`
