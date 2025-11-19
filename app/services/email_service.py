import resend
from app.core.settings import settings
import random
import string

# Configurar la API Key
resend.api_key = settings.RESEND_API_KEY

def generate_otp_code(length: int = 6) -> str:
    """Genera un código numérico de 6 dígitos."""
    return ''.join(random.choices(string.digits, k=length))

def send_password_reset_email(email_to: str, code: str):
    """
    Envía el correo usando la API de Resend.
    NOTA: Es una llamada síncrona rápida, no bloqueará mucho tu API.
    """
    
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Recuperación de Contraseña</h2>
        <p>Usa el siguiente código para restablecer tu contraseña en Nullbane:</p>
        <div style="background-color: #f4f4f4; padding: 20px; text-align: center; border-radius: 5px;">
            <h1 style="color: #000; letter-spacing: 5px; margin: 0;">{code}</h1>
        </div>
        <p style="color: #666; font-size: 12px; margin-top: 20px;">Este código expira en 15 minutos.</p>
    </div>
    """

    try:
        params = {
            "from": "Nullbane <onboarding@resend.dev>", # Usa este remitente por defecto
            "to": [email_to],
            "subject": "Código de Recuperación",
            "html": html_content
        }

        email = resend.Emails.send(params)
        print(f"✅ Correo enviado ID: {email.id}")
        return email

    except Exception as e:
        print(f"❌ Error enviando correo Resend: {e}")
        # No lanzamos error para no romper el flujo del usuario, pero lo logueamos