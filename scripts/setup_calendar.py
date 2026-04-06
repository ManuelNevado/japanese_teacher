#!/usr/bin/env python3
"""
setup_calendar.py
-----------------
Configura las credenciales de la API de Google Calendar para la escuela de japonés.
Ejecuta este script una sola vez para autorizar el acceso a tu Google Calendar.

Requisitos:
    pip install google-auth-oauthlib google-api-python-client

Pasos:
    1. Ve a https://console.cloud.google.com/
    2. Crea un proyecto nuevo (o usa uno existente)
    3. Activa la API "Google Calendar API"
    4. Crea credenciales OAuth 2.0 (tipo: Desktop App)
    5. Descarga el JSON de credenciales como 'credentials.json' en la raíz del proyecto
    6. Ejecuta: python3 scripts/setup_calendar.py
"""

import os
import sys
import json
from pathlib import Path

# --- Dependencia de Google ---
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Faltan dependencias. Instálalas con:")
    print("   pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)

# --- Configuración ---
SCOPES = ['https://www.googleapis.com/auth/calendar']
PROJECT_ROOT = Path(__file__).parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / 'credentials.json'
TOKEN_DIR = Path.home() / '.config' / 'japanese_teacher'
TOKEN_FILE = TOKEN_DIR / 'calendar_token.json'


def setup_calendar():
    """Autoriza el acceso a Google Calendar y guarda el token."""
    print("🎌 Escuela de Japonés — Configuración de Google Calendar")
    print("=" * 55)

    # Verificar que existe el archivo de credenciales
    if not CREDENTIALS_FILE.exists():
        print(f"\n❌ No encuentro el archivo de credenciales OAuth.")
        print(f"   Esperado en: {CREDENTIALS_FILE}")
        print("\n📋 Pasos para obtenerlo:")
        print("   1. Ve a: https://console.cloud.google.com/apis/credentials")
        print("   2. Crea credenciales → OAuth 2.0 → Aplicación de escritorio")
        print("   3. Descarga el JSON y guárdalo como 'credentials.json' en la raíz del proyecto")
        print(f"   4. Ruta correcta: {CREDENTIALS_FILE}")
        sys.exit(1)

    # Crear directorio de token si no existe
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)

    creds = None

    # Cargar token existente si hay
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            print(f"✅ Token existente encontrado en {TOKEN_FILE}")
        except Exception:
            print("⚠️  Token existente es inválido — re-autorizando...")
            creds = None

    # Refrescar o crear nuevo token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refrescando token expirado...")
            creds.refresh(Request())
        else:
            print("\n🌐 Abriendo navegador para autorización de Google...")
            print("   Inicia sesión con tu cuenta de Google y concede acceso a Calendar.")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # Guardar el token para uso futuro
        TOKEN_FILE.write_text(creds.to_json())
        print(f"\n✅ Token guardado en: {TOKEN_FILE}")

    # Verificar conexión con la API
    try:
        service = build('calendar', 'v3', credentials=creds)
        calendar = service.calendars().get(calendarId='primary').execute()
        print(f"\n✅ Conectado exitosamente al calendario: {calendar['summary']}")
        print(f"   Zona horaria: {calendar.get('timeZone', 'No especificada')}")
    except Exception as e:
        print(f"\n❌ Error al conectar con Google Calendar: {e}")
        sys.exit(1)

    # Actualizar student.json con timezone si no está configurado
    student_file = PROJECT_ROOT / 'data' / 'progress' / 'student.json'
    if not student_file.exists():
        template_file = PROJECT_ROOT / 'data' / 'progress' / 'student_template.json'
        if template_file.exists():
            import shutil
            shutil.copy(template_file, student_file)
            print(f"\n📁 Perfil de estudiante creado en: {student_file}")
            print("   Ejecuta ./scripts/init_student.sh para personalizar tu perfil.")

    print("\n🎉 ¡Configuración completada!")
    print("=" * 55)
    print("Ahora puedes usar la integración con Google Calendar.")
    print("Próximo paso: python3 scripts/schedule_lesson.py --help")


if __name__ == '__main__':
    setup_calendar()
