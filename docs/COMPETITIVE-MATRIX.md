# COMPETITIVE MATRIX — WorkAttest

> **Proof before acceptance.**

Where WorkAttest is different. **Positioning principle:** WorkAttest does **not** compete
as an editor, an agent, an agent framework, observability, a SIEM, generic GRC, a project
manager, a testing tool or an IAM. It is a **neutral layer** between them.

---

## 1. The axis of differentiation

Most tools prove **fragments**:

- an agent called a tool;
- a user started a session;
- a policy allowed an action;
- a commit passed CI.

WorkAttest **additionally** proves that:

- the commit corresponds to the **authorized request**;
- the concrete artifacts are identified;
- the applicable checks ran (and the agent did not choose them);
- the evidence belongs to that version;
- **no obligation was skipped**;
- the responsible person accepted **exactly** that result;
- the receipt remains verifiable **outside** WorkAttest.

## 2. Matrix by category

Legend: ✅ covers · ◐ partial · ✗ does not cover · — outside that category's scope

| Capability | Coding agents (Claude/Codex/Cursor) | Observability / traces | SIEM | CI/CD + status checks | Supply chain (Sigstore/in-toto/SLSA) | GitHub Artifact Attestations | Generic GRC | **WorkAttest** |
|---|---|---|---|---|---|---|---|---|
| Produce the change | ✅ | ✗ | ✗ | ◐ | ✗ | ✗ | ✗ | — (integrates) |
| Record what happened | ◐ | ✅ | ✅ | ◐ | ✗ | ✗ | ◐ | ◐ (focused on acceptance) |
| Scoped authorization **before** the action | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ◐ | ✅ |
| Prove the checks **ran** | ✗ | ✗ | ✗ | ◐ | ◐ | ◐ | ✗ | ✅ |
| The agent does **not** choose the checks | ✗ | — | — | ✗ | — | — | ✗ | ✅ |
| Artifact provenance (hash) | ✗ | ✗ | ✗ | ◐ | ✅ | ✅ | ✗ | ✅ |
| **Human approval bound to the exact artifact** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ◐ | ✅ |
| "No obligation skipped" (policy completeness) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ◐ | ✅ |
| **Offline** third-party verification | ✗ | ✗ | ✗ | ✗ | ◐ | ◐ | ✗ | ✅ |
| Neutral across stacks and agents | — | ◐ | ◐ | ✗ | ✅ | ✗ | ◐ | ✅ |

## 3. Adjacent competitors (the closest ones)

| Competitor | Overlap | WorkAttest's delta | Risk |
|---|---|---|---|
| **GitHub Artifact Attestations** | Signed, verifiable build provenance | Does not model *prior authorization* or *human approval of the exact result* as formal acceptance | **High** — the incumbent could extend into it; mitigate by integrating rather than competing |
| **Sigstore + in-toto + SLSA** | Signing, attestation, provenance levels | WorkAttest **aligns** with them and adds the *accepted work* layer (policy + approval + custody) | Medium — more ally than rival; use as the foundation |
| **Agent observability** (LLM tracing) | Records tool calls and sessions | A trace is neither a verifiable chain of custody nor a signed acceptance | Low — complementary |
| **GRC / audit tooling** | Approval workflow and evidence | Declarative approval versus approval bound cryptographically to the artifact | Medium — sell as the proof layer beneath GRC |

## 4. One-sentence positioning

> Sigstore and SLSA prove **where the artifact came from**. WorkAttest proves **that the
> work was authorized, verified and accepted by the responsible person** — and binds that
> to the exact artifact, verifiable offline.

## 5. Strategic implications

1. **Integrate, do not compete**, with identity/IAM and build provenance.
2. The defensible moat is **acceptance with custody** (authorization + policy + human
   approval bound to the artifact), not signing itself.
3. The most real competitive risk is an incumbent (GitHub) extending into "acceptance".
   Counter: depth in the first wedge, neutrality across stacks, and audit value delivered
   before the incumbent gets there.

## 6. Links

- The standards decisions behind interoperability: `docs/STANDARDS-DECISIONS.md`.
- Exactly what is proven: `docs/ACCOUNTABILITY-MODEL.md`.
