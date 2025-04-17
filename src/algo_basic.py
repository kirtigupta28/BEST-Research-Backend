# from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
from ecdsa.ellipticcurve import CurveFp, Point
from ecdsa.numbertheory import inverse_mod
from ecdsa.util import randrange
import hashlib
from ecdsa.ellipticcurve import CurveFp, Point
import base64
from cryptography.fernet import Fernet
import ecdsa.curves as curves
import ecdsa.keys as eckeys
import secrets
import random
import sympy
import time

# Custom curve parameters
# p = 17  # Prime modulus
# a = 2  # Curve coefficient a
# b = 2  # Curve coefficient b
# order = 19  # Order of the curve
# PatInf = [0, 0]  #define "Point at Infinity"

# Define the custom curve
# curve = CurveFp(p, a, b)

# Define the generator point (on the curve)
# G = Point(curve, 5, 1, order)

# G = curves.SECP256k1.generator

# generate large prime for cryptography 

p = 0

def generate_prime_number(bits):
    """Generates a prime number with the specified number of bits."""
    while True:
        # Generate a random integer with the specified number of bits
        num = secrets.randbits(bits)

        # Ensure the number is odd
        if num % 2 == 0:
            num += 1

        # Check if the number is prime using the Miller-Rabin primality test
        if is_prime(num):
            return num


def is_prime(num, k=5):
    """Checks if a number is prime using the Miller-Rabin primality test."""
    if num <= 1:
        return False
    if num <= 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False

    r, s = 0, num - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    for _ in range(k):
        a = random.randrange(2, num - 1)
        x = pow(a, s, num)
        if x == 1 or x == num - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, num)
            if x == num - 1:
                break
        else:
            return False
    return True


def is_generator(g, p):
    """Checks if g is a generator of Zp."""
    factors = sympy.primefactors(p - 1)
    for q in factors:
        if pow(g, (p - 1) // q, p) == 1:
            return False
    return True

# frontend
def generate_polynomial(t, constant_term, order):
    """Generate a polynomial of degree t-1 with a constant term and random coefficients."""
    coefficients = [constant_term] + [randrange(order) for _ in range(1, t)]
    return coefficients


# frontend
def evaluate_polynomial(coefficients, x, order):
    """Evaluate a polynomial at a given x modulo the order."""
    return sum(c * pow(x, i) for i, c in enumerate(coefficients)) % order


# backend
def mod_inv(a, m):
    return pow(
        a, -1, m
    )  #since python 3.8 (demonstrated in last video with extended euclidean in C)


def keygen():
    key = Fernet.generate_key()

    return key

def square_and_multiply(g, secret, p):
  """
  Calculates g^secret mod p using the square-and-multiply algorithm.

  Args:
    g: The base.
    secret: The exponent.
    p: The modulus.

  Returns:
    g^secret mod p
  """

  result = 1
  secret_bin = bin(secret)[2:]  # Convert secret to binary string

  for bit in secret_bin:
    result = (result * result) % p  # Square
    if bit == '1':
      result = (result * g) % p  # Multiply

  return result


# frontend
def compute_public_keys(shares, G):
    """Compute public keys for each party."""
    public_keys = []
    for poly in polynomials:
        secret = poly[0]
        public_keys.append(square_and_multiply(G, secret, p))

    return public_keys


# backend
def compute_overall_public_key(public_keys):
    Q = public_keys[0]
    for i in range(1, len(public_keys)):
        Q *= public_keys[i]%p

    return Q


# backend
def reconstruct_key(sub_secret_share, t, order):
    """ Reconstructs a secret from a share of sub secrets. Requires
        a subset of size t. The sub secret share is the split of the
        original split.
        PARAMS
        ------
            sub_secret_share: (int) sub set of secrets that can reconstruct secret.

            t: (int) size of sub set that can reconstruct secret.
            G: (ecdsa.ellipticcurve.Point) Base point for the elliptic curve.

        RETURNS
        -------
            reconstructed key.
    """
    assert (len(sub_secret_share) >= t)
    recon_key = 0

    for j in range(1, t + 1):
        mult = 1

        for h in range(1, t + 1):
            if h != j:
                mult *= (h / (h - j))

        recon_key *= (sub_secret_share[j - 1] * int(mult)) % order

    return recon_key % order


def int_to_fernet_key(value):
    """
    Convert an integer back to a Fernet key (URL-safe base64).
    """
    # Convert the integer to bytes
    key_bytes = value.to_bytes((value.bit_length() + 7) // 8, byteorder='big')
    # Encode bytes to a URL-safe base64 string
    return base64.urlsafe_b64encode(key_bytes).decode('utf-8')


def generate_key(order=curves.SECP256k1.order):
    """ Generates a private key for use with ECC. Basically
        a random number generator with mod order.

        PARAMS
        ------
            order: (int) the order of the curve.
        RETURNS
        -------
            (int) private key.
    """
    return randrange(order)


def encrypt(pub_key, message, G, order):
    """ Encrypts a message with an ECC threshold public key.
        Standard ECC encryption.

        PARAMS
        ------
            pub_key: (ecdsa.ellipticcurve.Point) public key with which to encrypt message.
            message: (int) message to be encrypted.
            G: (ecdsa.ellipticcurve.Point) Base point for the elliptic curve.
            O: (int) Order of elliptic curve
        RETURNS
        -------
            (P, c) touple with encrypted message.
    """
    k = randrange(order)

    C1 = square_and_multiply(G, k, order)
    H = square_and_multiply(pub_key, k, order)

    C2 = (message * H)%order

    return (C1, C2)


def decrypt(sec_key, cipher, order):
    """ Descrypts a ciphertext encrypted with the corresponding public key
        to the private key being provided.

        PARAMS
        ------
            sec_key: (int) secret key corresponding to the public key used to
            encrypt message.
            cipher: (ecdsa.ellipticcurve.Point, int) encrypted message.
        RETURNS
        -------
            message: (int) original message. 
    """
    (C1, C2) = cipher

    c1_x = square_and_multiply(C1, sec_key, order)

    message = C2*mod_inv(c1_x, order)

    # H = sec_key * C1

    # message = (C2 - H.y())

    return message%order


def fernet_key_to_int(fernet_key):
    """
    Convert a Fernet key (URL-safe base64) to an integer.
    """
    # Decode the base64 key to bytes
    key_bytes = base64.urlsafe_b64decode(fernet_key)
    # Convert bytes to an integer
    return int.from_bytes(key_bytes, byteorder='big')


def Enc_File(key, filename):
   # generating a key
#    key = int_to_fernet_key(key)

   fernet = Fernet(key)
 
   # opening the original file to encrypt
   with open(filename, 'rb') as file:
      original = file.read()
     
   # encrypting the file
   encrypted = fernet.encrypt(original)
 
   # opening the file in write mode and
   # writing the encrypted data
   with open(filename, 'wb') as encrypted_file:
      encrypted_file.write(encrypted)
   

def Dec(filename, key):
	# open file containing key
	# with open('filekey.key', 'rb') as filekey:
	# 	key = filekey.read()

	fernet = (Fernet(key))

	# opening the encrypted file
	with open(filename, 'rb') as enc_file:
		encrypted = enc_file.read()

	# decrypting the file
	decrypted = fernet.decrypt(encrypted)

	# opening the file in write mode and
	# writing the decrypted data
	with open(filename, 'wb') as dec_file:
		dec_file.write(decrypted)



if __name__ == "__main__":
    t = 3  # Threshold
    n = 5  # Number of shares

    p = generate_prime_number(512)
    print("Prime Number:", p)

    # Find a generator
    G = p-1  # Start with a small potential generator
    while not is_generator(G, p):
        G = random.randint(2, p - 1)

    time_for_key_genration = time.time()

    # Generate shares
    polynomials = [
        generate_polynomial(t, randrange(p), p) for _ in range(n)
    ]
    shares = [[evaluate_polynomial(poly, x + 1, p) for x in range(n)]
              for poly in polynomials]

    # Compute cumulative shares (scalar value)
    cumulative_shares = [
        sum(share[i] for share in shares) % p for i in range(n)
    ]

    # Compute public keys (exponentiation)
    public_keys = compute_public_keys(shares, G)

    #Overall public key
    overall_public_key = compute_overall_public_key(public_keys)

    time_for_key_genration = time.time() - time_for_key_genration
    print("Time for key generation:", time_for_key_genration)

    # Print results
    print("Polynomials:", polynomials)
    print("Shares:", shares)
    print("Cumulative Shares:", cumulative_shares)
    print("Public Keys:", [pk for pk in public_keys])
    print("Overall Public Key:",
          (overall_public_key))

    # reconstructed_key = reconstruct_key(cumulative_shares, t, p)

    # print("Reconstructed Key:", reconstructed_key)

    time_for_encryption = time.time()

    # # Generate a Fernet key
    fernet_key = keygen()
    print("Fernet Key:", fernet_key)

    # # Encrypt the file using Fernet symmetric encryption
    Enc_File(fernet_key, "Test.pdf")

    # # Encrypt the Fernet key using ECC
    C1, C2 = encrypt(overall_public_key, fernet_key_to_int(fernet_key), G,
                     p)
    print("C1:", C1)
    print("C2:", C2)

    time_for_encryption = time.time() - time_for_encryption
    print("Time for encryption:", time_for_encryption)

    # # Decrypt the Fernet key using ECC
    time_for_decryption = time.time()
    decrypted_key = decrypt(reconstructed_key, (C1, C2), p)
    print("Decrypted Key:", int_to_fernet_key(decrypted_key))

    # # Decrypt the file using Fernet symmetric decryption
    # @TODO: yahan par hard coded hai for time testing
    Dec("Test.pdf", fernet_key)
    time_for_decryption = time.time() - time_for_decryption
    print("Time for decryption:", time_for_decryption)

    # int_fernet_key = fernet_key_to_int(fernet_key)
    # safe_fernet_key = int_to_fernet_key(int_fernet_key)

    # print(safe_fernet_key==fernet_key.decode("utf-8") )
    # print(fernet_key)
    # print(safe_fernet_key)

    # s_key, p_key = generate_key_pair(t, n)





