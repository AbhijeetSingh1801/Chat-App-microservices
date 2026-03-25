import jwt, datetime, os

import pymysql
from flask import Flask, request


server = Flask(__name__)

DB_CONFIG = {
    "host":   os.environ.get("MYSQL_HOST"),
    "user":   os.environ.get("MYSQL_USER"),
    "password": os.environ.get("MYSQL_PASSWORD"),
    "db":     os.environ.get("MYSQL_DB"),
    "port":   int(os.environ.get("MYSQL_PORT", 3306)),
    "cursorclass": pymysql.cursors.Cursor,
}


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401 

    con = pymysql.connect(**DB_CONFIG)
    try:
        with con.cursor() as cur:
            res = cur.execute(
                "SELECT email, password FROM user WHERE email=%s", (auth.username,)
            )
            if res > 0:
                user_row = cur.fetchone()
                email, password = user_row[0], user_row[1]
                if auth.username != email or auth.password != password:
                    return "invalid credentials", 401
                return createJWT(email, os.environ.get("JWT_SECRET"), True)
    finally:
        con.close()

    return "invalid credentials", 401


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
        return "missing token", 401

    if not encoded_jwt.startswith("Bearer "):
        return "invalid token format", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt,
            os.environ.get("JWT_SECRET"),
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        return "token expired", 401
    except jwt.InvalidTokenError:
        return "invalid token", 401

    from flask import jsonify
    return jsonify(decoded), 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
