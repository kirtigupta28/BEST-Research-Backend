from flask import Flask, request, jsonify, send_file, make_response
from flask_pymongo import PyMongo
from gridfs import GridFS
from werkzeug.utils import secure_filename
from bson import ObjectId
from dotenv import dotenv_values
import io
from flask_cors import CORS, cross_origin
from binascii import unhexlify

from ecdsa.ellipticcurve import CurveFp, Point
from ecdsa.numbertheory import inverse_mod
from ecdsa.util import randrange
from cryptography.fernet import Fernet
from ecdsa.curves import SECP256k1

# from utils import int_to_urlsafe_base64, point_to_urlsafe_base64

import hashlib
from ecdsa.ellipticcurve import CurveFp, Point

# Custom curve parameters
p = 17  # Prime modulus
a = 2  # Curve coefficient a
b = 2  # Curve coefficient b
order = 19  # Order of the curve
PatInf = [0, 0] #define "Point at Infinity"


# Define the custom curve
curve = CurveFp(p, a, b)

# Define the generator point (on the curve)
G = Point(curve, 5, 1, order)


secrets = dotenv_values(".env")

def connect_db(): 

    app = Flask(__name__)
    CORS(app)
    app.config["MONGO_URI"] = secrets["MONGO_URI"]

    print("Connecting to MongoDB...")

    mongo = PyMongo(app)
    db = mongo.db
    return (app, db)

def upload_pdf(pdf_file, grid_fs):
    try:
        # Save the file to GridFS
        print(pdf_file)
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
    return pow(a, -1, m) #since python 3.8 (demonstrated in last video with extended euclidean in C)

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
    return Point(curve, x2, y2, order)


def compute_public_keys(shares, G):
    """Compute public keys for each party."""
    public_keys = []
    for poly in polynomials:
        secret = poly[0]
        public_keys.append(secret * G)

    return public_keys

def compute_overall_public_key(public_keys, G=SECP256k1.generator): 
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


def encrypt(pub_key, message, G=SECP256k1.generator, order=SECP256k1.order):
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


def keygen():
    key = Fernet.generate_key()

    return key

def encrypt_file(pdf_file, key):

    fernet = Fernet(key)

    # opening the original file to encrypt
    original = pdf_file.read()

    # encrypting the file
    encrypted = fernet.encrypt(original)

    # opening the file in write mode and
    # writing the encrypted data
    with open(pdf_file.filename, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

def decrypt_file(filename, key):

  # initialize the Fernet class

  fernet = (Fernet(key))

  # opening the encrypted file
  with open(filename+"_encrypted", 'rb') as enc_file:
    encrypted = enc_file.read()

  # decrypting the file
  decrypted = fernet.decrypt(encrypted)

  # opening the file in write mode and
  # writing the decrypted data
  with open(filename+"_decrypted", 'wb') as dec_file:
    dec_file.write(decrypted)

def hex_to_point(hex_public_key):
    """
    Convert a public key in hex format to a point on the elliptic curve.

    :param hex_public_key: The public key in hex format (uncompressed format).
    :return: Point on the elliptic curve.
    """
    curve = SECP256k1.curve  # Ensure the curve matches the one used in React

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
