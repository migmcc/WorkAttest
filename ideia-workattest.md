# WorkAttest

> **Proof before acceptance.**

## Estado

- **Tipo:** novo projeto independente
- **Estado inicial:** ideia / discovery
- **Nome de trabalho:** WorkAttest
- **Categoria proposta:** Verifiable Work Accountability
- **Primeiro mercado:** alterações de software produzidas ou assistidas por agentes de IA
- **Estratégia técnica:** core novo, reutilização seletiva de componentes comprovados
- **Relação com projetos existentes:** ProjectPilot, Taevdar e Agent Trust Gate serão clientes, integrações ou doadores de componentes — não o núcleo do novo produto

---

## 1. Resumo executivo

WorkAttest é uma infraestrutura local-first e verificável para garantir que trabalho produzido com assistência de IA só é aceite depois de existir uma cadeia completa de:

1. pedido de trabalho;
2. identidade;
3. autorização;
4. ações observadas;
5. artefactos identificados;
6. verificação independente;
7. decisão humana autenticada;
8. receipt assinado;
9. verificação externa.

O produto não pretende garantir que uma IA nunca erra.

Pretende garantir que nenhum trabalho relevante é aceite sem autoridade, evidência, validação e responsabilidade identificável.

### Proposta em uma frase

> WorkAttest transforma trabalho assistido por IA em trabalho formalmente autorizado, verificado, aceite e demonstrável.

### Problema central

Ferramentas como Claude Code, Codex, Cursor e agentes empresariais conseguem produzir código, documentos, decisões e ações com grande velocidade. Contudo, na maioria dos fluxos atuais continua a ser difícil provar:

- quem iniciou o trabalho;
- que agente e modelo foram utilizados;
- que permissões foram concedidas;
- que ações foram executadas;
- que artefactos foram alterados;
- que verificações correram realmente;
- que políticas estavam em vigor;
- quem aprovou o resultado exato;
- se a evidência foi alterada posteriormente.

Logs, traces e históricos de chat ajudam a reconstruir acontecimentos, mas não constituem necessariamente uma cadeia de custódia verificável nem uma aceitação formal do resultado.

---

## 2. Tese do produto

A unidade de accountability não deve ser:

- o prompt;
- a conversa;
- a chamada ao modelo;
- a tool call isolada;
- o log;
- o agente.

A unidade principal deve ser o **trabalho aceite**.

Um trabalho aceite é composto por:

```text
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

A diferenciação de WorkAttest não será apenas bloquear tool calls ou produzir audit logs.

Será ligar criptograficamente o pedido, a autoridade, a execução, a evidência, a verificação e a aceitação ao artefacto exato que entrou em produção ou foi entregue.

---

## 3. O que WorkAttest garante

WorkAttest deverá conseguir garantir, dentro do modelo de confiança documentado, que:

- o trabalho começou com um pedido identificável;
- o sujeito que atuou possuía uma autorização válida;
- a autorização tinha âmbito, limites e validade definidos;
- as ações relevantes foram registadas por uma fonte autorizada;
- os artefactos estão identificados através de hashes;
- as verificações declaradas foram efetivamente executadas;
- o agente não escolheu nem alterou os checks que o verificaram;
- a policy utilizada está identificada e versionada;
- a aprovação está ligada ao resultado exato;
- a identidade do aprovador deriva da autenticação;
- o receipt foi assinado;
- alterações posteriores à evidência são detetáveis;
- o receipt pode ser validado sem confiar na aplicação que o produziu.

## 4. O que WorkAttest não garante

WorkAttest não poderá afirmar que:

- o código nunca contém bugs;
- uma análise está sempre correta;
- um documento está juridicamente perfeito;
- um modelo nunca alucina;
- os checks configurados são suficientes para todos os riscos;
- uma aprovação humana foi intelectualmente competente;
- uma política organizacional é adequada apenas porque foi executada.

A promessa correta é processual e probatória:

> WorkAttest prova que o processo definido foi seguido e liga esse processo ao resultado aceite.

---

## 5. Clientes e utilizadores

### 5.1 Compradores empresariais

- CTO;
- CISO;
- Head of Engineering;
- Head of AI Platform;
- Responsible AI Lead;
- Internal Audit;
- Risk and Compliance;
- Quality Director;
- fornecedores de software para setores regulados;
- empresas com utilização intensiva de coding agents.

### 5.2 Utilizadores

- programadores;
- engineering managers;
- security engineers;
- quality engineers;
- release managers;
- auditores;
- approvers empresariais;
- operadores de agentes;
- equipas de plataforma.

### 5.3 Primeiro Ideal Customer Profile

Equipas de engenharia entre 20 e 300 pessoas que:

- já utilizam Claude Code, Codex, Cursor ou agentes equivalentes;
- desenvolvem software com impacto financeiro, operacional ou regulatório;
- possuem CI, pull requests e processos de aprovação;
- precisam de demonstrar como uma alteração foi produzida e aceite;
- não querem substituir GitHub, GitLab, Jira ou os agentes existentes.

Setores prioritários:

- fintech;
- banca;
- seguros;
- health-tech;
- automotive;
- industrial;
- legal-tech;
- cibersegurança;
- software B2B com clientes regulados.

---

## 6. Primeiro wedge comercial

### AI Software Change Accountability

O primeiro produto deverá controlar o ciclo de uma alteração de software produzida ou assistida por IA.

### Fluxo inicial

1. Um humano ou sistema cria um `WorkRequest`.
2. WorkAttest identifica o proprietário e o agente.
3. A policy avalia o risco e emite uma autorização.
4. A execução ocorre num workspace observado.
5. O gateway regista ações relevantes.
6. Git identifica o estado inicial e final.
7. O Verifier executa checks definidos pelo operador.
8. A policy produz `ACCEPT`, `HOLD` ou `REFUSE`.
9. Ações de risco elevado exigem aprovação humana autenticada.
10. É emitido um `Verifiable Work Receipt`.
11. Um verificador independente valida o receipt.
12. GitHub ou GitLab recebe um status check ligado ao receipt.

### Exemplo de decisão

```text
ACCEPT — autorização válida, artefactos identificados,
todos os gates obrigatórios passaram e o resultado foi aprovado.

HOLD — faltam evidências, aprovação, segregação de funções
ou um check obrigatório não foi executado.

REFUSE — ação proibida, identidade inválida, autorização expirada,
policy violada ou evidência incompatível com o artefacto.
```

---

## 7. Diferenciação

WorkAttest não deverá competir como:

- editor de código;
- agente de programação;
- framework de agentes;
- plataforma de observabilidade;
- SIEM;
- GRC genérico;
- gestor de projetos;
- ferramenta de testes;
- solução de autenticação.

WorkAttest deverá funcionar como uma camada neutral entre estes sistemas.

### Diferença principal

Outras ferramentas podem provar que:

- um agente chamou uma ferramenta;
- um utilizador iniciou uma sessão;
- uma policy permitiu uma ação;
- um commit passou no CI.

WorkAttest deverá provar adicionalmente que:

- o commit corresponde ao pedido autorizado;
- os artefactos concretos estão identificados;
- os checks aplicáveis foram executados;
- a evidência pertence àquela versão;
- nenhuma obrigação foi omitida;
- a pessoa responsável aceitou exatamente aquele resultado;
- o receipt continua verificável fora do WorkAttest.

---

## 8. Arquitetura de alto nível

```text
ProjectPilot / Jira / GitHub / API
                |
                v
          Work Request
                |
                v
     Identity + Policy Engine
                |
       ACCEPT / HOLD / REFUSE
                |
                v
        Execution Gateway
                |
     Claude / Codex / Humanos
                |
                v
 Git / Filesystem / Cloud / APIs
                |
                v
 Evidence Collector + Verifier
                |
                v
    Human Approval, quando exigida
                |
                v
      Verifiable Work Receipt
                |
                v
 Independent Verifier / Transparency Log
```

### 8.1 Core Domain

Responsável por:

- entidades;
- estados;
- invariantes;
- decisões;
- transições;
- erros;
- serialização canónica.

O domínio não deverá depender de:

- FastAPI;
- GitHub;
- Claude;
- Codex;
- bases de dados específicas;
- interfaces gráficas.

### 8.2 Identity

Representa sujeitos verificáveis:

- humano;
- agente;
- service account;
- workload;
- ferramenta;
- organização.

A identidade nunca deverá ser apenas um nome recebido no request body.

O primeiro MVP pode utilizar:

- chaves locais Ed25519;
- identidade Git;
- identidade GitHub;
- OIDC em CI.

Evoluções empresariais:

- SSO;
- SPIFFE/SPIRE;
- certificados;
- workload identity;
- service accounts;
- segregação de funções.

### 8.3 Policy Engine

Responsável por:

- classificar o pedido;
- avaliar risco;
- determinar permissões;
- exigir evidência;
- definir checks;
- exigir aprovação;
- emitir `ACCEPT`, `HOLD` ou `REFUSE`.

A policy deve ser:

- versionada;
- determinística;
- hashable;
- testável;
- independente do agente;
- incluída ou referenciada no receipt.

### 8.4 Authorization

Uma autorização deve definir:

- subject;
- trabalho autorizado;
- recursos;
- operações;
- limites;
- risco;
- policy;
- validade;
- condições;
- necessidade de approval;
- revogação.

Nenhuma ação de impacto deve ser aceite sem autorização válida.

### 8.5 Execution Gateway

Responsável por observar ou mediar ações como:

- comandos;
- alterações de ficheiros;
- chamadas a APIs;
- commits;
- mudanças de infraestrutura;
- deploys;
- comunicações externas;
- operações sobre dados.

O gateway não deve depender do relato do agente.

Sempre que possível, deverá obter confirmação do sistema afetado.

### 8.6 Evidence Store

Armazena ou referencia:

- artefactos;
- diffs;
- logs;
- resultados de testes;
- relatórios;
- hashes;
- configurações;
- versões;
- approvals;
- attestations externas.

O receipt não precisa de conter todo o conteúdo sensível.

Pode conter:

- hash;
- media type;
- tamanho;
- localização;
- política de retenção;
- classificação;
- envelope encriptado.

### 8.7 Verifier

Executa checks definidos pelo operador ou pela organização.

Cada resultado deverá conter:

- ID do check;
- nome;
- versão;
- definição ou hash da definição;
- implementação;
- comando, quando aplicável;
- ferramenta e versão;
- início e fim;
- duração;
- exit code;
- estado;
- hash do output;
- referências para artefactos de evidência;
- ambiente relevante;
- motivo de falha.

O agente nunca deve escolher os checks que o verificam.

### 8.8 Approval

Uma aprovação deverá conter:

- identidade autenticada;
- função;
- decisão;
- justificação;
- timestamp;
- receipt ou execution ID;
- hash do resultado aceite;
- assinatura;
- policy que exigiu a aprovação.

A aprovação deve ser append-only.

Uma pessoa nunca poderá aprovar uma proof pertencente a outra execução.

### 8.9 Receipt Issuer

Produz o envelope final assinado.

Requisitos:

- serialização canónica;
- schema versionado;
- assinatura digital;
- chain ou parent receipts;
- suporte para múltiplas signatures;
- possibilidade de redaction;
- exportação;
- verificação offline.

### 8.10 Independent Receipt Verifier

Comando inicial:

```bash
workattest verify receipt.json
```

Deverá validar:

- schema;
- assinatura;
- signatário;
- validade;
- hashes;
- artefactos disponíveis;
- policy;
- relação com a execução;
- approvals;
- cadeia;
- transparency proof, quando disponível.

A verificação não deverá exigir acesso ao servidor principal.

---

## 9. Modelo de domínio inicial

### WorkRequest

- `id`
- `title`
- `intent`
- `scope`
- `owner_subject`
- `system`
- `risk_class`
- `constraints`
- `acceptance_criteria`
- `created_at`

### Subject

- `id`
- `type`
- `issuer`
- `claims`
- `public_key`
- `status`

### Authorization

- `id`
- `request_id`
- `subject_id`
- `policy_id`
- `allowed_actions`
- `allowed_resources`
- `conditions`
- `issued_at`
- `expires_at`
- `revoked_at`
- `signature`

### ExecutionSession

- `id`
- `request_id`
- `authorization_id`
- `agent_subject_id`
- `human_owner_id`
- `model`
- `configuration_hash`
- `workspace`
- `started_at`
- `ended_at`
- `status`

### ActionEvent

- `id`
- `execution_id`
- `sequence`
- `action_type`
- `resource`
- `parameters_hash`
- `result_hash`
- `observed_by`
- `occurred_at`
- `previous_event_hash`
- `signature`

### ArtifactEvidence

- `id`
- `execution_id`
- `path_or_uri`
- `media_type`
- `before_hash`
- `after_hash`
- `size`
- `source`
- `classification`
- `evidence_uri`

### VerificationResult

- `id`
- `execution_id`
- `check_id`
- `check_version`
- `definition_hash`
- `status`
- `exit_code`
- `started_at`
- `ended_at`
- `output_hash`
- `evidence_refs`

### ApprovalDecision

- `id`
- `execution_id`
- `approver_subject_id`
- `decision`
- `justification`
- `result_hash`
- `policy_id`
- `decided_at`
- `signature`

### WorkReceipt

- `schema_version`
- `receipt_id`
- `request`
- `subjects`
- `authorization`
- `execution`
- `actions_root`
- `artifacts`
- `verification`
- `approvals`
- `policy`
- `issued_at`
- `issuer`
- `previous_receipt_hash`
- `receipt_hash`
- `signatures`
- `transparency_receipt`

---

## 10. Invariantes v1

1. Nenhuma execução existe sem `WorkRequest`.
2. Nenhuma execução começa sem subject e autorização válidos.
3. Nenhuma ação de impacto é aceite fora do âmbito autorizado.
4. Informação declarada pelo agente nunca é tratada como evidência verificada.
5. O agente nunca escolhe os checks que o verificam.
6. Todo artefacto relevante possui hash antes e/ou depois.
7. Todo resultado de verificação identifica a definição exata do check.
8. Ausência de checks obrigatórios nunca equivale a aprovação.
9. Um approval só pode aceitar o resultado da mesma execução.
10. A identidade do approver deriva da autenticação.
11. Ações e decisões são append-only.
12. Todo receipt é serializado de forma canónica.
13. Todo receipt final é assinado.
14. Alterações ao receipt ou aos elementos abrangidos são detetáveis.
15. Todo receipt pode ser verificado externamente.
16. Ações de risco elevado exigem approval humano.
17. Exceções são explícitas, justificadas e incluídas no receipt.
18. Um `REFUSE` nunca pode ser transformado em `ACCEPT` sem nova avaliação.
19. O conteúdo sensível nunca é incluído automaticamente na evidência.
20. Falhas de identidade, policy, assinatura ou verificação fecham em segurança.

---

## 11. Standards e compatibilidade

WorkAttest deverá evitar protocolos criptográficos proprietários quando já existem standards adequados.

Compatibilidades a avaliar:

- in-toto attestations;
- DSSE;
- Sigstore;
- Rekor ou transparency service privado;
- SCITT;
- OIDC;
- SPIFFE/SPIRE;
- OpenTelemetry;
- SBOMs CycloneDX e SPDX;
- SLSA;
- Git signing;
- GitHub attestations;
- MCP e protocolos de agentes;
- Open Agent Passport ou protocolos equivalentes.

Princípio:

> WorkAttest deve ligar standards existentes num modelo de aceitação do trabalho, não reinventar cada componente.

---

## 12. MVP técnico

### Objetivo

Demonstrar que uma alteração de software pode ser autorizada, observada, verificada, aprovada e transformada num receipt validável offline.

### Interface inicial

```bash
workattest init
workattest request create
workattest policy evaluate
workattest execution start
workattest execution observe
workattest evidence add
workattest verify run
workattest approve
workattest receipt issue
workattest receipt verify
```

### Cenário de demonstração

1. Repositório Git limpo.
2. Pedido: corrigir um bug específico.
3. Policy permite alterações apenas em determinados diretórios.
4. Codex ou Claude Code executa o trabalho.
5. WorkAttest recolhe:
   - commit inicial;
   - diff;
   - ficheiros;
   - comandos observados;
   - commit final.
6. Verifier executa:
   - testes;
   - lint;
   - typecheck;
   - security check;
   - check personalizado.
7. Uma alteração fora do scope produz `HOLD` ou `REFUSE`.
8. Um humano autenticado aprova o commit final.
9. WorkAttest emite um receipt assinado.
10. Outro computador valida o receipt com a chave pública.

### Critérios de conclusão do MVP

- receipt schema v1 publicado;
- assinaturas Ed25519;
- Git adapter;
- filesystem evidence;
- policy determinística;
- `ACCEPT/HOLD/REFUSE`;
- verifier independente;
- approval ligado ao execution ID;
- receipt verificável offline;
- testes adversariais;
- documentação do threat model;
- demo completa Claude/Codex → Git → receipt.

---

## 13. Fora do MVP

Não incluir inicialmente:

- dashboard empresarial;
- PWA;
- routing de modelos;
- memória;
- gestão de quotas;
- multi-tenant SaaS;
- billing;
- integrations marketplace;
- compliance completo com EU AI Act;
- mapeamento extensivo ISO;
- SIEM;
- ServiceNow;
- GitHub App completa;
- blockchain própria;
- custom LLM;
- autonomous agent framework.

O MVP deve provar o modelo de accountability, não a amplitude da plataforma.

---

## 14. Roadmap

### Fase 0 — Discovery e contratos

Entregáveis:

- `PRODUCT-BRIEF.md`
- `ACCOUNTABILITY-MODEL.md`
- `THREAT-MODEL.md`
- `TRUST-BOUNDARIES.md`
- `INVARIANTS.md`
- `RECEIPT-SCHEMA.json`
- `COMPETITIVE-MATRIX.md`
- `STANDARDS-DECISIONS.md`

Gate:

- modelo de confiança revisto;
- receipt v1 aprovado;
- primeiro caso de uso fechado;
- não existem claims de “garantia absoluta”.

### Fase 1 — Core determinístico

- entidades;
- estados;
- canonical JSON;
- policy decisions;
- storage interfaces;
- append-only events;
- unit tests;
- property-based tests;
- CLI mínima.

### Fase 2 — Cryptographic receipts

- keys;
- signing;
- verification;
- key rotation model;
- receipt chains;
- redaction;
- offline verifier;
- adversarial tamper tests.

### Fase 3 — Software change adapter

- Git snapshots;
- diffs;
- artifact hashes;
- command observation;
- verifier;
- approval;
- complete demo.

### Fase 4 — ProjectPilot integration

ProjectPilot torna-se o primeiro cliente de lifecycle.

Gates:

- validation → brief;
- planning → execution;
- execution → final-validation;
- final-validation → done.

Cada transição importante pode exigir um WorkAttest receipt válido.

### Fase 5 — Taevdar integration

Taevdar torna-se control plane e experiência operacional:

- pending decisions;
- executions;
- proofs;
- incidents;
- integrity;
- approvals;
- receipts.

A proof interna do Taevdar é progressivamente substituída por receipts WorkAttest.

### Fase 6 — GitHub App

- required status checks;
- PR receipts;
- organization policies;
- release receipts;
- identity via GitHub/OIDC;
- evidence links;
- branch protection integration.

### Fase 7 — Enterprise control plane

- SSO;
- RBAC;
- separation of duties;
- policy management;
- evidence retention;
- private transparency service;
- SIEM;
- Jira/ServiceNow;
- on-premises;
- audit reports.

---

## 15. Relação com projetos existentes

### ProjectPilot

Mantém-se como lifecycle orchestrator.

Reutilizar:

- arquitetura modular;
- determinismo;
- escrita atómica;
- hashes de artefactos;
- gates;
- adaptação de lifecycle.

Não reutilizar como core:

- estado JSON como autoridade;
- approvals declarativos;
- inventário editável como prova final.

### Taevdar

Torna-se control plane e cliente de execução.

Reutilizar ou portar:

- máquina de estados;
- Verifier;
- CheckResult;
- environment allowlist;
- project checks;
- escalations;
- checkpoints;
- workspace abstractions;
- testes de invariantes;
- fail-safe sem checks.

Reescrever:

- ProofRepository;
- proof schema;
- approvals;
- identity;
- hash chain;
- multi-tenant separation;
- sign-off API;
- trust model.

### Agent Trust Gate

Torna-se fornecedor de policy modules.

Reutilizar:

- `ACCEPT/HOLD/REFUSE`;
- findings;
- scoring;
- policy hashes;
- reports;
- módulos de GitHub Actions;
- exit codes.

Evoluir:

- receipts atuais para evidence statements ou policy decision records consumidos pelo WorkAttest.

---

## 16. Estrutura inicial do repositório

```text
workattest/
├── pyproject.toml
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── ideia.md
├── docs/
│   ├── PRODUCT-BRIEF.md
│   ├── ACCOUNTABILITY-MODEL.md
│   ├── THREAT-MODEL.md
│   ├── TRUST-BOUNDARIES.md
│   ├── INVARIANTS.md
│   ├── COMPETITIVE-MATRIX.md
│   └── STANDARDS-DECISIONS.md
├── schemas/
│   ├── work-request.schema.json
│   ├── authorization.schema.json
│   ├── action-event.schema.json
│   ├── verification-result.schema.json
│   └── work-receipt.schema.json
├── src/
│   └── workattest/
│       ├── domain/
│       ├── identity/
│       ├── policy/
│       ├── authorization/
│       ├── execution/
│       ├── evidence/
│       ├── verification/
│       ├── approval/
│       ├── receipts/
│       ├── crypto/
│       ├── storage/
│       ├── adapters/
│       │   ├── git/
│       │   ├── filesystem/
│       │   ├── projectpilot/
│       │   └── taevdar/
│       └── cli/
└── tests/
    ├── unit/
    ├── integration/
    ├── adversarial/
    ├── fixtures/
    └── conformance/
```

---

## 17. Estratégia de open source e negócio

### Open source

Abrir:

- receipt schema;
- verifier;
- canonicalization;
- signing interfaces;
- core domain;
- policy SDK;
- Git adapter;
- conformance suite.

Motivo:

> Um produto de confiança não deve exigir confiança cega num formato fechado.

### Comercial

Produto empresarial:

- control plane;
- SSO e RBAC;
- policy management;
- evidence retention;
- integrations;
- private transparency log;
- reporting;
- multi-organization;
- deployment on-premises;
- support;
- compliance packs;
- incident forensics.

### Serviços

- accountability assessment;
- desenho de policies;
- integração;
- preparação de processos;
- formação;
- implementação;
- auditoria técnica;
- suporte anual.

### Hipótese de preços

- diagnóstico: 5 000–15 000 €
- piloto: 20 000–50 000 €
- implementação: 50 000–150 000 €
- licença anual: 50 000–250 000 €
- on-premises/regulado: negociação específica

Estes valores são hipóteses a validar com clientes, não uma tabela comercial fechada.

---

## 18. Riscos principais

### Risco 1 — Categoria demasiado ampla

Mitigação:

- começar exclusivamente por software changes;
- demonstrar num PR;
- evitar claims genéricos de AI governance.

### Risco 2 — Concorrentes dominam identidade e authorization

Mitigação:

- integrar standards;
- não competir com IAM;
- concentrar diferenciação no trabalho aceite.

### Risco 3 — Receipt sem valor jurídico ou de auditoria

Mitigação:

- envolver auditores, juristas e responsáveis de compliance;
- documentar limites;
- construir evidence mapping;
- manter signatures e identity verificáveis.

### Risco 4 — Logging cria novos riscos

Mitigação:

- minimização de dados;
- redaction;
- encryption;
- evidence references;
- retenção configurável;
- classificação de informação.

### Risco 5 — Complexidade excessiva

Mitigação:

- CLI e biblioteca primeiro;
- sem UI no MVP;
- um único caso de uso;
- contratos antes de integrações.

### Risco 6 — “Accountability” não gera orçamento

Mitigação:

- vender redução de risco;
- demonstrar incident reconstruction;
- ligar ao custo de auditoria, rework, incidentes e falhas de release;
- conseguir design partners com dor concreta.

---

## 19. Validação de mercado

Entrevistar pelo menos:

- 5 Heads of Engineering;
- 3 CISOs ou security leads;
- 3 responsáveis de qualidade;
- 3 internal auditors/compliance;
- 2 empresas que utilizem coding agents em produção.

Perguntas:

1. Conseguem identificar que alterações foram produzidas com assistência de IA?
2. Conseguem provar que checks específicos foram executados sobre o commit entregue?
3. Sabem que permissões o agente possuía?
4. Conseguem reconstruir um incidente envolvendo um coding agent?
5. Quem assume responsabilidade pelo resultado?
6. O approval está ligado ao commit ou apenas ao PR?
7. Que evidência pedem os clientes ou auditores?
8. Qual seria o custo de um incidente não atribuível?
9. Que sistemas não podem ser substituídos?
10. Pagariam por um piloto que produzisse receipts verificáveis para releases?

### Sinal forte

Uma empresa aceita:

- disponibilizar um repositório não crítico;
- definir uma policy real;
- executar dez alterações;
- rever os receipts;
- pagar por parte do piloto.

---

## 20. Métricas

### Métrica principal

**Accepted work receipts por equipa por semana.**

Um receipt conta apenas quando:

- corresponde a trabalho real;
- possui artefacto final;
- checks correram;
- policy foi avaliada;
- aprovação necessária foi obtida;
- assinatura foi validada.

### Guardrails

- receipt verification success: 100%;
- cross-execution proof mismatch: 0;
- unsigned final receipts: 0;
- unauthorized impact accepted: 0;
- mandatory checks skipped: 0;
- evidence integrity failures não detetadas: 0;
- tempo adicional por execução;
- percentagem de HOLD corretos;
- taxa de false holds;
- tempo de auditoria poupado.

---

## 21. Critérios de decisão após o MVP

### Continuar

- receipt validável offline;
- integração funcional com Git;
- pelo menos dois agentes suportados;
- policy blocks demonstráveis;
- três design partners interessados;
- um piloto pago ou carta de intenção;
- auditores consideram a evidência útil;
- overhead operacional aceitável.

### Reorientar

- empresas valorizam o receipt mas não o gateway;
- maior procura por evidence export;
- integração GitHub é mais valiosa que CLI;
- qualidade e audit trail são valorizados mais que authorization.

### Parar

- não existe willingness to pay;
- receipts não alteram decisões de procurement, audit ou release;
- integrações necessárias tornam o produto inviável;
- concorrentes oferecem fluxo completo e acessível antes da validação.

---

## 22. Primeira sequência de trabalho

1. Criar o repositório privado `workattest`.
2. Inicializar com ProjectPilot.
3. Importar este `ideia.md`.
4. Executar validação formal através de SkillLab.
5. Produzir `PROJECT_BRIEF.md`.
6. Criar `ACCOUNTABILITY-MODEL.md`.
7. Criar `THREAT-MODEL.md`.
8. Criar `TRUST-BOUNDARIES.md`.
9. Definir invariantes.
10. Definir o `work-receipt.schema.json`.
11. Rever standards e concorrentes.
12. Só depois iniciar implementação.

### Comando conceptual para ProjectPilot

```bash
pp init "WorkAttest: infraestrutura verificável que liga pedido, identidade, autorização, execução, evidência, verificação e aprovação humana a um receipt assinado para trabalho assistido por IA." --name "WorkAttest"
```

---

## 23. Definição de sucesso

WorkAttest terá provado a ideia quando uma pessoa externa conseguir receber:

- o artefacto;
- o receipt;
- a chave ou cadeia de identidade;
- as referências de evidência;

e confirmar independentemente:

1. que aquele era o trabalho autorizado;
2. que aquela execução produziu o artefacto;
3. que os checks aplicáveis foram executados;
4. que o resultado corresponde aos hashes registados;
5. que o responsável aprovou exatamente aquele resultado;
6. que o receipt não foi alterado.

Esse é o núcleo do produto.

Tudo o resto — dashboard, GitHub App, reporting, compliance e enterprise control plane — existe para distribuir, operar e monetizar essa propriedade.
