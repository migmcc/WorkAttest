# STANDARDS DECISIONS — WorkAttest

> **Proof before acceptance.**

Decisions about which standards to adopt, evaluate or defer. **Principle:** WorkAttest
connects existing standards into a model of accepted work — it does **not reinvent each
component**. Avoid proprietary cryptographic protocols wherever an adequate standard
already exists.

Format: each decision is a mini-ADR (Adopt / Evaluate / Defer / Reject) with its reason.

---

## 1. Summary table

| Standard | Domain | Decision (MVP) | Reason |
|---|---|---|---|
| **Ed25519** | Signatures | **Adopt** | Simple, fast, deterministically verifiable offline |
| **JSON Canonicalization (RFC 8785 / JCS)** | Canonical serialization | **Adopt** | Required for reproducible hashes and receipts (INV-12) |
| **DSSE** (Dead Simple Signing Envelope) | Signature envelope | **Adopt** | Standard envelope for signed payloads; the basis of in-toto |
| **in-toto attestations** | Attestation format | **Adopt (align)** | Align the receipt with in-toto predicates to interoperate with the supply-chain ecosystem |
| **Sigstore (cosign/Fulcio)** | Keyless signing | **Evaluate** | Reduces key management; useful later, not blocking for the MVP |
| **Rekor / transparency log** | Inclusion and time proof | **Evaluate / Defer** | The MVP works offline; a transparency service (public or private) comes afterwards |
| **SCITT** | Supply-chain transparency | **Evaluate** | Emerging IETF standard; monitor for the enterprise control plane |
| **SLSA** | Provenance levels | **Align** | Frames receipts as provenance evidence; commercially useful |
| **OIDC** | Identity in CI | **Adopt (CI)** | Workload identity in pipelines without long-lived keys |
| **SPIFFE/SPIRE** | Workload identity | **Defer** | Enterprise-scale; oversized for the MVP |
| **Git commit signing** | Authorship | **Adopt** | A source of identity and integrity already available in the adapter |
| **GitHub Artifact Attestations** | Build provenance | **Evaluate (interop)** | Both a potential competitor **and** an integration point — map the delta |
| **OpenTelemetry** | Observability | **Defer** | Not core; useful for future operations |
| **CycloneDX / SPDX (SBOM)** | Component inventory | **Defer** | Outside the first wedge; relevant for release receipts |
| **RFC 3161 (TSA)** | Strong timestamps | **Defer** | Addresses the "weak timestamp" risk as the system evolves |
| **MCP / agent protocols** | Agent interoperability | **Evaluate** | A surface for observing agent actions |

## 2. Key decisions (in detail)

### D-1 — Signing: Ed25519 + DSSE. **Adopt.**
Ed25519 for the keys; DSSE as the envelope. Keeps offline verification simple and aligns
with in-toto. *Alternative rejected for the MVP:* proprietary schemes, which violate the
principle of not reinventing cryptography.

### D-2 — Canonicalization: RFC 8785 (JCS). **Adopt.**
Without canonical serialization there is no reproducible hash, and no INV-12/14. JCS is
standard and deterministic.

### D-3 — Attestation: align the receipt with in-toto. **Adopt (align).**
The `WorkReceipt` is conceptually an enriched in-toto predicate (authorization + human
approval + policy decision). Align the schema so in-toto attestations can be issued and
consumed without lock-in.

### D-4 — Transparency: offline first, log later. **Defer.**
The MVP must verify **without** a server (INV-15). Rekor, SCITT or a private transparency
service come in as optional reinforcement — proof of inclusion and time — never as a
dependency.

### D-5 — Positioning against GitHub Attestations / Sigstore / SLSA. **Evaluate (critical).**
These cover "this commit came from an authorized build". WorkAttest's **delta** is binding
*accepted work plus an authenticated human approval* to the exact artifact. This analysis
feeds `docs/COMPETITIVE-MATRIX.md` and carries strategic risk: do not compete with IAM or
with build provenance; differentiate on **acceptance**.

### D-6 — Identity: local keys + Git + OIDC (CI) in the MVP; SSO/SPIFFE later. **Adopt/Defer.**
Cover the real cases of the first wedge without building an IAM.

## 3. Criteria for promoting an "Evaluate" to an "Adopt"

- A use case in the first wedge requires it.
- It does not mandate network access or break the MVP's offline verification.
- It reduces blind trust (it increases independent verifiability).
- It has a stable, testable implementation.

## 4. Links

- Impact on trust: `docs/TRUST-BOUNDARIES.md`.
- Differentiation against competitors: `docs/COMPETITIVE-MATRIX.md`.
- Receipt structure: `schemas/work-receipt.schema.json`.
