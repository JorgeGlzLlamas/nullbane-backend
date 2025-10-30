from sqlalchemy import create_engine, text
from app.core.settings import settings
import sys

print("Intentando conectar a la base de datos...")
print(f"URL: {str(settings.DATABASE_URL)}")

try:
    engine = create_engine(str(settings.DATABASE_URL))

    # 2. Intentar conectar y ejecutar una consulta simple
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(f"Resultado de 'SELECT 1': {result.fetchone()}")
    
    print("\n✅ ¡Conexión exitosa!")
    print("La configuración en .env y app/core/settings.py es correcta.")

except Exception as e:
    print(f"\n❌ ERROR: No se pudo conectar a la base de datos.")
    print(f"Detalle del error:\n{e}")
    sys.exit(1) # Salir con código de error