
"""Minimal ADB-over-TCP client (pure Python protocol + Java crypto).
Needed because this phone cannot exec an adb binary from app storage."""
import socket, struct, base64, os, json, hashlib, time

A_CNXN=0x4e584e43; A_AUTH=0x48545541; A_OPEN=0x4e45504f
A_OKAY=0x59414b4f; A_CLSE=0x45534c43; A_WRTE=0x45545257
ID_HOST=0; ID_LOCAL=1; ID_REMOTE=2

KEYFILE = "/data/user/0/com.niki914.zafiro/files/adb/adbkey.json"

def _java():
    from java.security import KeyPairGenerator, KeyFactory, Signature
    from java.security.spec import RSAPublicKeySpec, RSAPrivateKeySpec
    return KeyPairGenerator, KeyFactory, Signature, RSAPublicKeySpec, RSAPrivateKeySpec

def load_or_make_key():
    if os.path.exists(KEYFILE):
        j=json.load(open(KEYFILE))
        return int(j["n"]), int(j["d"]), j["e"]
    KPG,_,_,_,_ = _java()
    kpg = KPG.getInstance("RSA"); kpg.initialize(2048)
    kp = kpg.generateKeyPair()
    priv = kp.getPrivate(); pub = kp.getPublic()
    n = int(str(priv.getModulus())); d = int(str(priv.getPrivateExponent())); e = int(str(pub.getPublicExponent()))
    json.dump({"n":str(n),"d":str(d),"e":e}, open(KEYFILE,"w"))
    try: os.chmod(KEYFILE, 0o600)
    except Exception: pass
    return n,d,e

def _int32_le(x):
    return struct.pack(">I", x & 0xffffffff)

def pubkey_blob(n, e):
    size = 2048 // 8
    words = size // 4
    mod = n.to_bytes(size, "little")
    n0inv = (pow(n & 0xffffffff, -1, 1 << 32) * -1) % (1 << 32)
    rr = pow(2, 64 * words, n).to_bytes(size, "little")
    return _int32_le(words) + _int32_le(n0inv) + mod + rr + _int32_le(e)

def pubkey_b64(n, e, name="zafiro@phone"):
    return base64.b64encode(pubkey_blob(n, e) + b" " + name.encode()).decode()

def sign_token(n, d, token, scheme=2):
    """PKCS#1 v1.5 signature with SHA-1 DigestInfo over the 20-byte token.
    scheme 1 = token is re-hashed (real adb RSA_sign), 2 = token used raw as digest (adb_shell)."""
    k = 256
    digest = hashlib.sha1(token).digest() if scheme == 1 else token
    di = bytes.fromhex("3021300906052b0e03021a05000414") + digest
    pad = b"\xff" * (k - len(di) - 3)
    em = b"\x00\x01" + pad + b"\x00" + di
    m = int.from_bytes(em, "big")
    s = pow(m, d, n)
    return s.to_bytes(k, "big")

class AdbError(Exception): pass

class Adb:
    def __init__(self, host, port=5555, timeout=20):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.buf = b""
        self.n, self.d, self.e = load_or_make_key()
        self.next_local = 1
        self.banner = ""

    def _send(self, cmd, a0, a1, data=b""):
        hdr = struct.pack("<6I", cmd, a0, a1, len(data), sum(data) & 0xffffffff, cmd ^ 0xffffffff)
        self.sock.sendall(hdr + data)

    def _recv_exact(self, n):
        out = b""
        while len(out) < n:
            c = self.sock.recv(n - len(out))
            if not c:
                raise AdbError("connection closed by device")
            out += c
        return out

    def _read(self):
        hdr = self._recv_exact(24)
        cmd, a0, a1, ln, csum, magic = struct.unpack("<6I", hdr)
        if magic != (cmd ^ 0xffffffff):
            raise AdbError("bad header magic")
        data = self._recv_exact(ln) if ln else b""
        return cmd, a0, a1, data

    def connect(self, auth_timeout=120, scheme=2, on_prompt=None):
        self._send(A_CNXN, 0x01000001, 262144, b"host::features=cmd,stat_v2\0")
        deadline = time.time() + auth_timeout
        signed = 0
        pubkey_sent = False
        while time.time() < deadline:
            try:
                cmd, a0, a1, data = self._read()
            except socket.timeout:
                continue
            if cmd == A_CNXN:
                self.banner = data.decode("utf-8", "replace").rstrip("\0")
                self.maxdata = min(a1, 262144) or 262144
                return self.banner
            if cmd == A_AUTH and a0 == 1:      # TOKEN
                if signed < 1:
                    self._send(A_AUTH, 2, 0, sign_token(self.n, self.d, data, scheme))
                    signed += 1
                elif not pubkey_sent:
                    if on_prompt: on_prompt()
                    self._send(A_AUTH, 3, 0, pubkey_b64(self.n, self.e).encode() + b"\0")
                    pubkey_sent = True
                    self.sock.settimeout(5)
                # after pubkey, keep waiting for CNXN (dialog on TV)
            elif cmd == A_STLS:
                raise AdbError("device requires TLS (wireless debugging) - use adb pair")
        raise AdbError("timed out: allow dialog not accepted on the TV?")

    # ---- streams ----
    def open_stream(self, dest):
        lid = self.next_local; self.next_local += 1
        self._send(A_OPEN, lid, 0, dest.encode() + b"\0")
        while True:
            cmd, a0, a1, data = self._read()
            if cmd == A_OKAY and a1 == lid:
                return lid, a0
            if cmd == A_CLSE and a1 == lid:
                raise AdbError("stream refused: " + dest)

    def _wait_wrte(self, lid):
        while True:
            cmd, a0, a1, data = self._read()
            if cmd == A_WRTE and a1 == lid:
                self._send(A_OKAY, a0, lid)
                return data
            if cmd == A_CLSE and a1 == lid:
                return None

    def shell(self, cmd, timeout=120):
        last = None
        for attempt in range(4):
            try:
                self.sock.settimeout(timeout)
                lid, rid = self.open_stream("shell:" + cmd)
                out = b""
                while True:
                    d = self._wait_wrte(lid)
                    if d is None: break
                    out += d
                return out.decode("utf-8", "replace")
            except AdbError as e:
                last = e
                if "refused" in str(e):
                    time.sleep(0.25)
                    continue
                raise
        return "ERROR: %s" % last


    def _drain(self, lid, sink, timeout=0.0):
        """Read every fully available packet; append WRTE data to sink."""
        import select as _sel
        while True:
            r,_,_ = _sel.select([self.sock], [], [], timeout)
            if not r: return
            cmd, a0, a1, data = self._read()
            if cmd == A_WRTE and a1 == lid:
                self._send(A_OKAY, a0, lid)
                sink.append(data)
            elif cmd == A_CLSE and a1 == lid:
                raise AdbError("__closed__")

    def shell_stdin(self, cmd, data, chunk=32768, timeout=180):
        """Run `cmd` with `data` streamed to its stdin (like adb shell < file)."""
        self.sock.settimeout(timeout)
        lid, rid = self.open_stream("shell:" + cmd)
        sink = []
        try:
            for i in range(0, len(data), chunk):
                self._send(A_WRTE, lid, rid, data[i:i+chunk])
                self._drain(lid, sink)
            self._send(A_CLSE, lid, rid)
        except AdbError as e:
            if "__closed__" not in str(e):
                raise
        # collect remaining output
        end = time.time() + timeout
        while time.time() < end:
            try:
                self.sock.settimeout(2.0)
                cmd, a0, a1, d = self._read()
            except socket.timeout:
                break
            if cmd == A_WRTE and a1 == lid:
                self._send(A_OKAY, a0, lid); sink.append(d)
            elif cmd == A_CLSE and a1 == lid:
                break
        return b"".join(sink).decode("utf-8", "replace")

    def push(self, local_path, remote_path, chunk=60000):
        size = os.path.getsize(local_path)
        lid, rid = self.open_stream("sync:")
        def wr(data):
            self._send(A_WRTE, lid, rid, data)
            while True:
                cmd, a0, a1, d = self._read()
                if cmd == A_WRTE and a1 == lid:
                    self._send(A_OKAY, a0, lid); return d
                if cmd == A_CLSE and a1 == lid:
                    raise AdbError("sync stream closed")
        def recv_msg():
            cmd, a0, a1, d = self._read()
            if cmd == A_WRTE and a1 == lid:
                self._send(A_OKAY, a0, lid); return d
            if cmd == A_CLSE:
                raise AdbError("sync stream closed")
            return b""
        wr(b"SEND" + struct.pack("<I", len(remote_path)) + remote_path.encode())
        r = recv_msg()
        if not r.startswith(b"OKAY"):
            raise AdbError("SEND rejected: %r" % r[:32])
        with open(local_path, "rb") as f:
            sent = 0
            while sent < size:
                b = f.read(chunk)
                if not b: break
                wr(b"DATA" + struct.pack("<I", len(b)) + b)
                r = recv_msg()
                if not r.startswith(b"OKAY"):
                    raise AdbError("DATA rejected: %r" % r[:32])
                sent += len(b)
            wr(b"DONE" + struct.pack("<I", 0o644 << 16 | 0))
            r = recv_msg()
            if not r.startswith(b"OKAY"):
                raise AdbError("DONE failed: %r" % r[:32])
        self._send(A_CLSE, lid, rid)
        return size

    def close(self):
        try: self.sock.close()
        except Exception: pass
