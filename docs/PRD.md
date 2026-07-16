# PRD — WorkAttest (MVP: AI Software Change Accountability)

> **Proof before acceptance.**

| | |
|---|---|
| **Documento** | Product Requirements Document |
| **Âmbito** | MVP — primeiro wedge (alterações de software assistidas por IA) |
| **Estado** | Planning |
| **Fonte** | `ideia-workattest.md`, `PROJECT_BRIEF.md` |
| **Fora de âmbito** | Ver §9 e `PROJECT_BRIEF.md` §7 |

---

## 1. Objetivo do produto (MVP)

Demonstrar, ponta-a-ponta, que uma alteração de software assistida por IA pode ser
**autorizada, observada, verificada, aprovada e transformada num receipt assinado que
qualquer terceiro valida offline** — sem confiar na aplicação que o produziu.

O MVP prova o **modelo de accountability**, não a amplitude da plataforma.

## 2. Utilizadores e jobs-to-be-done

| Utilizador | Job | Necessidade que o MVP satisfaz |
|---|---|---|
| Programador / operador de agente | Executar uma alteração assistida por IA | Obter autorização com âmbito e produzir evidência sem fricção manual |
| Engineering manager / approver | Aceitar um resultado | Aprovar *exatamente* o artefacto verificado, com identidade autenticada |
| Security / quality engineer | Definir e garantir checks | Garantir que os checks obrigatórios correm e que o agente não os escolhe |
| Auditor / compliance | Reconstruir e confiar | Verificar offline que o processo foi seguido e ligado ao artefacto |
| Terceiro externo | Confiar sem acesso ao servidor | Validar receipt com chave pública, sem o WorkAttest |

## 3. Requisitos funcionais

### 3.1 WorkRequest & Autorização
- **FR-1** O sistema regista um `WorkRequest` (intent, scope, owner, sistema, risk_class, acceptance_criteria).
- **FR-2** A policy avalia o request e emite `ACCEPT` / `HOLD` / `REFUSE` de forma **determinística**.
- **FR-3** Uma autorização válida define subject, ações permitidas, recursos, condições, validade e se exige approval. Nenhuma ação de impacto é aceite fora do âmbito autorizado.

### 3.2 Identidade
- **FR-4** Cada subject (humano, agente, service account) é verificável por chave (MVP: Ed25519 local, identidade Git/GitHub, OIDC em CI). Identidade **nunca** é apenas um nome no request body.

### 3.3 Execução & Observação
- **FR-5** Uma `ExecutionSession` liga request, autorização, agente, humano, modelo e workspace.
- **FR-6** O Git adapter captura estado inicial e final (commits, diffs, hashes de ficheiros).
- **FR-7** `ActionEvent`s relevantes são registados append-only com hash encadeado (`previous_event_hash`). Informação declarada pelo agente **nunca** é tratada como evidência verificada.

### 3.4 Evidência & Verificação
- **FR-8** `ArtifactEvidence` regista before/after hash, media type, size, source, classification para cada artefacto relevante.
- **FR-9** O Verifier executa checks definidos pelo **operador** (testes, lint, typecheck, security, custom). Cada `VerificationResult` regista check_id, versão, definition_hash, exit_code, output_hash, timing e evidence_refs.
- **FR-10** O agente **não** escolhe nem altera os checks que o verificam. Ausência de checks obrigatórios **nunca** equivale a aprovação.

### 3.5 Aprovação
- **FR-11** Ações de risco elevado exigem `ApprovalDecision` de humano autenticado, ligada ao `result_hash` da **mesma** execução, com justificação e assinatura. Append-only.

### 3.6 Receipt & Verificação independente
- **FR-12** O Receipt Issuer produz um `WorkReceipt` com serialização **canónica**, schema versionado e assinatura Ed25519, incluindo/ referenciando policy, actions_root, artifacts, verification, approvals.
- **FR-13** `workattest receipt verify <file>` valida schema, assinatura, signatário, hashes, artefactos, policy, relação com a execução e approvals — **offline**, sem acesso ao servidor principal.
- **FR-14** Qualquer alteração posterior ao receipt ou à evidência abrangida é **detetável**.

### 3.7 CLI mínima
- **FR-15** `workattest init | request create | policy evaluate | execution start/observe | evidence add | verify run | approve | receipt issue | receipt verify`.

## 4. Requisitos não-funcionais

- **NFR-1 Determinismo** — policy e serialização canónica produzem o mesmo output para o mesmo input; receipts são hashable e reproduzíveis.
- **NFR-2 Independência de infraestrutura** — o core do domínio não depende de FastAPI, GitHub, Claude, Codex ou DB específica.
- **NFR-3 Fail-safe** — falhas de identidade, policy, assinatura ou verificação fecham em segurança (nunca em `ACCEPT`).
- **NFR-4 Append-only** — ações, decisões e approvals não são mutáveis.
- **NFR-5 Minimização de dados** — conteúdo sensível nunca é incluído automaticamente na evidência; suporte a hash+referência, classificação e redaction.
- **NFR-6 Standards-first** — preferir in-toto/DSSE/Sigstore/SCITT/SLSA a cripto proprietária.
- **NFR-7 Verificação offline** — o verifier independente não requer o servidor principal nem rede.

## 5. Modelo de domínio (resumo)

`WorkRequest` · `Subject` · `Authorization` · `ExecutionSession` · `ActionEvent` ·
`ArtifactEvidence` · `VerificationResult` · `ApprovalDecision` · `WorkReceipt`.
Campos detalhados em `ideia-workattest.md` §9; invariantes em `docs/INVARIANTS.md`.

## 6. Fluxo de demonstração (aceitação do MVP)

1. Repositório Git limpo; pedido: corrigir um bug específico.
2. Policy permite alterações **apenas** em determinados diretórios.
3. Claude Code / Codex executa o trabalho num workspace observado.
4. WorkAttest recolhe commit inicial, diff, ficheiros, comandos observados, commit final.
5. Verifier corre testes, lint, typecheck, security check e um check personalizado.
6. Uma alteração **fora do scope** produz `HOLD` ou `REFUSE`.
7. Um humano autenticado aprova o commit final.
8. WorkAttest emite um receipt assinado.
9. **Outro computador** valida o receipt com a chave pública.

## 7. Critérios de aceitação (Definition of Done — MVP)

- [ ] Receipt schema v1 publicado (`schemas/work-receipt.schema.json`).
- [ ] Assinaturas Ed25519 funcionais (sign + verify).
- [ ] Git adapter (snapshots, diffs, hashes).
- [ ] Filesystem evidence.
- [ ] Policy determinística com `ACCEPT/HOLD/REFUSE`.
- [ ] Verifier independente; agente não escolhe os checks.
- [ ] Approval ligado ao execution ID e ao result_hash.
- [ ] Receipt verificável **offline** noutra máquina.
- [ ] Testes adversariais (tamper de receipt e de evidência detetado).
- [ ] Threat model documentado (`docs/THREAT-MODEL.md`).
- [ ] Demo completa Claude/Codex → Git → receipt.

## 8. Métricas & guardrails

**Métrica principal:** *Accepted work receipts por equipa por semana* (conta apenas com
artefacto final, checks corridos, policy avaliada, aprovação obtida e assinatura válida).

**Guardrails a zero:** receipt verification success < 100% · cross-execution proof
mismatch · unsigned final receipts · unauthorized impact aceite · mandatory checks
saltados · falhas de integridade de evidência não detetadas.

## 9. Fora de âmbito (MVP)

Dashboard/PWA · multi-tenant SaaS · billing · GitHub App completa · routing de modelos ·
memória · quotas · compliance EU AI Act/ISO extensivo · SIEM/ServiceNow · blockchain
própria · custom LLM · agent framework · Enterprise control plane (SSO/RBAC/SoD).

## 10. Dependências e riscos (ligação)

- Riscos e critérios de paragem: `PROJECT_BRIEF.md` §10.
- **Condição de aprovação vinculativa:** entrevistas de mercado (§19 da ideia) em
  paralelo; *willingness-to-pay* é o critério de paragem primário.
- Decisões de standards: `docs/STANDARDS-DECISIONS.md`.
- Fronteiras de confiança e ameaças: `docs/TRUST-BOUNDARIES.md`, `docs/THREAT-MODEL.md`.
