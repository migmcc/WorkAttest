# ROADMAP — WorkAttest

> **Proof before acceptance.**

Roadmap macro por fases. O MVP corresponde às Fases 0–3. As fases 4+ são expansão
de plataforma e só são justificadas após validação de mercado (ver critérios de
paragem em `PROJECT_BRIEF.md` §10 e §21 da ideia).

**Regra de ouro:** *contratos antes de integrações; core antes de UI; um único caso de
uso antes de amplitude.*

---

## Linha temporal (macro)

```
Fase 0 ── Fase 1 ── Fase 2 ── Fase 3 ──┐  (MVP)
Discovery  Core     Crypto    SW change │
contratos  determ.  receipts  adapter   │
                                        ▼
                          [ Gate MVP + validação de mercado ]
                                        │
Fase 4 ── Fase 5 ── Fase 6 ── Fase 7    ▼  (expansão, só se willingness-to-pay provada)
PPilot     Taevdar   GitHub    Enterprise
integr.    ctrl plane  App      control plane
```

**Track paralelo obrigatório (condição de aprovação):** entrevistas de mercado (§19),
a correr desde a Fase 0. *Willingness-to-pay* é o critério de paragem primário.

---

## Fase 0 — Discovery & contratos  *(MVP)*

Formalizar o modelo antes de escrever core.

**Entregáveis**
- [x] `PROJECT_BRIEF.md`
- [x] `docs/PRD.md`
- [x] `docs/ROADMAP.md`
- [x] `docs/ACCOUNTABILITY-MODEL.md`
- [x] `docs/THREAT-MODEL.md`
- [x] `docs/TRUST-BOUNDARIES.md`
- [x] `docs/INVARIANTS.md`
- [x] `docs/STANDARDS-DECISIONS.md`
- [x] `docs/COMPETITIVE-MATRIX.md`
- [x] `schemas/work-receipt.schema.json` (receipt v1)

**Gate:** modelo de confiança revisto · receipt v1 aprovado · primeiro caso de uso
fechado · zero claims de "garantia absoluta" · ≥3 entrevistas de mercado iniciadas.

## Fase 1 — Core determinístico  *(MVP)*

**Entregáveis:** entidades e estados do domínio · canonical JSON · policy decisions
(`ACCEPT/HOLD/REFUSE`) determinísticas · storage interfaces · append-only events com
hash chain · unit tests · property-based tests · CLI mínima (esqueleto).

**Gate:** domínio independente de infraestrutura · policy determinística testada ·
serialização canónica reprodutível · cobertura de invariantes de domínio.

## Fase 2 — Cryptographic receipts  *(MVP)*

**Entregáveis:** geração e gestão de chaves Ed25519 · signing e verification · modelo
de key rotation · receipt chains (`previous_receipt_hash`) · redaction · **offline
verifier** · testes adversariais de tamper.

**Gate:** receipt assinado e verificável offline · tamper de receipt/evidência
detetado · múltiplas assinaturas suportadas · schema versionado.

## Fase 3 — Software change adapter  *(MVP — fecha o MVP)*

**Entregáveis:** Git snapshots (inicial/final) · diffs · artifact hashes · observação
de comandos · Verifier com checks do operador · approval humano · **demo completa**
Claude/Codex → Git → receipt.

**Gate = Definition of Done do MVP** (ver `docs/PRD.md` §7). Executar a demo do §6 do PRD
e validar o receipt noutra máquina.

---

### ▲ Ponto de decisão pós-MVP (`PROJECT_BRIEF.md` §10 / ideia §21)
Continuar / reorientar / parar, com base em: receipt validável offline · integração
Git funcional · ≥2 agentes suportados · policy blocks demonstráveis · ≥3 design
partners · ≥1 piloto pago ou LOI · auditores consideram a evidência útil.

---

## Fase 4 — ProjectPilot integration  *(expansão)*

ProjectPilot torna-se o primeiro cliente de lifecycle. Transições relevantes
(validation→brief, planning→execution, execution→final-validation, →done) podem exigir
um WorkAttest receipt válido.

## Fase 5 — Taevdar integration  *(expansão)*

Taevdar torna-se control plane e experiência operacional (pending decisions,
executions, proofs, incidents, integrity, approvals, receipts). A proof interna do
Taevdar é progressivamente substituída por receipts WorkAttest.

## Fase 6 — GitHub App  *(expansão)*

Required status checks · PR receipts · organization policies · release receipts ·
identidade via GitHub/OIDC · evidence links · branch protection.

## Fase 7 — Enterprise control plane  *(expansão)*

SSO · RBAC · separation of duties · policy management · evidence retention · private
transparency service · SIEM · Jira/ServiceNow · on-premises · audit reports.

---

## Componentes open-source vs. comercial

| Open source (confiança) | Comercial (monetização) |
|---|---|
| receipt schema · verifier · canonicalization · signing interfaces · core domain · policy SDK · Git adapter · conformance suite | control plane · SSO/RBAC · policy management · evidence retention · integrations · private transparency log · reporting · multi-org · on-premises · compliance packs · incident forensics |

> Um produto de confiança não deve exigir confiança cega num formato fechado.
