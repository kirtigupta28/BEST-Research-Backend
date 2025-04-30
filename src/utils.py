from flask import Flask, request, jsonify, send_file, make_response
from flask_pymongo import PyMongo
from gridfs import GridFS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from bson import ObjectId
from dotenv import dotenv_values
import io
from flask_cors import CORS, cross_origin
from binascii import unhexlify
import hashlib

from ecdsa.ellipticcurve import CurveFp, Point
from ecdsa.numbertheory import inverse_mod
from ecdsa.util import randrange
from cryptography.fernet import Fernet
# from ecdsa.curves import SECP256k1, NIST256p
from ecdsa.ecdsa import point_is_valid, int_to_string
import base64

# from utils import int_to_urlsafe_base64, point_to_urlsafe_base64

import hashlib
from ecdsa.ellipticcurve import CurveFp, Point

# Custom curve parameters
# p = SECP256k1.curve.p()  # Prime modulus
# a = SECP256k1.curve.a() # Curve coefficient a
# order = SECP256k1.order  # Order of the curve
# order = 19
# PatInf = [0, 0] #define "Point at Infinity"
# G = SECP256k1.generator

p = 17  # Prime modulus
a = 2  # Curve coefficient a
b = 2  # Curve coefficient b
order = 19  # Order of the curve
PatInf = [0, 0] #define "Point at Infinity"


# Define the custom curve
curve = CurveFp(p, a, b)

# Define the generator point (on the curve)
G = Point(curve, 5, 1, order)

# secrets = dotenv_values(".env")
import os 

def connect_db(): 

    app = Flask(__name__)
    CORS(app)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    print("Connecting to MongoDB...")

    mongo = PyMongo(app)
    db = mongo.db
    return (app, db)

def configure(app): 
    app.config["JWT_SECRET_KEY"] = secrets["JWT_SECRET_KEY"]

def upload_pdf(pdf_file, grid_fs):
    try:
        # Save the file to GridFS
        print("Inside utils.upload_pdf", pdf_file)
        filename = secure_filename(pdf_file.filename)  # Ensure filename is safe
        file_id = grid_fs.put(pdf_file, filename=filename, content_type='application/pdf')
        
        return str(file_id)

    except Exception as e:
        
        return -1


def get_pdf(file_id, grid_fs):
    try:
        # Retrieve the file from GridFS
        file_data = grid_fs.get(ObjectId(file_id))
        
        # Create a file-like object from the file data
        file_stream = io.BytesIO(file_data.read())
        file_stream.seek(0)
        
        # Return the file as a response
        response = send_file(
            file_stream,
            mimetype=file_data.content_type,
            as_attachment=True,
            download_name=file_data.filename
        )

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 404

def convert_pdf_to_bytes(pdf_file):
    try:        
        # Create a file-like object from the file data
        file_stream = io.BytesIO(pdf_file.read())
        file_stream.seek(0)
        
        # Return the file as a response
        response = send_file(
            file_stream,
            mimetype=pdf_file.content_type,
            as_attachment=True,
            download_name=pdf_file.filename
        )

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 404

    
def delete_pdf(file_id, grid_fs):
    try:
        # Delete the file from GridFS
        grid_fs.delete(ObjectId(file_id))
        
        return jsonify({"message": "File deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 404


def generate_polynomial(t, constant_term, order):
    """Generate a polynomial of degree t-1 with a constant term and random coefficients."""
    coefficients = [constant_term] + [randrange(order) for _ in range(1, t)]
    return coefficients


def evaluate_polynomial(coefficients, x, order):
    """Evaluate a polynomial at a given x modulo the order."""
    return sum(c * pow(x, i) for i, c in enumerate(coefficients)) % order

def mod_inv(a, m):
    return pow(a, -1, m)

def is_point_on_curve(x, y, curve):
  """Check if a point lies on the given elliptic curve."""
#   if point is None:
#       return True  # Identity point
  x, y = x, y
  return (y**2 - x**3 - SECP256k1.curve.a() * x - SECP256k1.curve.b()) % SECP256k1.curve.p() == 0

def add_points(x0, y0, x1, y1, a, p):
    while y1 < 0:
        y1 = y1 + p

    if x0 == x1 and y0 == y1:
        Lambda = (3 * x0 * x0 + a) * mod_inv(2 * y0, p)
    else:
        if x0 == x1:
            return PatInf
        elif [x0, y0] == PatInf:
            return x1, y1
        elif [x1, y1] == PatInf:
            return x0, y0
        else:
            Lambda = (y1 - y0) * mod_inv(x1 - x0, p)

    x2 = (Lambda * Lambda - x0 - x1) % p
    y2 = ((x0 - x2) * Lambda - y0) % p
    if (point_is_valid(G, x2, y2)):
        print("Point on curve")
    else:
        print("Error: Point not on curve")
    res = Point(curve, x2, y2)
    return res


def compute_public_keys(shares, G):
    """Compute public keys for each party."""
    public_keys = []
    for poly in polynomials:
        secret = poly[0]
        public_keys.append(secret * G)

    return public_keys

def compute_overall_public_key(public_keys): 
    Q = public_keys[0]
    for i in range(1, len(public_keys)):
        Q = add_points(Q.x(), Q.y(), public_keys[i].x(), public_keys[i].y(), a, p)

    return Q

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

        recon_key += (sub_secret_share[j - 1] * int(mult)) % order

    return recon_key % order


def encrypt(pub_key, message):
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
    C1 = k * G
    H = k * pub_key

    C2 = (message + H.y())

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

    message = (C2 - H.y())

    return message

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

        recon_key += (sub_secret_share[j - 1] * int(mult)) % order

    return recon_key % order

def string_to_fernet_key(input_string):
    # Hash the string using SHA256 to ensure it's 32 bytes long
    hash_bytes = hashlib.sha256(input_string.encode()).digest()
    
    # Take the first 32 bytes and encode them in URL-safe base64
    fernet_key = base64.urlsafe_b64encode(hash_bytes[:32])
    
    return fernet_key

# def int_to_fernet_key_large(number: int) -> str:
#     # Convert the integer to bytes
#     num_bytes = number.to_bytes((number.bit_length() + 7) // 8, 'big')
    
#     # If too large, truncate or pad to 32 bytes
#     if len(num_bytes) > 32:
#         num_bytes = num_bytes[:32]
#     else:
#         num_bytes = num_bytes.rjust(32, b'\x00')  # Pad to 32 bytes
    
#     # Base64 encode in a URL-safe manner
#     key = base64.urlsafe_b64encode(num_bytes).decode('utf-8')
#     return key


def int_to_fernet_key(value):
    """
    Convert an integer back to a Fernet key (URL-safe base64).
    """
    # Convert the integer to bytes
    key_bytes = value.to_bytes((value.bit_length() + 7) // 8, byteorder='big')
    # Encode bytes to a URL-safe base64 string
    return base64.urlsafe_b64encode(key_bytes).decode('utf-8')


def keygen():
    key = Fernet.generate_key()

    return key

def encrypt_file(pdf_file, key):

    fernet = Fernet(key)

    print(type(pdf_file))

    # opening the original file to encrypt
    original = pdf_file.read()

    # encrypting the file
    encrypted = fernet.encrypt(original)

    file_stream = io.BytesIO(encrypted)

    # Create a custom FileStorage object
    new_file = FileStorage(
        stream=file_stream,
        filename="encrypted_file.pdf",
        content_type="application/pdf"
    )

    return new_file

def decrypt_file(pdf_file, key):
  
  # initialize the Fernet class
  try:
    fernet = (Fernet(int_to_string(key)))

    # encrypted data 
    encrypted_data = pdf_file.read()
    print("Encrypted Data", encrypted_data)

    decrypted = fernet.decrypt(encrypted_data)

    print("Decrypted Data ", decrypted)
    
    file_stream = io.BytesIO(decrypted)

    # Create a custom FileStorage object
    new_file = FileStorage(
        stream=file_stream,
        filename="decrypted_file.pdf",
        content_type="application/pdf"
    )

    return new_file

  except fernet.InvalidToken as e:
    print(e)
  except TypeError as e:
    print(e)
  except Exception as e:
        print(e)

#   print(pdf_file)

  # encryted data 
#   encrypted_data = pdf_file.read()
#   print(encrypted_data)
#   print(pdf_file)

  # decrypt the data
#   decrypted_data = fernet.decrypt(encrypted_data)

  # opening the encrypted file
#   with open(filename, 'wb') as dec_file:
#         dec_file.write(decrypted_data)

def hex_to_point(hex_public_key):
    """
    Convert a public key in hex format to a point on the elliptic curve.

    :param hex_public_key: The public key in hex format (uncompressed format).
    :return: Point on the elliptic curve.
    """
    # curve = SECP256k1.curve  # Ensure the curve matches the one used in React

    # Validate and parse the hex public key
    if len(hex_public_key) != 130 or not hex_public_key.startswith("04"):
        raise ValueError("Invalid uncompressed public key format")

    # Extract x and y coordinates from the hex string
    x = int(hex_public_key[2:66], 16)  # First 64 characters after "04" are x
    y = int(hex_public_key[66:], 16)   # Next 64 characters are y

    # Verify the point lies on the curve
    if not curve.contains_point(x, y):
        raise ValueError("The public key coordinates are not on the curve")

    return Point(curve, x, y)


def point_to_hex(point):
    """
    Converts an ECDSA point (x, y) to the hex format compatible with elliptic library.
    :param point: An elliptic curve point with x and y coordinates.
    :return: Hexadecimal string of the uncompressed public key.
    """
    x = point.x()
    y = point.y()

    # Convert x and y coordinates to hexadecimal
    x_hex = format(x, '064x')  # 32-byte (64 hex chars) representation
    y_hex = format(y, '064x')  # 32-byte (64 hex chars) representation

    # Concatenate with the prefix for uncompressed public keys
    return f"04{x_hex}{y_hex}"
