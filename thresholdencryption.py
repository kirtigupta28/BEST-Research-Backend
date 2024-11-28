import os
from ecdsa.util import randrange
from ecdsa.curves import SECP256k1
from ecdsa.ellipticcurve import Point
from ecdsa.numbertheory import inverse_mod
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


# ------------------ ECC Threshold Cryptosystem ------------------ #

def secret_split(secret, t, n, G=SECP256k1.generator, O=SECP256k1.order):
    """
    Splits a secret into `n` shares, where `t` shares can reconstruct it.
    """
    assert n >= t, "Number of shares must be greater than or equal to threshold."

    # Polynomial coefficients (secret is the constant term)
    coef = [secret] + [randrange(O) for _ in range(1, t)]

    # Polynomial function
    f = lambda x: sum([coef[i] * pow(x, i) for i in range(t)]) % O

    # Generate `n` shares
    secret_shares = [f(i) for i in range(1, n + 1)]

    # Public commitments (polynomial coefficients multiplied by the generator)
    F = [coef[j] * G for j in range(t)]

    return secret_shares, F


def verify_secret_share(secret_share, i, F, G=SECP256k1.generator):
    """
    Verifies a secret share using public commitments.
    """
    verify = F[0]

    for j in range(1, len(F)):
        verify += pow(i + 1, j) * F[j]

    return verify == secret_share * G


def reconstruct_key(sub_secret_shares, t, O=SECP256k1.order):
    """
    Reconstructs the secret key using a subset of `t` shares.
    """
    assert len(sub_secret_shares) >= t, "Insufficient shares to reconstruct the key."

    recon_key = 0
    for j in range(t):
        mult = 1
        for k in range(t):
            if j != k:
                mult *= (k + 1) / (k + 1 - (j + 1))
        recon_key += sub_secret_shares[j] * mult
    return int(recon_key) % O


def encrypt(pub_key, aes_key, G=SECP256k1.generator, O=SECP256k1.order):
    """
    Encrypts the AES key using ECC public key encryption.
    """
    k = randrange(O)
    C1 = k * G
    H = k * pub_key
    C2 = (int.from_bytes(aes_key, "big") + H.y()) % O
    return (C1, C2)


def decrypt(sec_key, cipher, O=SECP256k1.order):
    """
    Decrypts the encrypted AES key using ECC private key decryption.
    """
    C1, C2 = cipher
    H = sec_key * C1
    aes_key_int = (C2 - H.y()) % O
    aes_key = aes_key_int.to_bytes(32, "big")
    return aes_key


# ------------------ AES File Encryption ------------------ #

def encrypt_file(input_file, output_file, aes_key):
    """
    Encrypts a file using AES-256 encryption.
    """
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(input_file, "rb") as f:
        plaintext = f.read()

    ciphertext = iv + encryptor.update(plaintext) + encryptor.finalize()

    with open(output_file, "wb") as f:
        f.write(ciphertext)


def decrypt_file(input_file, output_file, aes_key):
    """
    Decrypts an AES-encrypted file.
    """
    with open(input_file, "rb") as f:
        data = f.read()

    iv = data[:16]
    ciphertext = data[16:]
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    with open(output_file, "wb") as f:
        f.write(plaintext)


# ------------------ Threshold Parameters & Operations ------------------ #

def generate_threshold_parameters(t, n):
    """
    Generates threshold cryptosystem parameters.
    """
    sec_key = randrange(SECP256k1.order)  # Private key
    pub_key = sec_key * SECP256k1.generator  # Public key
    secret_shares, commitments = secret_split(sec_key, t, n)
    return sec_key, pub_key, secret_shares, commitments


# ------------------ Example Usage ------------------ #

if __name__ == "__main__":
    # Example parameters
    t = 3  # Threshold
    n = 5  # Number of shares
    file_to_encrypt = "example.pdf"
    encrypted_file = "example_encrypted.pdf"
    decrypted_file = "example_decrypted.pdf"

    # Generate threshold parameters
    sec_key, pub_key, secret_shares, commitments = generate_threshold_parameters(t, n)

    print("Private Key:", sec_key)
    print("Public Key:", pub_key)

    # Verify shares
    for i in range(n):
        valid = verify_secret_share(secret_shares[i], i, commitments)
        print(f"Share {i + 1} verified: {valid}")

    # Reconstruct the secret key
    recon_key = reconstruct_key(secret_shares[:t], t)
    print("Reconstructed Key:", recon_key)

    # Generate AES key
    aes_key = os.urandom(32)

    # Encrypt AES key with ECC
    cipher = encrypt(pub_key, aes_key)
    print("Encrypted AES Key:", cipher)

    # Decrypt AES key with ECC
    decrypted_aes_key = decrypt(sec_key, cipher)
    print("Decrypted AES Key matches:", decrypted_aes_key == aes_key)

    # Encrypt file
    encrypt_file(file_to_encrypt, encrypted_file, aes_key)
    print(f"File encrypted: {encrypted_file}")

    # Decrypt file
    decrypt_file(encrypted_file, decrypted_file, aes_key)
    print(f"File decrypted: {decrypted_file}")
