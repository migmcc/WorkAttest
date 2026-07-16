# TRUST BOUNDARIES — WorkAttest

> **Proof before acceptance.**

Onde a confiança **começa** e **acaba**. Um receipt só tem valor se o seu consumidor
souber exatamente em que raízes de confiança está a assentar e o que fica fora delas.

---

## 1. Princípio

WorkAttest **não** confia no relato do agente. Sempre que possível, obtém confirmação
do sistema afetado (Git, filesystem, CI), não da narrativa do executor. A evidência
declarada pelo agente é tratada como *afirmação*, nunca como *facto verificado*.

## 2. Raízes de confiança (trust anchors)

| Âncora | O que ancora | Grau de confiança | Substituível por |
|---|---|---|---|
| Chaves Ed25519 (signing keys) | Assinaturas de receipts, approvals, events | **Crítica** | HSM, KMS, Sigstore keyless |
| Identidade Git / commit signing | Autoria de commits | Média | GitHub/OIDC, SPIFFE |
| Identidade GitHub / OIDC (CI) | Subject em pipelines | Média | SSO, workload identity |
| Definições de checks (hash) | Que check correu | Alta (se o hash for controlado pelo operador) | Registo de checks assinado |
| Fonte observadora (Git/FS adapter) | Ações e artefactos | Alta (fonte autorizada) | Gateway mediado |
| Relógio / timestamps | Ordem e validade temporal | Baixa (MVP: relógio local) | RFC 3161 TSA, transparency log |

## 3. Zonas de confiança

```
┌─────────────────────────── UNTRUSTED ───────────────────────────┐
│  Agente (Claude/Codex)  ·  workspace  ·  input do request body    │
│  → tudo aqui é AFIRMAÇÃO, sujeita a verificação                    │
└───────────────┬───────────────────────────────────────────────────┘
                │  trust boundary #1: observação por fonte autorizada
┌───────────────▼─────────────── SEMI-TRUSTED ──────────────────────┐
│  Git adapter · FS adapter · Verifier runner                        │
│  → recolhem factos do sistema afetado, não da narrativa do agente  │
└───────────────┬───────────────────────────────────────────────────┘
                │  trust boundary #2: policy determinística + assinatura
┌───────────────▼─────────────────── TRUSTED ───────────────────────┐
│  Core domain · Policy engine · Receipt issuer · signing keys       │
│  → determinístico, canónico, assinado                              │
└───────────────┬───────────────────────────────────────────────────┘
                │  trust boundary #3: verificação offline com chave pública
┌───────────────▼──────────────── INDEPENDENT ──────────────────────┐
│  Independent verifier (outra máquina, sem servidor)                │
│  → confia APENAS na chave pública + no schema, não na app emissora │
└────────────────────────────────────────────────────────────────────┘
```

## 4. O que fica **dentro** da fronteira de confiança

- O core do domínio é determinístico e independente de infraestrutura.
- A policy é versionada, hashable e testável.
- O receipt é serializado canonicamente e assinado.
- A verificação independente não requer o servidor principal.

## 5. O que fica **fora** (assunções e limites explícitos)

- **Correção do trabalho** — fora de âmbito (ver `ACCOUNTABILITY-MODEL.md` §3).
- **Suficiência dos checks** — a organização é responsável por definir checks adequados;
  WorkAttest prova que correram, não que bastavam.
- **Competência da aprovação humana** — provamos *quem* e *o quê*, não a qualidade do juízo.
- **Segurança da chave privada** — se a signing key for comprometida, o modelo cai.
  Mitigação: rotação, HSM/KMS, keyless (Sigstore) na evolução.
- **Confiança no relógio (MVP)** — timestamps locais não são prova de tempo forte;
  evolução: TSA / transparency log.
- **Integridade da máquina que observa** — o adapter tem de correr em ambiente íntegro.

## 6. Modo de falha: fail-safe

Falhas de identidade, policy, assinatura ou verificação **fecham em segurança**
(`HOLD`/`REFUSE`), nunca em `ACCEPT`. Ausência de checks obrigatórios ≠ aprovação.

## 7. Ligações

- Ameaças a cada fronteira: `docs/THREAT-MODEL.md`.
- Factos garantidos: `docs/ACCOUNTABILITY-MODEL.md`, `docs/INVARIANTS.md`.
- Escolhas de âncoras/standards: `docs/STANDARDS-DECISIONS.md`.
