import base64
import sys
from ecdsa.util import randrange
from ecdsa.curves import SECP256k1
from ecdsa.ellipticcurve import Point
from cryptography.fernet import Fernet
import random
import os
import hashlib
import base64
from sympy import mod_inverse

# Function Definitions


def derive_fernet_key(ecc_key):
    """Derive a 32-byte Fernet-compatible key from an ECC key."""
    key_bytes = str(ecc_key).encode()  # Convert the ECC key to bytes
    sha256 = hashlib.sha256(key_bytes).digest()  # Compute SHA-256 hash
    return base64.urlsafe_b64encode(sha256[:32])  # Use the first 32 bytes

def generate_polynomial(t, constant_term, order):
    """Generate a polynomial of degree t-1 with a constant term and random coefficients."""
    print(f"\nGenerating polynomial of degree {t-1}...")
    coefficients = [constant_term] + [randrange(order) for _ in range(1, t)]
    print(f"Polynomial Coefficients: {coefficients}")
    return coefficients

def evaluate_polynomial(coefficients, x, order):
    """Evaluate a polynomial at a given x modulo the order."""
    return sum(c * pow(x, i) for i, c in enumerate(coefficients)) % order

def generate_shares(n, t, order):
    """Generate shares for n parties with a threshold t."""
    print("\nGenerating shares for parties...")
    polynomials = [generate_polynomial(t, randrange(order), order) for _ in range(n)]
    shares = [[evaluate_polynomial(poly, x + 1, order) for x in range(n)] for poly in polynomials]
    print(f"Generated Shares: {shares}")
    return polynomials, shares

def compute_cumulative_shares(shares, n):
    """Compute cumulative secret shares for each party."""
    print("\nComputing cumulative shares for each party...")
    cumulative_shares = [sum(shares[j][i] for j in range(n)) % SECP256k1.order for i in range(n)]
    print(f"Cumulative Shares: {cumulative_shares}")
    return cumulative_shares

def compute_public_keys(cumulative_shares, G):
    """Compute public keys for each party."""
    print("\nComputing public keys for each party...")
    public_keys = [share * G for share in cumulative_shares]
    print(f"Public Keys: {public_keys}")
    return public_keys

#----------------------------------------------------------------------

def lagrange_interpolation(selected_shares, selected_indices, t, order):
    """
    Reconstruct the secret using Lagrange interpolation.
    
    Params:
    - selected_shares: List of shares (int).
    - selected_indices: List of corresponding indices (int, 1-based).
    - t: Threshold (int).
    - order: Modulus for arithmetic operations.
    
    Returns:
    - Reconstructed secret (int).
    """
    assert len(selected_shares) == t, "Must provide exactly t shares for reconstruction."
    
    reconstructed_secret = 0
    for j in range(t):
        # Calculate Lagrange coefficient
        lj = 1
        for m in range(t):
            if m != j:
                numerator = selected_indices[m] % order
                denominator = (selected_indices[m] - selected_indices[j]) % order
                lj *= numerator * mod_inverse(denominator, order)
                lj %= order

        # Add share contribution
        reconstructed_secret += selected_shares[j] * lj
        reconstructed_secret %= order

    return reconstructed_secret

#-----------------------------------------------------------------------

def reconstruct_key(selected_shares, selected_indices, t, order):
    """
    Reconstruct the secret from a subset of t shares using Lagrange interpolation.
    """
    print("\nReconstructing secret key using selected shares...")
    assert len(selected_shares) == t, "Must provide exactly t shares for reconstruction."
    reconstructed_secret = 0

    for j in range(t):
        lj = 1  # Lagrange basis polynomial
        print(f"\nCalculating Lagrange coefficient for share {j + 1} (index {selected_indices[j]}):")
        for m in range(t):
            if m != j:
                numerator = selected_indices[m] % order
                denominator = (selected_indices[m] - selected_indices[j]) % order
                denominator_inv = mod_inverse(denominator, order)  # Modular inverse
                lj *= numerator * denominator_inv
                lj %= order  # Modular reduction
                print(f"  For m={m + 1}: numerator={numerator}, denominator={denominator}, "
                      f"denominator_inv={denominator_inv}, lj={lj}")

        share_contribution = selected_shares[j] * lj
        reconstructed_secret += share_contribution
        reconstructed_secret %= order  # Modular reduction
        print(f"  Share contribution: {share_contribution % order}, "
              f"Reconstructed so far: {reconstructed_secret}")

    print(f"\nReconstructed Secret: {reconstructed_secret}")
    return reconstructed_secret


def file_encrypt(filename, ecc_key):
    print("\nEncrypting file...")
    key = derive_fernet_key(ecc_key)  # Derive Fernet key from ECC key
    fernet = Fernet(key)

    print("encryption fernet key :", fernet)
    print("actual key: ", ecc_key)

    with open(filename, 'rb') as file:
        original = file.read()

    encrypted = fernet.encrypt(original)

    with open(filename, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)
    print("File has been encrypted.")

def file_decrypt(filename, ecc_key):
    print("\nDecrypting file...")
    key = derive_fernet_key(ecc_key)  # Derive Fernet key from ECC key
    fernet = Fernet(key)

    print("decryption fernet key: ", fernet)
    print("actual decryption key: ", ecc_key)

    with open(filename, 'rb') as enc_file:
        encrypted = enc_file.read()

    decrypted = fernet.decrypt(encrypted)

    with open(filename, 'wb') as dec_file:
        dec_file.write(decrypted)
    print("File has been decrypted.")



# Main Program
if __name__ == "__main__":
    # Step 1: Take user inputs for n and t
    n = int(input("Enter the number of parties (n): "))
    t = int(input("Enter the threshold (t): "))

    # Step 2: Generate shares and compute public/private keys
    polynomials, shares = generate_shares(n, t, SECP256k1.order)
    cumulative_shares = compute_cumulative_shares(shares, n)
    public_keys = compute_public_keys(cumulative_shares, SECP256k1.generator)

    # Compute the overall public key
    overall_public_key = public_keys[0]
    for pub_key in public_keys[1:]:
        overall_public_key += pub_key
    


    # Step 3: Ask the user if they want to encrypt a file
    file_name = input("\nEnter the path of the file to encrypt: ")
    encrypt_choice = input("Do you want to encrypt the file? (yes/no): ").lower()
    if encrypt_choice == "yes":
        key = base64.urlsafe_b64encode(int(overall_public_key.x()).to_bytes(32, 'big'))
        file_encrypt(file_name, key)

    # Step 4: Reconstruct the key using random t shares
    random_indices = random.sample(range(1, n + 1), t)
    selected_shares = [cumulative_shares[i - 1] for i in random_indices]
    reconstructed_secret = reconstruct_key(selected_shares, random_indices, t, SECP256k1.order)
        # Debugging: Check keys
    print("Derived encryption key:", derive_fernet_key(overall_public_key))
    print("Derived decryption key:", derive_fernet_key(reconstructed_secret))

    # Step 5: Ask the user if they want to decrypt the file
    decrypt_choice = input("Do you want to decrypt the file? (yes/no): ").lower()
    # print(f"Secret Value (encryption): {secret_value}")
    # print(f"Reconstructed Secret (decryption): {reconstructed_secret}")

    if decrypt_choice == "yes":
        # file_name = input("\nEnter the path of the file to decrypt: ")
        key = base64.urlsafe_b64encode(int(reconstructed_secret).to_bytes(32, 'big'))
        file_decrypt(file_name, key)

    # Output summary
    print("\nSummary:")
    print(f"Polynomials: {polynomials}")
    print(f"Shares: {shares}")
    print(f"Cumulative Shares: {cumulative_shares}")
    print(f"Public Keys: {public_keys}")
    print(f"Overall Public Key: {overall_public_key}")
