# STANDARDS DECISIONS — WorkAttest

> **Proof before acceptance.**

Decisões sobre que standards adotar, avaliar ou adiar. **Princípio:** WorkAttest liga
standards existentes num modelo de aceitação do trabalho — **não reinventa cada
componente**. Evitar protocolos criptográficos proprietários quando já existe standard
adequado.

Formato: cada decisão é um mini-ADR (Adotar / Avaliar / Adiar / Rejeitar) com razão.

---

## 1. Quadro-resumo

| Standard | Domínio | Decisão (MVP) | Razão |
|---|---|---|---|
| **Ed25519** | Assinaturas | **Adotar** | Simples, rápido, deterministicamente verificável offline |
| **JSON Canonicalization (RFC 8785 / JCS)** | Serialização canónica | **Adotar** | Necessário para hashes/receipts reprodutíveis (INV-12) |
| **DSSE** (Dead Simple Signing Envelope) | Envelope de assinatura | **Adotar** | Envelope standard para payloads assinados; base do in-toto |
| **in-toto attestations** | Formato de atestação | **Adotar (alinhar)** | Alinhar o receipt com predicados in-toto para interoperar com o ecossistema supply-chain |
| **Sigstore (cosign/Fulcio)** | Keyless signing | **Avaliar** | Reduz gestão de chaves; útil na evolução, não bloqueante no MVP |
| **Rekor / transparency log** | Prova de inclusão/tempo | **Avaliar / Adiar** | MVP funciona offline; transparency service (público ou privado) entra depois |
| **SCITT** | Transparência de supply-chain | **Avaliar** | Standard emergente IETF; monitorizar para o control plane empresarial |
| **SLSA** | Níveis de proveniência | **Alinhar** | Enquadrar os receipts como evidência de proveniência; útil comercialmente |
| **OIDC** | Identidade em CI | **Adotar (CI)** | Identidade de workload em pipelines sem chaves de longa duração |
| **SPIFFE/SPIRE** | Workload identity | **Adiar** | Enterprise; sobredimensionado para o MVP |
| **Git commit signing** | Autoria | **Adotar** | Fonte de identidade e integridade já disponível no adapter |
| **GitHub Artifact Attestations** | Proveniência de build | **Avaliar (interop)** | Potencial concorrente **e** ponto de integração — mapear o delta |
| **OpenTelemetry** | Observabilidade | **Adiar** | Não é core; útil para operação futura |
| **CycloneDX / SPDX (SBOM)** | Inventário de componentes | **Adiar** | Fora do primeiro wedge; relevante em release receipts |
| **RFC 3161 (TSA)** | Timestamp forte | **Adiar** | Endereça o risco de "timestamp fraco" na evolução |
| **MCP / protocolos de agentes** | Interop com agentes | **Avaliar** | Superfície de observação de ações de agentes |

## 2. Decisões-chave (detalhe)

### D-1 — Assinatura: Ed25519 + DSSE. **Adotar.**
Ed25519 para as chaves; DSSE como envelope. Mantém a verificação offline simples e
alinha com in-toto. *Alternativa rejeitada no MVP:* esquemas proprietários (violam o
princípio de não reinventar cripto).

### D-2 — Canonicalização: RFC 8785 (JCS). **Adotar.**
Sem serialização canónica não há hash reprodutível nem INV-12/14. JCS é standard e
determinístico.

### D-3 — Atestação: alinhar o receipt com in-toto. **Adotar (alinhar).**
O `WorkReceipt` é conceptualmente um predicado in-toto enriquecido (autorização +
aprovação humana + decisão de policy). Alinhar o schema para poder emitir/consumir
atestações in-toto sem lock-in.

### D-4 — Transparência: offline primeiro, log depois. **Adiar.**
O MVP tem de verificar **sem** servidor (INV-15). Rekor/SCITT/transparency privado
entram como reforço opcional (prova de inclusão e tempo), não como dependência.

### D-5 — Posicionamento vs. GitHub Attestations / Sigstore / SLSA. **Avaliar (crítico).**
Estes cobrem "este commit veio de um build autorizado". O **delta** do WorkAttest é
ligar *trabalho aceite + aprovação humana autenticada* ao artefacto exato. Esta análise
alimenta `docs/COMPETITIVE-MATRIX.md` e é um risco estratégico (não competir com IAM
nem com proveniência de build; diferenciar no *aceite*).

### D-6 — Identidade: chaves locais + Git + OIDC (CI) no MVP; SSO/SPIFFE depois. **Adotar/Adiar.**
Cobrir os casos reais do primeiro wedge sem construir um IAM.

## 3. Critérios para promover um "Avaliar" a "Adotar"

- Existe um caso de uso do primeiro wedge que o exige.
- Não obriga a rede nem quebra a verificação offline do MVP.
- Reduz confiança cega (aumenta verificabilidade independente).
- Tem implementação estável e testável.

## 4. Ligações

- Impacto na confiança: `docs/TRUST-BOUNDARIES.md`.
- Diferenciação vs. concorrentes: `docs/COMPETITIVE-MATRIX.md`.
- Estrutura do receipt: `schemas/work-receipt.schema.json`.
