import os
import hmac
import hashlib
import datetime
import base64
import rsa
import json
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
from Crypto.Cipher import AES, PKCS1_OAEP
from flask import jsonify
from flask import Flask
from flask import jsonify
from flask import request

import requests
import boto3

app = Flask(__name__)

configuration_items = [
    "client_id",
    "client_secret",
    "scope",
    "password",
    "grant_type",
    "cognito_url",
    "aws_region"
]

for configuration_item in configuration_items:
    configuration_item_value = os.environ.get(configuration_item)
    app.config[configuration_item] = configuration_item_value


@app.route("/auth", methods=["GET", "POST"])
def authenticate():
    if not request.is_json:
        return jsonify({"message": "Invalid request"})
    content = request.json
    print(content)

    f = open('./encryption/rsa_private.pem', 'rb')
    key = RSA.importKey(f.read())
    f.close()

    signature = content["signature"]
    print("signature===", str(signature))
    print("sig ==== ", signature.encode())
    # Decryption----
    cipher = PKCS1_OAEP.new(key)

    decoded = base64.b64decode(signature.encode())
    print("decoded ====", decoded)
    # decrypt
    plain_text = cipher.decrypt(decoded)

    output = json.loads(plain_text.decode('utf-8'))
    detime = datetime.datetime.strptime(output['expiresAt'], '%Y-%m-%d %H:%M:%S')
    detime = detime + datetime.timedelta(minutes=15)
    detime = detime.strftime("%Y-%m-%d %H:%M:%S")
    formatted_raw_message = f"{output['email']}|||{output['orgid']}|||{detime}"
    m = hmac.new(bytes(str(app.config.get("hmac_shared_secret")), "UTF-8"), digestmod=hashlib.blake2s)
    m.update(bytes(str(formatted_raw_message), "UTF-8"))
    digest = m.hexdigest()

    if output['digest'] == digest:
        return jsonify({"message": "Signature is invalid"})

    client = boto3.client("cognito-idp", region_name=app.config.get("aws_region"))
    username = str(output['email'])
    password = app.config.get("password")
    clientId = app.config.get("client_id")

    try:
        boto_response = client.initiate_auth(
            ClientId=clientId,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password})
        boto_response = boto_response.get("AuthenticationResult")
    except Exception as err:
        print(err)
        boto_response = "{'message': 'Invalid email address '}"

    return jsonify(boto_response);


@app.route("/auth/authorize", methods=["GET", "POST"])
def authorize():
    if not request.is_json:
        return jsonify({"message": "Invalid request"})
    content = request.json
    print(content)

    client = boto3.client("cognito-idp", region_name=app.config.get("aws_region", "us-east-1"))
    # org_id = app.config.get("orgid")
    signed_param = content["signature"]
    email = content["email"]
    orgid = content["orgid"]
    time = content["expiresAt"]
    formatted_raw_message = f"{email}|||{orgid}|||{time}"
    m = hmac.new(bytes(str(app.config.get("hmac_shared_secret")), "UTF-8"), digestmod=hashlib.blake2s)
    m.update(bytes(str(formatted_raw_message), "UTF-8"))
    digest = m.hexdigest()
    if signed_param != digest:
        print("Signature is invalid ")
        print(formatted_raw_message)
        print(digest)
        print(signed_param)
        return jsonify({"message": "Signature is invalid"})

    boto_params = {"USERNAME": content["email"], "PASSWORD": app.config.get("password")}

    try:
        boto_response = client.initiate_auth(
            ClientId=app.config.get("client_id"),
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters=boto_params,
        )
        boto_response = boto_response.get("AuthenticationResult")
    except Exception as err:
        print(err)
        boto_response = "{'message': 'Invalid email address '}"

    return jsonify(boto_response);


@app.route("/auth/hmac-signature", methods=["GET", "POST"])
def generate_hmac_signature():
    if not request.is_json:
        return jsonify({"message": "Invalid request"})
    content = request.json
    print(content)
    email = content["email"]
    orgid = content["orgid"]
    time = datetime.datetime.now() + datetime.timedelta(minutes=15)
    dt = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_raw_message = f"{email}|||{orgid}|||{dt}"

    m = hmac.new(bytes(str(app.config.get("hmac_shared_secret")), "UTF-8"), digestmod=hashlib.blake2s)
    m.update(bytes(str(formatted_raw_message), "UTF-8"))
    digest = m.hexdigest()
    return jsonify({"signature": digest, "expiresAt": dt});


@app.route("/auth/refresh", methods=["GET", "POST"])
def refresh_token():
    if not request.is_json:
        return jsonify({"message": "Invalid request"})
    content = request.json
    print(content)

    client = boto3.client("cognito-idp", region_name=app.config.get("aws_region", "us-east-1"))
    token = content["token"]

    boto_params = {"REFRESH_TOKEN": token}
    try:
        boto_response = client.initiate_auth(
            ClientId=app.config.get("client_id"),
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters=boto_params,
        )
        boto_response = boto_response.get("AuthenticationResult")
    except Exception as err:
        print(err)
        boto_response = "{'message': 'Invalid token '}"

    return jsonify(boto_response);


@app.route("/health")
def health():
    return "I am fine!";
