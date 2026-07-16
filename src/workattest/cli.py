"""WorkAttest command-line interface (MVP subset).

Commands:
  workattest init [--dir DIR]        Initialize a .workattest workspace + issuer key.
  workattest keygen [--out FILE]     Generate an Ed25519 key pair (PEM).
  workattest demo [--out FILE]       Build a signed demo receipt and verify it offline.
  workattest receipt verify FILE     Verify a receipt offline; exit 0 if valid, 1 if not.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .crypto.keys import KeyPair
from .receipts.verifier import verify_receipt
from .scenario import build_accepted_receipt
from .storage import read_json, write_json


def _cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.dir) / ".workattest"
    (root / "keys").mkdir(parents=True, exist_ok=True)
    (root / "receipts").mkdir(parents=True, exist_ok=True)
    key_path = root / "keys" / "issuer.pem"
    if key_path.exists() and not args.force:
        print(f"Already initialized: {key_path} exists (use --force to regenerate).")
        return 0
    kp = KeyPair.generate()
    key_path.write_bytes(kp.private_bytes_pem())
    print(f"Initialized WorkAttest workspace at {root}")
    print(f"Issuer key id: {kp.key_id}")
    print(f"Public key (b64): {kp.public_key_b64}")
    return 0


def _cmd_keygen(args: argparse.Namespace) -> int:
    kp = KeyPair.generate()
    out = Path(args.out) if args.out else None
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(kp.private_bytes_pem())
        print(f"Wrote private key to {out}")
    print(f"key_id: {kp.key_id}")
    print(f"public_key_b64: {kp.public_key_b64}")
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    result = build_accepted_receipt()
    out = Path(args.out) if args.out else Path("receipt.json")
    write_json(out, result.receipt)
    print(f"Policy decision: {result.decision.value}")
    for reason in result.reasons:
        print(f"  - {reason}")
    print(f"Wrote signed receipt to {out}")
    report = verify_receipt(result.receipt)
    print()
    print(report.summary())
    return 0 if report.valid else 1


def _cmd_observe_git(args: argparse.Namespace) -> int:
    from datetime import datetime, timezone

    from .adapters.git import GitError
    from .adapters.git.flow import build_change_receipt
    from .domain.enums import RiskClass
    from .verification import load_checks

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        checks = load_checks(args.checks) if args.checks else ()
    except (OSError, ValueError) as exc:
        print(f"cannot load checks: {exc}", file=sys.stderr)
        return 2
    approver_key = None
    if args.approver_key:
        try:
            approver_key = KeyPair.from_pem(Path(args.approver_key).read_bytes())
        except (OSError, ValueError) as exc:
            print(f"cannot load approver key: {exc}", file=sys.stderr)
            return 2
    try:
        result = build_change_receipt(
            repo_path=args.repo,
            before_ref=args.before,
            after_ref=args.after,  # None => working tree
            allowed_prefix=args.allowed_prefix,
            issuer_key=KeyPair.generate(),
            agent_key=KeyPair.generate(),
            now=now,
            risk=RiskClass.HIGH if args.high_risk else RiskClass.LOW,
            checks=checks,
            approver_key=approver_key,
        )
    except GitError as exc:
        print(f"git error: {exc}", file=sys.stderr)
        return 2

    out = Path(args.out) if args.out else Path("receipt.json")
    write_json(out, result.receipt)
    print(f"Repo: {args.repo}  (before {result.before_commit})")
    print(f"Changed files ({len(result.changed_paths)}): {', '.join(result.changed_paths) or '(none)'}")
    for vr in result.receipt.get("verification", []):
        flag = "*" if vr.get("mandatory") else " "
        print(f"  check[{flag}] {vr['check_id']}: {vr['status']} (exit {vr.get('exit_code')})")
    print(f"Policy decision: {result.decision.value}")
    for reason in result.reasons:
        print(f"  - {reason}")
    print(f"Wrote signed receipt to {out}")
    report = verify_receipt(result.receipt)
    print()
    print(report.summary())
    return 0 if report.valid else 1


def _cmd_receipt_verify(args: argparse.Namespace) -> int:
    try:
        receipt = read_json(args.file)
    except (OSError, ValueError) as exc:
        print(f"Cannot read receipt: {exc}", file=sys.stderr)
        return 2
    report = verify_receipt(receipt)
    print(report.summary())
    return 0 if report.valid else 1


def _cmd_receipt_redact(args: argparse.Namespace) -> int:
    from .redaction import redact_receipt

    try:
        receipt = read_json(args.file)
    except (OSError, ValueError) as exc:
        print(f"Cannot read receipt: {exc}", file=sys.stderr)
        return 2
    redacted = redact_receipt(receipt, args.field)
    out = Path(args.out) if args.out else Path(args.file)
    write_json(out, redacted)
    print(f"Redacted fields {args.field} -> {out}")
    report = verify_receipt(redacted)
    print(report.summary())
    return 0 if report.valid else 1


def _cmd_receipt_open(args: argparse.Namespace) -> int:
    from .redaction import open_disclosure

    try:
        receipt = read_json(args.file)
    except (OSError, ValueError) as exc:
        print(f"Cannot read receipt: {exc}", file=sys.stderr)
        return 2
    try:
        value = open_disclosure(receipt, args.field)
    except KeyError as exc:
        print(f"Unknown field: {exc}", file=sys.stderr)
        return 2
    except LookupError as exc:
        print(f"Redacted: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Integrity failure: {exc}", file=sys.stderr)
        return 1
    print(f"{args.field}: {value}")
    return 0


def _cmd_receipt_verify_chain(args: argparse.Namespace) -> int:
    from .receipts import verify_chain

    receipts = []
    for path in args.files:
        try:
            receipts.append(read_json(path))
        except (OSError, ValueError) as exc:
            print(f"Cannot read receipt {path}: {exc}", file=sys.stderr)
            return 2
    report = verify_chain(receipts)
    print(report.summary())
    return 0 if report.valid else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workattest", description="Verifiable Work Accountability")
    parser.add_argument("--version", action="version", version=f"workattest {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize a workspace and issuer key")
    p_init.add_argument("--dir", default=".")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=_cmd_init)

    p_keygen = sub.add_parser("keygen", help="Generate an Ed25519 key pair")
    p_keygen.add_argument("--out")
    p_keygen.set_defaults(func=_cmd_keygen)

    p_demo = sub.add_parser("demo", help="Build and verify a signed demo receipt")
    p_demo.add_argument("--out")
    p_demo.set_defaults(func=_cmd_demo)

    p_git = sub.add_parser("observe-git", help="Observe a git change and issue a receipt")
    p_git.add_argument("--repo", default=".")
    p_git.add_argument("--before", default="HEAD", help="Base ref (default HEAD)")
    p_git.add_argument("--after", default=None, help="Target ref (default: working tree)")
    p_git.add_argument("--allowed-prefix", default="src/", dest="allowed_prefix",
                       help="Authorized directory scope (default src/)")
    p_git.add_argument("--high-risk", action="store_true", help="Treat as high risk (requires approval)")
    p_git.add_argument("--checks", help="Path to an operator checks config (JSON list)")
    p_git.add_argument("--approver-key", dest="approver_key",
                       help="PEM private key of the human approver (adds a signed approval)")
    p_git.add_argument("--out")
    p_git.set_defaults(func=_cmd_observe_git)

    p_receipt = sub.add_parser("receipt", help="Receipt operations")
    r_sub = p_receipt.add_subparsers(dest="receipt_command")
    p_verify = r_sub.add_parser("verify", help="Verify a receipt offline")
    p_verify.add_argument("file")
    p_verify.set_defaults(func=_cmd_receipt_verify)

    p_chain = r_sub.add_parser("verify-chain", help="Verify an ordered receipt chain (root first)")
    p_chain.add_argument("files", nargs="+")
    p_chain.set_defaults(func=_cmd_receipt_verify_chain)

    p_redact = r_sub.add_parser("redact", help="Remove disclosed values (keeps commitments); stays verifiable")
    p_redact.add_argument("file")
    p_redact.add_argument("--field", action="append", default=[], help="Field name to redact (repeatable)")
    p_redact.add_argument("--out")
    p_redact.set_defaults(func=_cmd_receipt_redact)

    p_open = r_sub.add_parser("open", help="Reveal a disclosed field and verify its commitment")
    p_open.add_argument("file")
    p_open.add_argument("field")
    p_open.set_defaults(func=_cmd_receipt_open)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())
