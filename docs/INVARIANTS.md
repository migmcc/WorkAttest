# INVARIANTS — WorkAttest (v1)

> **Proof before acceptance.**

Invariantes do sistema: propriedades que têm de ser **sempre verdadeiras**. Cada uma é
testável e mapeia para ameaças (`docs/THREAT-MODEL.md`) e para factos de accountability
(`docs/ACCOUNTABILITY-MODEL.md`). Violá-las invalida o receipt.

Convenção de estados terminais da policy: `ACCEPT` / `HOLD` / `REFUSE`.

---

| ID | Invariante | Categoria | Como é testado |
|---|---|---|---|
| **INV-1** | Nenhuma execução existe sem `WorkRequest`. | Autoridade | Rejeitar `execution start` sem `request_id` válido |
| **INV-2** | Nenhuma execução começa sem subject e autorização válidos. | Identidade | Rejeitar start com subject/auth em falta ou inválidos |
| **INV-3** | Nenhuma ação de impacto é aceite fora do âmbito autorizado. | Autorização | Ação fora de `allowed_actions/resources` → HOLD/REFUSE |
| **INV-4** | Informação declarada pelo agente nunca é evidência verificada. | Integridade | Evidência só de fonte autorizada; declaração ≠ facto |
| **INV-5** | O agente nunca escolhe os checks que o verificam. | Segregação | Checks vêm da config do operador, não do request do agente |
| **INV-6** | Todo artefacto relevante possui hash antes e/ou depois. | Integridade | `ArtifactEvidence` exige `before_hash`/`after_hash` |
| **INV-7** | Todo `VerificationResult` identifica a definição exata do check. | Verificação | `definition_hash` presente e ligado ao check |
| **INV-8** | Ausência de checks obrigatórios nunca equivale a aprovação. | Fail-safe | Falta de check obrigatório → HOLD, nunca ACCEPT |
| **INV-9** | Um approval só pode aceitar o resultado da mesma execução. | Segregação | `approval.result_hash` == resultado da própria execução |
| **INV-10** | A identidade do approver deriva da autenticação. | Identidade | Approver = subject autenticado, nunca nome livre |
| **INV-11** | Ações e decisões são append-only. | Integridade | Sem update/delete; só append com hash chain |
| **INV-12** | Todo receipt é serializado de forma canónica. | Determinismo | Round-trip de canonicalização estável e reprodutível |
| **INV-13** | Todo receipt final é assinado. | Cripto | `signatures` não vazio; sign obrigatório na emissão |
| **INV-14** | Alterações ao receipt ou aos elementos abrangidos são detetáveis. | Integridade | Tamper de qualquer byte → verificação falha |
| **INV-15** | Todo receipt pode ser verificado externamente. | Independência | Verificação offline só com chave pública + schema |
| **INV-16** | Ações de risco elevado exigem approval humano. | Autoridade | `risk_class` elevado sem approval → HOLD |
| **INV-17** | Exceções são explícitas, justificadas e incluídas no receipt. | Transparência | Exceção sem justificação registada → inválida |
| **INV-18** | Um `REFUSE` nunca vira `ACCEPT` sem nova avaliação. | Estado | Transição REFUSE→ACCEPT exige reavaliação registada |
| **INV-19** | Conteúdo sensível nunca é incluído automaticamente na evidência. | Privacidade | Default = hash+ref/classificação; inclusão é explícita |
| **INV-20** | Falhas de identidade, policy, assinatura ou verificação fecham em segurança. | Fail-safe | Qualquer falha nestes eixos → HOLD/REFUSE, nunca ACCEPT |

---

## Estratégia de teste

- **Unit tests** — cada invariante tem pelo menos um teste positivo e um negativo.
- **Property-based tests** — determinismo (INV-12) e hash chain (INV-11) validados com
  inputs gerados.
- **Testes adversariais** — INV-4/5/8/9/14/18/20 mapeiam diretamente para T-1…T-12 em
  `docs/THREAT-MODEL.md`.
- **Conformance suite** — verifica que qualquer implementação do verifier respeita
  INV-12…INV-15.

> Regra de ouro: se um invariante não tem um teste que falha quando ele é violado, o
> invariante ainda não existe.
