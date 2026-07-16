from workattest.crypto import KeyPair, Signature, sign, verify


def test_sign_and_verify_roundtrip():
    kp = KeyPair.generate()
    sig = sign(kp, b"the message")
    assert verify(sig, b"the message") is True


def test_verify_fails_on_tampered_message():
    kp = KeyPair.generate()
    sig = sign(kp, b"the message")
    assert verify(sig, b"the MESSAGE") is False


def test_verify_fails_on_wrong_key():
    kp1 = KeyPair.generate()
    kp2 = KeyPair.generate()
    sig = sign(kp1, b"msg")
    forged = Signature(alg=sig.alg, key_id=sig.key_id, public_key=kp2.public_key_b64, value=sig.value)
    assert verify(forged, b"msg") is False


def test_verify_never_raises_on_garbage():
    bad = Signature(alg="ed25519", key_id="x", public_key="not-base64!!", value="also-bad")
    assert verify(bad, b"msg") is False


def test_pem_roundtrip():
    kp = KeyPair.generate()
    restored = KeyPair.from_pem(kp.private_bytes_pem())
    assert restored.public_key_b64 == kp.public_key_b64
