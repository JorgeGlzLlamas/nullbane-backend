from sqlmodel import SQLModel

class Token(SQLModel):
    """
    Schema de respuesta para un inicio de sesión exitoso.
    Contiene el token de acceso y su tipo.
    """
    access_token: str
    refresh_token: str
    token_type: str


class AccessTokenOnly(SQLModel):
    """
    Schema de respuesta solo para el refresh.
    Devuelve ÚNICAMENTE el nuevo access token.
    """
    access_token: str
    token_type: str


class RefreshRequest(SQLModel):
    refresh_token: str


class PromoteRequest(SQLModel):
    """
    Schema de entrada para la petición de promoción a admin.
    """
    secret_key: str
