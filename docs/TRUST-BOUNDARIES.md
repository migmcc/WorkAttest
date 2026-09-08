# TRUST BOUNDARIES — WorkAttest

> **Proof before acceptance.**

Where trust **begins** and where it **ends**. A receipt is only worth something if whoever
consumes it knows exactly which roots of trust it rests on, and what falls outside them.

---

## 1. Principle

WorkAttest does **not** trust the agent's account of events. Wherever possible it obtains
confirmation from the affected system (Git, filesystem, CI) rather than from the executor's
narrative. Evidence declared by the agent is treated as a *claim*, never as a *verified
fact*.

## 2. Trust anchors

| Anchor | What it anchors | Degree of trust | Can be replaced by |
|---|---|---|---|
| Ed25519 signing keys | Signatures on receipts, approvals, events | **Critical** | HSM, KMS, Sigstore keyless |
| Git identity / commit signing | Commit authorship | Medium | GitHub/OIDC, SPIFFE |
| GitHub / OIDC identity (CI) | The subject in pipelines | Medium | SSO, workload identity |
| Check definitions (hash) | Which check actually ran | High (if the operator controls the hash) | A signed check registry |
| Observing source (Git/FS adapter) | Actions and artifacts | High (authorized source) | A mediated gateway |
| Clock / timestamps | Ordering and temporal validity | Low (MVP: local clock) | RFC 3161 TSA, transparency log |

## 3. Trust zones

```
┌─────────────────────────── UNTRUSTED ───────────────────────────┐
│  Agent (Claude/Codex)  ·  workspace  ·  request body input        │
│  → everything here is a CLAIM, subject to verification             │
└───────────────┬───────────────────────────────────────────────────┘
                │  trust boundary #1: observation by an authorized source
┌───────────────▼─────────────── SEMI-TRUSTED ──────────────────────┐
│  Git adapter · FS adapter · Verifier runner                        │
│  → collect facts from the affected system, not the agent's story   │
└───────────────┬───────────────────────────────────────────────────┘
                │  trust boundary #2: deterministic policy + signature
┌───────────────▼─────────────────── TRUSTED ───────────────────────┐
│  Core domain · Policy engine · Receipt issuer · signing keys       │
│  → deterministic, canonical, signed                                │
└───────────────┬───────────────────────────────────────────────────┘
                │  trust boundary #3: offline verification, public key only
┌───────────────▼──────────────── INDEPENDENT ──────────────────────┐
│  Independent verifier (another machine, no server)                 │
│  → trusts ONLY the public key and the schema, not the issuing app  │
└────────────────────────────────────────────────────────────────────┘
```

## 4. What sits **inside** the trust boundary

- The core domain is deterministic and infrastructure-independent.
- The policy is versioned, hashable and testable.
- The receipt is canonically serialized and signed.
- Independent verification does not require the main server.

## 5. What sits **outside** it (explicit assumptions and limits)

- **Correctness of the work** — out of scope (see `ACCOUNTABILITY-MODEL.md` §3).
- **Sufficiency of the checks** — the organization is responsible for defining adequate
  checks; WorkAttest proves they ran, not that they were enough.
- **Competence of the human approval** — we prove *who* and *what*, not the quality of the
  judgement.
- **Private key security** — if the signing key is compromised, the model collapses.
  Mitigation: rotation, HSM/KMS, and keyless (Sigstore) as the system evolves.
- **Trust in the clock (MVP)** — local timestamps are not strong proof of time; the path
  forward is a TSA or a transparency log.
- **Integrity of the observing machine** — the adapter must run in an intact environment.

## 6. Failure mode: fail-safe

Identity, policy, signature or verification failures **close safely** (`HOLD`/`REFUSE`),
never as `ACCEPT`. Absent mandatory checks are not an approval.

## 7. Links

- Threats against each boundary: `docs/THREAT-MODEL.md`.
- Guaranteed facts: `docs/ACCOUNTABILITY-MODEL.md`, `docs/INVARIANTS.md`.
- Anchor and standards choices: `docs/STANDARDS-DECISIONS.md`.
