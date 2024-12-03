from flask import Flask, request, jsonify, send_file, make_response
from flask_pymongo import PyMongo
from gridfs import GridFS
from werkzeug.utils import secure_filename
from bson import ObjectId
from dotenv import dotenv_values
import io

from ecdsa.ellipticcurve import CurveFp, Point
from ecdsa.numbertheory import inverse_mod
from ecdsa.util import randrange

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
    app.config["MONGO_URI"] = secrets["MONGO_URI"]

    print("Connecting to MongoDB...")

    mongo = PyMongo(app)
    db = mongo.db
    return (app, db)

def upload_pdf(pdf_file, grid_fs):
    try:
        # Save the file to GridFS
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

def compute_overall_public_key(public_keys, G): 
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
    return round(message)



# Example Usage
t = 3  # Threshold
n = 5  # Number of shares
mess = 67432278 # Example message
# message = string_to_point(curve, str(mess), hashlib.sha256)

# Generate shares
polynomials = [
    generate_polynomial(t, randrange(order), order) for _ in range(n)
]
shares = [[evaluate_polynomial(poly, x + 1, order) for x in range(n)]
          for poly in polynomials]

# Compute cumulative shares (scalar value)
cumulative_shares = [
    sum(share[i] for share in shares) % order for i in range(n)
]

# Compute public keys (point addition)
public_keys = compute_public_keys(shares, G)

# Combine public keys
# overall_public_key = public_keys[0]
# for pub_key in public_keys[1:]:
    # overall_public_key = add_points(overall_public_key, pub_key, a, p)

#Overall public key 
overall_public_key = compute_overall_public_key(public_keys, G)

# Print results
print("Polynomials:", polynomials)
print("Shares:", shares)
print("Cumulative Shares:", cumulative_shares)
print("Public Keys:", [(pk.x(), pk.y()) for pk in public_keys])
print("Overall Public Key:", (overall_public_key.x(), overall_public_key.y()))
print("Message:", mess)

# Working fine
reconstructed_key = reconstruct_key(cumulative_shares, t, order)
