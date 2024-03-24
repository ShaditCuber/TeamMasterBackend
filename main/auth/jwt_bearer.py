from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.http import HTTPAuthorizationCredentials
from starlette.requests import Request
from .jwt_handler import decodeJWT


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No se ha proporcionado un código de Bearer Token.",
                )

            payload = decodeJWT(credentials.credentials)
            # print(payload, "PAYLOAD")
            if "error_code" in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=payload["detail"],
                )

            return credentials.credentials

        else:
            raise HTTPException(
                status_code=403, detail="Código de autorización no válido."
            )

    # def verify_jwt(self, jwtToken: str) -> bool:
    #     # print("verifying token")
    #     isTokenValid: bool = False
    #     try:
    #         payload = decodeJWT(jwtToken)
    #     except Exception:
    #         payload = None
    #     # print(payload)

    #     # if payload == 0:
    #     #     raise HTTPException(status_code=401, detail="Token ha Caducado.")

    #     if payload and payload != -1:
    #         isTokenValid = True

    #     return isTokenValid


# from fastapi import Request, HTTPException
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.security.http import HTTPAuthorizationCredentials
# from starlette.requests import Request
# from .jwt_handler import decodeJWT


# class JWTBearer(HTTPBearer):
#     def __init__(self, auto_error: bool = True):
#         super(JWTBearer, self).__init__(auto_error=auto_error)

#     async def __call__(self, request: Request):
#         credentials: HTTPAuthorizationCredentials = await super(
#             JWTBearer, self
#         ).__call__(request)
#         if credentials:
#             if not credentials.scheme == "Bearer":
#                 print("No se ha proporcionado un código de Bearer Token.")
#                 raise HTTPException(
#                     status_code=403, detail="Token no válido o token caducado."
#                 )

#             # try:
#             if not self.verify_jwt(credentials.credentials):
#                 raise HTTPException(status_code=403, detail="Token no válido.")
#             # except Exception as e:
#             #     print(e,'XDDDD')
#             #     raise HTTPException(status_code=401, detail="Token ha caducado.")

#             return credentials.credentials

#         else:
#             raise HTTPException(
#                 status_code=403, detail="Código de autorización no válido."
#             )

#     def verify_jwt(self, jwtToken: str) -> bool:
#         # print("verifying token")
#         isTokenValid: bool = False
#         try:
#             payload = decodeJWT(jwtToken)
#         except Exception:
#             payload = None
#         # print(payload)

#         # if payload == 0:
#         #     raise HTTPException(status_code=401, detail="Token ha Caducado.")
#         print(payload, "PAYLOAD")
#         if payload and payload != -1:
#             isTokenValid = True

#         return isTokenValid
