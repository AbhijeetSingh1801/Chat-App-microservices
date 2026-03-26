import jwt, datetime, os

import bcrypt
import pymysql
from flask import Flask, jsonify, request


server = Flask(__name__)

DB_CONFIG = {
    "host":   os.environ.get("MYSQL_HOST"),
    "user":   os.environ.get("MYSQL_USER"),
    "password": os.environ.get("MYSQL_PASSWORD"),
    "db":     os.environ.get("MYSQL_DB"),
    "port":   int(os.environ.get("MYSQL_PORT", 3306)),
    "cursorclass": pymysql.cursors.Cursor,
}


@server.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "bad_request", "detail": "JSON body required"}), 400

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "bad_request", "detail": "email and password are required"}), 400

    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    con = pymysql.connect(**DB_CONFIG)
    try:
        with con.cursor() as cur:
            cur.execute(
                "INSERT INTO user (email, password) VALUES (%s, %s)", (email, pw_hash)
            )
            con.commit()
    except pymysql.err.IntegrityError:
        return jsonify({"error": "conflict", "detail": "email already registered"}), 409
    finally:
        con.close()

    return jsonify({"message": "user registered"}), 201


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return jsonify({"error": "unauthorized", "detail": "missing credentials"}), 401

    con = pymysql.connect(**DB_CONFIG)
    try:
        with con.cursor() as cur:
            res = cur.execute(
                "SELECT email, password FROM user WHERE email=%s", (auth.username,)
            )
            if res > 0:
                user_row = cur.fetchone()
                email, pw_hash = user_row[0], user_row[1]
                if not bcrypt.checkpw(auth.password.encode("utf-8"), pw_hash.encode("utf-8")):
                    return jsonify({"error": "unauthorized", "detail": "invalid credentials"}), 401
                return createJWT(email, os.environ.get("JWT_SECRET"), True)
    finally:
        con.close()

    return jsonify({"error": "unauthorized", "detail": "invalid credentials"}), 401


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "email": username,
            "authz": authz,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
        },
        secret,
        algorithm="HS256",
    )


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")
    if not encoded_jwt:
        return jsonify({"error": "unauthorized", "detail": "missing token"}), 401

    if not encoded_jwt.startswith("Bearer "):
        return jsonify({"error": "unauthorized", "detail": "invalid token format"}), 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt,
            os.environ.get("JWT_SECRET"),
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "unauthorized", "detail": "token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "unauthorized", "detail": "invalid token"}), 401

    return jsonify(decoded), 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
