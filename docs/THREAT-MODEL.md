# THREAT MODEL — WorkAttest

> **Proof before acceptance.**

Threat model for the MVP. Structure: adversaries → assets → threats per link in the chain
→ mitigations → the adversarial tests that validate them. STRIDE framing where it applies.

---

## 1. Adversaries considered

| Adversary | Motivation | Assumed capability |
|---|---|---|
| **Dishonest/compromised agent** | Get out-of-scope work accepted | Controls its own narrative; does **not** control the checks or the keys |
| **Insider** (developer/approver) | Approve or forge an improper acceptance | Authenticated; constrained by segregation of duties |
| **Man-in-the-middle / after-the-fact tampering** | Alter evidence or a receipt after issuance | Has access to the receipt/evidence file |
| **Verifier evasion** | Pass without running mandatory checks | May try to choose or omit checks |
| **Replay / cross-execution** | Reuse an approval or proof from another execution | Has access to earlier receipts |
| **Key compromise** | Sign forged receipts | Obtains the private key (outside the scope of cryptographic defence — see limits) |

**Out of scope (MVP):** attacks on hardware/HSM, the dependency supply chain, attacks on
the AI model itself, and physical coercion of an approver.

## 2. Assets to protect

Signing keys · receipts · evidence (diffs, hashes, outputs) · policy and check definitions
· approval records · the **link** between all of them.

## 3. Threats per link (STRIDE) and mitigations

| Link / surface | Threat (STRIDE) | Mitigation | Invariant |
|---|---|---|---|
| Identity | **S**poofing — a name in the request body | Identity derives from a key or signed claim, never from a free-text string | INV-2, INV-10 |
| Authorization | **E**levation — acting out of scope | Actions validated against `allowed_actions/resources`; out of scope → REFUSE | INV-3 |
| Actions | **R**epudiation / **T**ampering — deny or alter what was done | Append-only plus hash chain (`previous_event_hash`); from an authorized source, not the agent | INV-4, INV-11 |
| Agent-supplied evidence | **T**ampering — declaring something false | Declared information is never verified evidence; the affected system confirms it | INV-4 |
| Artifacts | **T**ampering — swapping the artifact | `before_hash`/`after_hash`; the receipt binds to the exact hash | INV-6, INV-14 |
| Verification | **V**erifier evasion — the agent picks or omits checks | Checks are operator-defined; the agent does not choose them; absence is not approval | INV-5, INV-7, INV-8 |
| Policy | **T**ampering — swapping the policy silently | Policy is versioned, hashable, and referenced in the receipt | INV-7 |
| Approval | **E**levation / **cross-execution** — approving proof from another execution | The approval binds to the `result_hash` of the **same** execution; identity is authenticated | INV-9, INV-10 |
| Receipt | **T**ampering after the fact | Canonical serialization plus signature; changes are detectable | INV-12, INV-13, INV-14 |
| External verification | **I**nformation / dependence on the server | Offline verification with the public key and schema alone | INV-15 |
| Confidentiality | **I**nformation disclosure — leaking sensitive data through evidence | Sensitive content is never automatic; hash+ref, classification, redaction, encryption | INV-19 |
| Decision | **D**oS / degradation leading to unsafe acceptance | Fail-safe: failures close to HOLD/REFUSE, never ACCEPT | INV-20 |
| Terminal state | Reopening a REFUSE as an ACCEPT | A REFUSE only changes through a new evaluation | INV-18 |

## 4. Adversarial tests (mandatory in the MVP)

Every mitigation must have a test that **fails the receipt** when the attack is attempted.
All twelve are covered; the last column says where.

| | Attack | Required outcome | Test |
|---|---|---|---|
| **T-1** | Alter one byte of the receipt after signing | verification fails | `tests/adversarial/test_tamper.py` |
| **T-2** | Alter an artifact after `after_hash` | mismatch detected | `tests/adversarial/test_tamper.py` |
| **T-3** | Remove or tamper with an `ActionEvent` mid-chain | the hash chain breaks | `tests/unit/test_events.py` |
| **T-4** | Agent declares a check "passed" without running it | it does not count | `tests/adversarial/test_substitution.py` |
| **T-5** | Omit a mandatory check | HOLD, never ACCEPT | `tests/unit/test_policy.py` |
| **T-6** | Apply execution A's approval to execution B's result | rejected | `tests/adversarial/test_tamper.py` · `tests/unit/test_policy.py` |
| **T-7** | Expired authorization | REFUSE | `tests/unit/test_policy.py` |
| **T-8** | Action outside the authorized directories | HOLD/REFUSE | `tests/unit/test_policy.py` |
| **T-9** | Substitute the policy without updating its hash | detected | `tests/adversarial/test_substitution.py` |
| **T-10** | Approve with an unauthenticated identity / free-text name | rejected | `tests/adversarial/test_tamper.py` |
| **T-11** | Verify a receipt with no access to the server | succeeds (offline) | `tests/adversarial/test_offline_vectors.py` |
| **T-12** | Reopen a REFUSE as an ACCEPT without re-evaluating | blocked | `tests/adversarial/test_tamper.py` |

**T-11** deserves a note of its own. It is the only one not demonstrated by tampering with
something: the vectors in `tests/vectors/` were signed on another machine, by keys that no
longer exist, and CI verifies them on Linux, macOS and Windows. See
`tests/vectors/README.md`.

## 5. Accepted residual risks (MVP)

- **Key compromise** — if the private key is exfiltrated, forged receipts become possible.
  Partial mitigation: rotation and short scope; the path forward is HSM/KMS/keyless. Documented.
- **Weak timestamps** — a local clock is not strong proof of time. The path forward is a
  TSA or a transparency log.
- **Observing host integrity** — an intact observation environment is assumed.

## 6. Links

- Trust boundaries and anchors: `docs/TRUST-BOUNDARIES.md`.
- Referenced invariants (INV-*): `docs/INVARIANTS.md`.
- Proven facts and their limits: `docs/ACCOUNTABILITY-MODEL.md`.
