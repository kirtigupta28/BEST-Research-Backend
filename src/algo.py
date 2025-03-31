# from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
from ecdsa.ellipticcurve import CurveFp, Point, INFINITY
from ecdsa.numbertheory import inverse_mod
from ecdsa.util import randrange
import hashlib
from ecdsa.ellipticcurve import CurveFp, Point
import base64
from cryptography.fernet import Fernet
import ecdsa.curves as curves
import ecdsa.keys as eckeys
from ecdsa.ecdsa import point_is_valid, int_to_string, string_to_int, int2byte
import random
from pypdf import PdfReader

import time 

# Custom curve parameters
# p = 17  # Prime modulus
# a = 2  # Curve coefficient a
# b = 2  # Curve coefficient b
# order = 19  # Order of the curve
# PatInf = [0, 0]  #define "Point at Infinity"

# # Define the custom curve
# curve = CurveFp(p, a, b)

# # Define the generator point (on the curve)
# G = Point(curve, 5, 1, order)

curve = curves.BRAINPOOLP256t1.curve
G = curves.BRAINPOOLP256t1.generator
order = curves.BRAINPOOLP256t1.order
# PatInf = Point(x=None, y=None, curve=None)
a = curve.a
b = curve.b
p = order

def generate_polynomial_and_commitments(t, constant_term):
    """Generate a polynomial of degree t-1 with a constant term and random coefficients."""
    coefficients = [constant_term] + [randrange(order) for _ in range(1, t)] 
    commitments = [coeff*G for coeff in coefficients] 

    return coefficients, commitments

def evaluate_polynomial(coefficients, x):
    """Evaluate a polynomial at a given x modulo the order."""
    return sum(c * pow(x, i) for i, c in enumerate(coefficients)) % order  #n*(t-1)


def verify_secret_share(secret_share, j, commitments, n, t):
    '''
        si,j*G ?= sigma(0 to t-1) j^i * Fi, j
        ith participant generated share for jth participant
    '''
    verify = 0

    for i in range(n):
        # verify share sent by ith participant to jth participant
        verify = commitments[i][0]
        for k in range(1, t):
            verify += pow(j, k) * commitments[i][k] #n^2*t point multiplications + n^2*t point additions
        
        status = verify == secret_share[i][j-1] * G #n^2
        yield status, i, j

# def verify_secret_share(secret_share, i, F):
#     """ Verifies that a specific share of a set of secret shares is
#         valid against a list of public parameters used to generate it.
    
#         PARAMS
#         ------
#             secret_share: (int) specific share to be verified.
            
#             i: (int) index of the secrete instance in the share
#             F: (list) set of public parameters with which the share
#                 was generated.
        
#         RETURNS
#         -------
#             boolean value indicating if specific share is valid.
#     """
#     verify = F[0]

#     for j in range(1, len(F)):
#         verify += pow(i+1, j) * F[j]

#     return verify == secret_share * G


# def mod_inv(a, m):
#     return pow(
#         a, -1, m
#     )  

# def add_points(x1, y1, x2, y2, a, p):
#     #check this while loop
#     while y2 < 0:
#         y2 = y2 + p

#     if x1 == x2 and y1 == y2:
#         Lambda = (3 * x1 * x1 + a) * mod_inv(2 * y1, p)
#     else:
#         if x1 == x2:
#             return INFINITY
#         elif [x1, y1] == INFINITY:
#             return x2, y2
#         elif [x2, y2] == INFINITY:
#             return x1, y1
#         else:
#             Lambda = (y2 - y1) * mod_inv(x2 - x1, p)

#     x3 = (Lambda * Lambda - x1 - x2) % p
#     y3 = ((x1 - x2) * Lambda - y1) % p
#     return Point(curve=curves.SECP256k1.curve, x=x3, y=y3, order=order)


# frontend
def compute_public_keys():
    """Compute public keys for each party."""
    public_keys = []
    for poly in polynomials:
        secret = poly[0]
        public_keys.append(secret * G) #n

    return public_keys


# backend
def compute_overall_public_key(public_keys):
    Q = public_keys[0]
    for i in range(1, len(public_keys)):
        Q = Q + public_keys[i] #n point addition
        # Q = Q.__add__(public_keys[i])
        # Q = add_points(Q.x(), Q.y(), public_keys[i].x(), public_keys[i].y(), a,
        #                p)
    return Q


# backend
def reconstruct_key(sub_secret_share, t):
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

        recon_key += (sub_secret_share[j - 1] * int(mult)) % order

    return recon_key % order

def signature_generation(faculty_private_key, message):
    h=int(hashlib.sha256(message.encode()).hexdigest(),16)
    k=random.randint(0, p-1)
    R = k*G
    r = R.x() % p
    inv_k = inverse_mod(k, p)
    s = ((h + faculty_private_key*r)*inv_k)%p
    return r, s

def symmetric_key_gen():
    key = Fernet.generate_key()

    return key


def int_to_fernet_key(value):
    """
    Convert an integer back to a Fernet key (URL-safe base64).
    """
    # Convert the integer to bytes
    key_bytes = value.to_bytes((value.bit_length() + 7) // 8, byteorder='big')
    # Encode bytes to a URL-safe base64 string
    # base64.urlsafe_b64encode(key_bytes).decode('utf-8')
    return base64.urlsafe_b64encode(key_bytes)


def asymmetric_encryption(pub_key, message):
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
    k = randrange(order-1) #0 to p-2

    C1 = (k * G) 
    H = (k * pub_key) 

    #TODO:confirm here
    C2 = (message + H.y()) % order

    return (C1, C2)


def decrypt(sec_key, cipher):
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

    H = sec_key * C1

    message = (C2 - H.y()) % order

    return message


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

def signature_verification(faculty_public_key, r, s, message):
    h = int(hashlib.sha256(message.encode()).hexdigest(),16)
    w = inverse_mod(s, p)
    u1 = (h*w) %p
    u2 = (r*w) %p
    P = u1*G+u2*faculty_public_key
    rx = (P.x())%p

    print("R' = ", rx)

    return rx==r

def get_message(file):

    # creating a pdf reader object
    reader = PdfReader(file)

    # printing number of pages in pdf file
    print(len(reader.pages))

    # creating a page object
    page = reader.pages[0]

    # extracting text from page
    return page.extract_text()

if __name__ == "__main__":
    # Example Usage
    t: int = 3  # Threshold
    n: int = 5  # Number of shares
    file = "Test.pdf"

    time_for_key_generation = time.time()

    # Generate shares
    polynomials: list[list] = []
    commitments: list[list] = []

    for _ in range(n):
        polynomial, commitment = generate_polynomial_and_commitments(t, randrange(order))
        polynomials.append(polynomial)
        commitments.append(commitment)

    shares = [[evaluate_polynomial(poly, x + 1) for x in range(n)]
              for poly in polynomials]

    # Compute cumulative shares (scalar value)
    cumulative_shares = [
        sum(share[i] for share in shares) % order for i in range(n) 
    ]

    # Verification of shares
    for j in range(n):
        print(f"Participant {j+1} share: {cumulative_shares[j]}")
        for result, i, j in verify_secret_share(shares, j+1, commitments, n, t):
            print(f"Verified: {result}, share sent by i: {i} to j: {j}")

    # Compute public keys (point addition)
    public_keys = compute_public_keys()

    #Overall public key
    overall_public_key = compute_overall_public_key(public_keys)

    time_for_key_generation = time.time() - time_for_key_generation
    print("Time for key generation:", time_for_key_generation)

    # for i in range(n):
    #     print(s[i], end=' ')
    #     print("Verfied:",verify_secret_share(s[i], i, F))

    # Print results
    print("Polynomials:", polynomials)
    print("Shares:", shares)
    print("Cumulative Shares:", cumulative_shares)
    print("Public Keys:", [(pk.x(), pk.y()) for pk in public_keys])
    print("Overall Public Key:",
          (overall_public_key.x(), overall_public_key.y()))

    # Working fine
    reconstructed_key = reconstruct_key(cumulative_shares, t)

    print("Reconstructed Key:", reconstructed_key)

    faculty_private_key = random.randint(0, p-1)
    faculty_public_key = faculty_private_key*G

    time_for_signature_gen = time.time()

    message = get_message(file)

    r, s = signature_generation(faculty_private_key, message)

    print("Time for sign gen: ", time.time()-time_for_signature_gen)

    print("Value of r = ", r)

    time_for_encryption = time.time()
    # Generate a Fernet key
    symmetric_key = symmetric_key_gen()
    print("Symmetric Key:", symmetric_key)

    # Encrypt the file using Fernet symmetric encryption
    Enc_File(symmetric_key, "Test.pdf")

    # Encrypt the Fernet key using ECC
    C1, C2 = asymmetric_encryption(overall_public_key, fernet_key_to_int(symmetric_key))
    print("C1:", C1)
    print("C2:", C2)

    print("Time for encryption:", time.time() - time_for_encryption)

    time_for_decryption = time.time()

    # Decrypt the Fernet key using ECC
    decrypted_key = decrypt(reconstructed_key, (C1, C2))
    print("Decrypted Key:", int_to_fernet_key(decrypted_key))

    # Decrypt the file using Fernet symmetric decryption
    Dec("Test.pdf", int_to_fernet_key(decrypted_key))

    print("Time for decryption:", time.time() - time_for_decryption)

    time_for_signature_ver = time.time()

    message = get_message(file)

    result = signature_verification(faculty_public_key, r, s, message)

    print("Time for sign gen: ", time.time()-time_for_signature_gen)

    print("Result of signature verification", result)
