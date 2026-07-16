# ACCOUNTABILITY MODEL — WorkAttest

> **Proof before acceptance.**

Define **o que significa "trabalho aceite"** em WorkAttest, que factos são provados,
com que força, e onde termina a responsabilidade do sistema. É o contrato conceptual
que o receipt materializa.

---

## 1. A unidade de accountability

A unidade **não** é o prompt, a conversa, a chamada ao modelo, a tool call isolada, o
log nem o agente. É o **trabalho aceite**:

```
Pedido autorizado
+ identidade do humano e do agente
+ permissões utilizadas
+ ações executadas
+ artefactos produzidos ou alterados
+ verificações independentes
+ exceções e riscos
+ aprovação autenticada
+ receipt assinado
= Verifiable Work Receipt
```

## 2. A cadeia de custódia (9 elos)

Cada elo tem de estar **ligado criptograficamente** ao seguinte para o trabalho contar
como aceite:

| # | Elo | Facto provado | Ligação criptográfica |
|---|---|---|---|
| 1 | Pedido | O trabalho começou com um `WorkRequest` identificável | `request_id`, hash do request |
| 2 | Identidade | Humano e agente são subjects verificáveis | chave pública / claims assinados |
| 3 | Autorização | Existia autoridade válida com âmbito e validade | `authorization.signature` |
| 4 | Ações | As ações relevantes foram registadas por fonte autorizada | hash chain de `ActionEvent` (`actions_root`) |
| 5 | Artefactos | Os artefactos estão identificados | `before_hash` / `after_hash` |
| 6 | Verificação | Os checks declarados correram de facto | `VerificationResult` + `definition_hash` + `output_hash` |
| 7 | Policy | A policy aplicada está identificada e versionada | `policy_id` + hash da policy |
| 8 | Aprovação | O responsável aceitou *exatamente* aquele resultado | `approval.result_hash` == resultado + assinatura |
| 9 | Receipt | O envelope final é íntegro e verificável offline | `receipt_hash` + `signatures` |

Quebrar qualquer elo → o trabalho **não** é aceite (fecha em `HOLD`/`REFUSE`).

## 3. Força probatória (o que o receipt prova / não prova)

| Prova (dentro do modelo de confiança) | **Não** prova |
|---|---|
| O trabalho começou com pedido identificável | Que o código não tem bugs |
| O subject possuía autorização válida, com âmbito e validade | Que uma análise está correta |
| As ações foram registadas por fonte autorizada | Que um documento é juridicamente perfeito |
| Os artefactos estão identificados por hash | Que o modelo nunca alucina |
| As verificações declaradas correram | Que os checks configurados são suficientes |
| O agente não escolheu os checks | Que a aprovação humana foi competente |
| A policy está identificada e versionada | Que a policy organizacional é adequada |
| A aprovação liga-se ao resultado exato | |
| A identidade do approver deriva de autenticação | |
| Alterações posteriores são detetáveis | |
| O receipt é validável sem confiar na app que o produziu | |

**Promessa correta (processual e probatória):**
> WorkAttest prova que o processo definido foi seguido e liga esse processo ao resultado aceite.

## 4. Decisões de accountability

A policy emite exatamente um de três estados terminais por avaliação:

- **ACCEPT** — autorização válida, artefactos identificados, todos os gates obrigatórios
  passaram, e (se exigido) o resultado foi aprovado.
- **HOLD** — falta evidência, aprovação, segregação de funções, ou um check obrigatório
  não foi executado. Estado recuperável mediante nova evidência/aprovação.
- **REFUSE** — ação proibida, identidade inválida, autorização expirada, policy violada,
  ou evidência incompatível com o artefacto. Um `REFUSE` **nunca** vira `ACCEPT` sem
  nova avaliação.

## 5. Segregação de funções

- O **agente** executa; **não** escolhe nem altera os checks que o verificam (elo 6).
- O **operador/organização** define os checks obrigatórios e a policy.
- O **approver humano** aceita o resultado; a sua identidade **deriva da autenticação**,
  não de um nome declarado. Uma pessoa **nunca** aprova a proof de outra execução.
- O **verifier independente** valida o receipt sem confiar na aplicação emissora.

## 6. Papéis (RACI simplificado do trabalho aceite)

| Papel | Responsabilidade no receipt |
|---|---|
| Owner (humano) | Cria o request; é o dono do trabalho |
| Agent (IA) | Executa dentro do âmbito autorizado |
| Policy | Classifica risco, exige evidência/aprovação, decide |
| Verifier | Corre e atesta os checks (independente do agente) |
| Approver | Aceita o resultado exato, com identidade autenticada |
| Issuer | Emite e assina o receipt canónico |
| Independent Verifier | Confirma tudo offline |

## 7. Ligações

- Invariantes que garantem estes factos: `docs/INVARIANTS.md`.
- Onde a confiança começa e acaba: `docs/TRUST-BOUNDARIES.md`.
- Ameaças a cada elo: `docs/THREAT-MODEL.md`.
- Estrutura do envelope: `schemas/work-receipt.schema.json`.
