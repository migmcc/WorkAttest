# PROJECT BRIEF — WorkAttest

> **Proof before acceptance.**

| | |
|---|---|
| **Projeto** | WorkAttest (`workattest`) |
| **Categoria** | Verifiable Work Accountability |
| **Primeiro mercado** | Alterações de software produzidas ou assistidas por agentes de IA |
| **Estado** | Brief — validação APROVADA (condicional) |
| **Fonte** | `ideia-workattest.md` (documento de discovery completo) |

---

## 1. Problema

Agentes como Claude Code, Codex e Cursor produzem código, decisões e ações a alta
velocidade. Logs, traces e históricos de chat ajudam a reconstruir o que aconteceu,
mas **não constituem uma cadeia de custódia verificável nem uma aceitação formal do
resultado**. Na maioria dos fluxos atuais continua difícil provar quem iniciou o
trabalho, que autoridade existia, que ações e artefactos resultaram, que verificações
correram de facto, e quem aprovou o resultado *exato*.

## 2. Tese

A unidade de accountability não é o prompt, a conversa, a tool call, o log nem o
agente — é o **trabalho aceite**. Um trabalho aceite liga criptograficamente:

```
pedido autorizado + identidade (humano+agente) + permissões usadas
+ ações executadas + artefactos alterados + verificações independentes
+ exceções/riscos + aprovação autenticada + receipt assinado
= Verifiable Work Receipt
```

A promessa é **processual e probatória**, não de correção:

> WorkAttest prova que o processo definido foi seguido e liga esse processo ao
> resultado aceite. Não garante que o código não tem bugs, que um modelo nunca
> alucina, nem que uma aprovação humana foi competente.

Esta honestidade de âmbito é deliberada e é o que torna o receipt defensável perante
auditores e juristas.

## 3. Primeiro wedge — AI Software Change Accountability

Controlar o ciclo de uma alteração de software assistida por IA, demonstrável num PR:

`WorkRequest` → identidade + policy → autorização (`ACCEPT/HOLD/REFUSE`) →
execução observada → snapshots Git + ações → Verifier (checks do operador) →
aprovação humana autenticada (risco elevado) → **Verifiable Work Receipt assinado** →
verificação independente offline → status check em GitHub/GitLab.

## 4. Cliente-alvo (ICP inicial)

Equipas de engenharia de 20–300 pessoas que já usam coding agents, produzem software
com impacto financeiro/operacional/regulatório, têm CI + PRs + aprovações, e precisam
de **demonstrar** como uma alteração foi produzida e aceite — sem substituir GitHub,
GitLab, Jira ou os agentes existentes. Setores prioritários: fintech, banca, seguros,
health-tech, automotive, industrial, legal-tech, cibersegurança, B2B regulado.

## 5. Diferenciação

WorkAttest **não** é editor, agente, framework de agentes, observabilidade, SIEM, GRC
genérico, gestor de projetos ou IAM. É uma **camada neutra** entre estes sistemas.

Outras ferramentas provam que um agente chamou uma tool, que um utilizador iniciou
sessão, que uma policy permitiu uma ação, ou que um commit passou no CI. WorkAttest
prova **adicionalmente** que o commit corresponde ao pedido autorizado, que os
artefactos concretos estão identificados, que os checks aplicáveis correram, que a
evidência pertence àquela versão, que nenhuma obrigação foi omitida, e que a pessoa
responsável aceitou *exatamente* aquele resultado — verificável fora do WorkAttest.

## 6. Estratégia técnica

- **Core determinístico e independente de infraestrutura** (sem dependência de FastAPI,
  GitHub, Claude, Codex ou DB específica): entidades, estados, invariantes, decisões,
  serialização canónica.
- **Standards-first** — evitar cripto proprietária: in-toto, DSSE, Sigstore/Rekor,
  SCITT, OIDC, SPIFFE/SPIRE, SLSA, SBOM, Git signing, GitHub attestations.
- **Reuso disciplinado** — ProjectPilot, Taevdar e Agent Trust Gate como clientes /
  doadores de componentes, **não** como núcleo. Não herdar o anti-padrão "estado JSON
  editável como prova final".

## 7. MVP — âmbito

**Objetivo:** demonstrar que uma alteração de software pode ser autorizada, observada,
verificada, aprovada e transformada num receipt validável **offline**.

**Inclui:** receipt schema v1 · assinaturas Ed25519 · Git adapter · filesystem
evidence · policy determinística com `ACCEPT/HOLD/REFUSE` · verifier independente ·
approval ligado ao execution ID · verificação offline · testes adversariais (tamper) ·
threat model documentado · demo Claude/Codex → Git → receipt.

**CLI mínima:** `workattest init | request create | policy evaluate | execution
start/observe | evidence add | verify run | approve | receipt issue | receipt verify`.

**Fora do MVP:** dashboard/PWA · multi-tenant SaaS · billing · GitHub App completa ·
compliance EU AI Act/ISO extensivo · SIEM/ServiceNow · blockchain própria · custom LLM
· agent framework. *O MVP prova o modelo de accountability, não a amplitude da plataforma.*

## 8. Invariantes-chave (v1)

Nenhuma execução sem `WorkRequest` e autorização válida · info declarada pelo agente
nunca é evidência verificada · o agente nunca escolhe os checks que o verificam ·
ausência de checks obrigatórios ≠ aprovação · um approval só aceita o resultado da
mesma execução · ações e decisões são append-only · todo receipt é canónico, assinado
e verificável externamente · alterações à evidência são detetáveis · falhas de
identidade/policy/assinatura/verificação fecham em segurança. *(Lista completa: §10 da ideia.)*

## 9. Critérios de sucesso (MVP)

Uma pessoa externa, recebendo artefacto + receipt + chave/cadeia de identidade +
referências de evidência, confirma independentemente: (1) era o trabalho autorizado;
(2) aquela execução produziu o artefacto; (3) os checks aplicáveis correram; (4) o
resultado corresponde aos hashes; (5) o responsável aprovou exatamente aquele
resultado; (6) o receipt não foi alterado.

**Métrica principal:** *Accepted work receipts por equipa por semana* (só conta com
artefacto final, checks corridos, policy avaliada, aprovação obtida e assinatura válida).
**Guardrails a zero:** proof mismatch cross-execution, unsigned final receipts,
unauthorized impact aceite, mandatory checks saltados, falhas de integridade não detetadas.

## 10. Riscos e critérios de paragem

| Risco | Severidade | Mitigação |
|---|---|---|
| **Willingness-to-pay não provada** | **Existencial** | Vender redução de risco; demonstrar reconstrução de incidente; design partners com dor concreta |
| Categoria demasiado ampla / custo de educação | Alto | Começar só por software changes; demo num PR; evitar claims de "AI governance" |
| Standards/vendors (GitHub Attestations, Sigstore, SLSA) invadem a lane | Alto | Integrar standards, não competir; diferenciar no *trabalho aceite* + aprovação humana ligada ao artefacto exato |
| Execution Gateway (observar sem confiar no agente) é a peça mais difícil/intrusiva | Médio-Alto | MVP limita-se a snapshots Git + comandos observados; evitar scope creep |
| Receipt sem valor jurídico/de auditoria | Médio | Envolver auditores/juristas cedo; documentar limites; evidence mapping |
| Logging cria novos riscos | Médio | Minimização, redaction, encryption, evidence references, retenção configurável |

**Parar se:** não existe willingness to pay · receipts não alteram decisões de
procurement/audit/release · integrações necessárias tornam o produto inviável ·
concorrentes oferecem fluxo completo e acessível antes da validação.

## 11. Roadmap (macro)

Fase 0 Discovery/contratos → Fase 1 Core determinístico → Fase 2 Cryptographic
receipts → Fase 3 Software change adapter (Git) → Fase 4 ProjectPilot integration →
Fase 5 Taevdar control plane → Fase 6 GitHub App → Fase 7 Enterprise control plane.

## 12. Decisão de validação (registada)

**APROVADO (condicional)** — fonte: manual, via ProjectPilot.

Tese sólida (unidade de accountability = trabalho aceite); MVP tecnicamente viável e
bem delimitado; âmbito honesto (processual/probatório, não correção). **O risco
dominante é de mercado, não de construção.**

**Condição vinculativa:** executar as entrevistas de validação de mercado (§19 da
ideia) **em paralelo** com a Fase 0/1, e tratar *willingness-to-pay* como o critério
de paragem primário (§21). Esta aprovação cobre **construir o core do MVP + validar a
procura** — não construir a plataforma enterprise completa.

## 13. Próxima sequência de trabalho

1. Avançar no lifecycle ProjectPilot (setup-advice → execução).
2. Produzir os contratos da Fase 0: `ACCOUNTABILITY-MODEL.md`, `THREAT-MODEL.md`,
   `TRUST-BOUNDARIES.md`, `INVARIANTS.md`, `RECEIPT-SCHEMA.json`,
   `COMPETITIVE-MATRIX.md`, `STANDARDS-DECISIONS.md`.
3. Iniciar as entrevistas de mercado (§19) em paralelo.
4. Gate da Fase 0: modelo de confiança revisto · receipt v1 aprovado · primeiro caso
   de uso fechado · zero claims de "garantia absoluta".
