import jwt

# import boto3
import json
import time
import datetime
from decouple import config

# from util.util import get_user_by_id_amplify


# def get_secret(secret_name: str = "SecretJWT"):
#     session = boto3.session.Session()
#     client = session.client(service_name="secretsmanager", region_name="us-east-1")

#     try:
#         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
#     except Exception as e:
#         raise e

#     secret = get_secret_value_response["SecretString"]

#     return json.loads(secret)


JWT_ALGORITHM = config("ALGORITHM")
JWT_ID = config("ID")


def token_response(token: str):
    return {"token de acceso": token}


def decodeJWT(token: str) -> dict:
    try:
        decoded = jwt.decode(
            token, algorithms=[JWT_ALGORITHM], options={"verify_signature": False}
        )

        sub = decoded.get("sub")

        expiration = decoded.get("exp")

        if expiration < int(time.time()):
            # print('CADUCADO')
            return {"error_code": "TOKEN_EXPIRED", "detail": "Token ha caducado"}

        # print(decoded["iss"].split("/")[-1])
        if decoded["iss"].split("/")[-1] != JWT_ID:
            # print('ADULTERADO')
            return {"error_code": "INVALID" , "detail": "Token Adulterado"}

        return {"sub": sub, "username": decoded.get("username")}

    except jwt.ExpiredSignatureError:
        return {"error_code": "TOKEN_EXPIRED", "detail": "Token ha caducado"}

    except jwt.InvalidTokenError:
        return {"error_code": "INVALID_TOKEN", "detail": "Token no válido"}

    except Exception as e:
        print(e)
        return {"error_code": "UNKNOWN_ERROR", "detail": "Error desconocido"}


# def decodeJWT(token: str) -> dict:
#     try:
#         # print("decoding token", token)
#         decoded = jwt.decode(
#             token, algorithms=[JWT_ALGORITHM], options={"verify_signature": False}
#         )
#         # print(decoded, "DECODED")

#         sub = decoded.get("sub")
#         # print(sub, "SUB")
#         # if sub == "aa20c105-ca66-43a2-9dfa-58349da1b544":
#         #     return True

#         # existing_user = get_user_by_id_amplify(sub)
#         expiration = decoded.get("exp")
#         expiration_Date = datetime.datetime.fromtimestamp(expiration).strftime(
#             "%Y-%m-%d %H:%M:%S"
#         )
#         # print(expiration_Date, "EXPIRATION DATE")
#         if expiration < int(time.time()):
#             # return 0
#             return None
#         # return (existing_user or decoded['iss'].split('/')[-1] == JWT_ID)
#         # print(JWT_ID)
#         # print(decoded["iss"].split("/")[-1] == JWT_ID)
#         return decoded["iss"].split("/")[-1] == JWT_ID

#     except Exception as e:
#         print(e,'Error en jwt_handler.py')
#         return None


def get_user_id_from_token(token: str) -> str:
    try:
        decoded = jwt.decode(
            token, algorithms=[JWT_ALGORITHM], options={"verify_signature": False}
        )
        return decoded.get("sub"), decoded.get("username")
    except Exception as e:
        return None
