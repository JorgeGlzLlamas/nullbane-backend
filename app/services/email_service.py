from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.settings import settings
import random
import string

# Configuración de FastAPI-Mail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TIMEOUT=30
)

def generate_otp_code(length: int = 6) -> str:
    """Genera un código numérico de 6 dígitos."""
    return ''.join(random.choices(string.digits, k=length))

async def send_password_reset_email(email_to: str, code: str):
    """Envía el correo con el código."""
    
    html = f"""
    <h3>Recuperación de Contraseña</h3>
    <p>Usa el siguiente código para restablecer tu contraseña:</p>
    <h1 style="color: #4A90E2; letter-spacing: 5px;">{code}</h1>
    <p>Este código expira en 15 minutos.</p>
    <p>Si no solicitaste esto, ignora este correo.</p>
    """

    message = MessageSchema(
        subject="Tu código de recuperación - Nullbane",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
