# THREAT MODEL — WorkAttest

> **Proof before acceptance.**

Modelo de ameaças do MVP. Estrutura: adversários → ativos → ameaças por elo da cadeia
→ mitigações → testes adversariais que as validam. Enquadramento STRIDE onde aplicável.

---

## 1. Adversários considerados

| Adversário | Motivação | Capacidade assumida |
|---|---|---|
| **Agente desonesto/comprometido** | Fazer aceitar trabalho fora do âmbito | Controla a sua própria narrativa; **não** controla os checks nem as chaves |
| **Insider** (dev/approver) | Aprovar/forjar aceitação indevida | Autenticado; limitado por segregação de funções |
| **Man-in-the-middle / tamper pós-facto** | Alterar evidência ou receipt após emissão | Acesso ao ficheiro de receipt/evidência |
| **Verifier evasion** | Fazer passar sem correr checks obrigatórios | Pode tentar escolher/omitir checks |
| **Replay / cross-execution** | Reutilizar aprovação/prova de outra execução | Acesso a receipts anteriores |
| **Key compromise** | Assinar receipts forjados | Obtém a chave privada (fora do âmbito de defesa criptográfica — ver limites) |

**Fora de âmbito (MVP):** ataques ao hardware/HSM, cadeia de fornecimento das
dependências, ataques ao próprio modelo de IA, e coação física de um approver.

## 2. Ativos a proteger

Signing keys · receipts · evidência (diffs, hashes, outputs) · definições de policy e
checks · registos de aprovação · a **ligação** entre todos eles.

## 3. Ameaças por elo (STRIDE) e mitigações

| Elo / superfície | Ameaça (STRIDE) | Mitigação | Invariante |
|---|---|---|---|
| Identidade | **S**poofing — nome no request body | Identidade deriva de chave/claim assinado, nunca de string livre | INV-2, INV-10 |
| Autorização | **E**levation — agir fora do âmbito | Ações validadas contra `allowed_actions/resources`; fora do âmbito → REFUSE | INV-3 |
| Ações | **R**epudiation / **T**ampering — negar ou alterar o que foi feito | Append-only + hash chain (`previous_event_hash`); fonte autorizada, não o agente | INV-4, INV-11 |
| Evidência do agente | **T**ampering — declarar falso | Info declarada nunca é evidência verificada; confirmação do sistema afetado | INV-4 |
| Artefactos | **T**ampering — trocar o artefacto | `before_hash`/`after_hash`; receipt liga-se ao hash exato | INV-6, INV-14 |
| Verificação | **V**erifier evasion — o agente escolhe/omite checks | Checks definidos pelo operador; agente não os escolhe; ausência ≠ aprovação | INV-5, INV-7, INV-8 |
| Policy | **T**ampering — trocar a policy silenciosamente | Policy versionada, hashable, incluída/referenciada no receipt | INV-7 |
| Aprovação | **E**levation / **cross-execution** — aprovar prova de outra execução | Approval liga-se ao `result_hash` da **mesma** execução; identidade autenticada | INV-9, INV-10 |
| Receipt | **T**ampering pós-facto | Serialização canónica + assinatura; alterações detetáveis | INV-12, INV-13, INV-14 |
| Verificação externa | **I**nformation / dependência do servidor | Verificação offline só com chave pública + schema | INV-15 |
| Confidencialidade | **I**nformation disclosure — leak de dados sensíveis na evidência | Conteúdo sensível nunca automático; hash+ref, classificação, redaction, encryption | INV-19 |
| Decisão | **D**oS / degradação → aceitação insegura | Fail-safe: falhas fecham em HOLD/REFUSE, nunca ACCEPT | INV-20 |
| Estado terminal | Reabrir REFUSE como ACCEPT | REFUSE só muda com nova avaliação | INV-18 |

## 4. Testes adversariais (obrigatórios no MVP)

Cada mitigação tem de ter um teste que **falha o receipt** quando o ataque é tentado:

- [ ] **T-1** Alterar um byte do receipt após assinatura → verificação falha.
- [ ] **T-2** Alterar um artefacto após `after_hash` → mismatch detetado.
- [ ] **T-3** Remover/adulterar um `ActionEvent` no meio da chain → hash chain quebra.
- [ ] **T-4** Agente tenta declarar um check como "passado" sem o correr → não conta.
- [ ] **T-5** Omitir um check obrigatório → decisão HOLD, nunca ACCEPT.
- [ ] **T-6** Aplicar a aprovação da execução A ao resultado da execução B → rejeitado (cross-execution).
- [ ] **T-7** Autorização expirada → REFUSE.
- [ ] **T-8** Ação fora dos diretórios autorizados → HOLD/REFUSE.
- [ ] **T-9** Substituir a policy por outra sem atualizar o hash → detetado.
- [ ] **T-10** Aprovar com identidade não autenticada / nome livre → rejeitado.
- [ ] **T-11** Verificar receipt sem acesso ao servidor → sucesso (offline).
- [ ] **T-12** Reabrir um REFUSE como ACCEPT sem reavaliar → bloqueado.

## 5. Riscos residuais aceites (MVP)

- **Key compromise** — se a chave privada for exfiltrada, receipts forjados tornam-se
  possíveis. Mitigação parcial: rotação, escopo curto; evolução: HSM/KMS/keyless. Documentado.
- **Timestamp fraco** — relógio local não é prova de tempo forte. Evolução: TSA/transparency log.
- **Integridade do host observador** — assume-se ambiente de observação íntegro.

## 6. Ligações

- Fronteiras e âncoras de confiança: `docs/TRUST-BOUNDARIES.md`.
- Invariantes referenciados (INV-*): `docs/INVARIANTS.md`.
- Factos provados/limites: `docs/ACCOUNTABILITY-MODEL.md`.
