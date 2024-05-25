import base64
import struct
import time
from Cryptodome.Cipher import AES
from nacl.public import PublicKey, SealedBox
import nacl.utils
def encryptPassword(password: str):
    timestamp = int(time.time())
    key = nacl.utils.random(32)
    cipher = AES.new(key, AES.MODE_GCM, nonce=b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", mac_len=16)
    cipher.update(str(timestamp).encode("utf-8"))
    encryptedPassword, cipherTag = cipher.encrypt_and_digest(password.encode("utf-8"))
    encryptionKeyBytes = bytes.fromhex("8dd9aad29d9a614c338cff479f850d3ec57c525c33b3f702ab65e9e057fc087e")
    seal_box = SealedBox(PublicKey(encryptionKeyBytes))
    encryptedKey = seal_box.encrypt(key)
    encrypted = struct.pack("<BB", 1, 87) + struct.pack("<h", len(encryptedKey)) + encryptedKey + cipherTag + encryptedPassword
    return f"#PWD_INSTAGRAM_BROWSER:9:{timestamp}:{base64.b64encode(encrypted).decode('utf-8')}"
