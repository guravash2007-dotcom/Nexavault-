import os, json, base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

class NexaEngine:
    def __init__(self):
        self.vault_path = "vault_storage"
        self.manifest_file = ".vault_manifest.bin"
        if not os.path.exists(self.vault_path): 
            os.makedirs(self.vault_path)

    def derive_key(self, password):
        salt = b'Nexa_Static_Salt_2026'
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def shatter(self, file_path, password):
        try:
            key = self.derive_key(password)
            fernet = Fernet(key)
            with open(file_path, "rb") as f: data = f.read()
            
            encrypted = fernet.encrypt(data)
            chunk = len(encrypted) // 3
            file_id = str(abs(hash(file_path)))[:6]
            
            # Store the FULL original path
            filename = os.path.basename(file_path)
            orig_dir = os.path.dirname(file_path)

            for i in range(3):
                part = encrypted[i*chunk : (i+1)*chunk] if i < 2 else encrypted[i*chunk:]
                with open(os.path.join(self.vault_path, f"{file_id}_p{i}.shard"), "wb") as f:
                    f.write(part)

            self._update_manifest(file_id, filename, orig_dir, password)
            os.remove(file_path) 
            return True
        except: return False

    def _update_manifest(self, fid, name, orig_dir, pw):
        manifest = self.get_history(pw) or {}
        # Save name AND original directory
        manifest[fid] = {"name": name, "dir": orig_dir}
        key = self.derive_key(pw)
        with open(self.manifest_file, "wb") as f:
            f.write(Fernet(key).encrypt(json.dumps(manifest).encode()))

    def get_history(self, pw):
        if not os.path.exists(self.manifest_file): return {}
        try:
            key = self.derive_key(pw)
            with open(self.manifest_file, "rb") as f:
                return json.loads(Fernet(key).decrypt(f.read()).decode())
        except: return None

    def reconstitute(self, fid, name, orig_dir, pw):
        try:
            key = self.derive_key(pw)
            combined = b""
            for i in range(3):
                with open(os.path.join(self.vault_path, f"{fid}_p{i}.shard"), "rb") as f:
                    combined += f.read()
            
            decrypted = Fernet(key).decrypt(combined)
            # Restore to original directory
            final_path = os.path.join(orig_dir, name)
            with open(final_path, "wb") as f:
                f.write(decrypted)
            return True
        except: return False
