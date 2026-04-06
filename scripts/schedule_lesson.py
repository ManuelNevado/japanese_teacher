#!/usr/bin/env python3
"""
schedule_lesson.py
------------------
Crea un evento de estudio de japonés en Google Calendar.
Invocado por los agentes al final de cada lección para programar la siguiente sesión.

Uso:
    python3 scripts/schedule_lesson.py \\
        --title "Estudio Japonés — Partículas は y が" \\
        --duration 30 \\
        --content "Aprenderemos las partículas は y が con ejercicios prácticos" \\
        --objective "Distinguir cuándo usar は vs が en oraciones simples" \\
        --type vocabulary   # grammar | vocabulary | kanji | quiz | conversation
        --date 2024-01-16   # Opcional: si no se da, usa el próximo día laborable
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, date
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("❌ Faltan dependencias. Ejecuta: pip install google-api-python-client google-auth")
    sys.exit(1)

# --- Configuración ---
PROJECT_ROOT = Path(__file__).parent.parent
TOKEN_FILE = Path.home() / '.config' / 'japanese_teacher' / 'calendar_token.json'
STUDENT_FILE = PROJECT_ROOT / 'data' / 'progress' / 'student.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Colores de evento por tipo de lección
EVENT_COLORS = {
    'grammar':      '9',   # Blueberry
    'vocabulary':   '2',   # Sage (verde)
    'kanji':        '3',   # Grape (morado)
    'quiz':         '5',   # Banana (amarillo)
    'conversation': '11',  # Tomato (rojo)
    'review':       '1',   # Lavanda
    'default':      '2',   # Sage
}

# Emojis por tipo
EMOJIS = {
    'grammar': '📖',
    'vocabulary': '🗃',
    'kanji': '✍️',
    'quiz': '📝',
    'conversation': '💬',
    'review': '🔄',
    'default': '🎌',
}


def load_student_config():
    """Carga la configuración del estudiante."""
    if STUDENT_FILE.exists():
        with open(STUDENT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('calendar_settings', {})
    return {
        'default_study_time': '07:00',
        'study_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
        'calendar_id': 'primary',
        'timezone': 'Europe/Madrid',
        'reminder_minutes': 10,
    }


def next_study_day(config, from_date=None):
    """Calcula el próximo día de estudio según la configuración."""
    if from_date is None:
        from_date = date.today() + timedelta(days=1)

    day_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2,
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }
    study_days_nums = {day_map[d] for d in config.get('study_days', ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])}

    check = from_date
    for _ in range(14):  # máximo 2 semanas adelante
        if check.weekday() in study_days_nums:
            return check
        check += timedelta(days=1)

    return from_date + timedelta(days=1)  # fallback


def get_calendar_service():
    """Autentifica y devuelve el servicio de Google Calendar."""
    if not TOKEN_FILE.exists():
        print("❌ No hay token de autenticación.")
        print("   Ejecuta primero: python3 scripts/setup_calendar.py")
        sys.exit(1)

    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if not creds.valid:
            from google.auth.transport.requests import Request
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                TOKEN_FILE.write_text(creds.to_json())
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Error de autenticación: {e}")
        print("   Ejecuta: python3 scripts/setup_calendar.py")
        sys.exit(1)


def create_study_event(args):
    """Crea el evento de estudio en Google Calendar."""
    config = load_student_config()
    timezone = config.get('timezone', 'Europe/Madrid')
    tz = ZoneInfo(timezone)

    # Determinar fecha
    if args.date:
        event_date = datetime.strptime(args.date, '%Y-%m-%d').date()
    else:
        event_date = next_study_day(config)

    # Determinar hora
    study_time = args.start_time or config.get('default_study_time', '07:00')
    hour, minute = map(int, study_time.split(':'))

    # Construir datetimes
    start_dt = datetime(event_date.year, event_date.month, event_date.day,
                        hour, minute, tzinfo=tz)
    end_dt = start_dt + timedelta(minutes=args.duration)

    # Tipo de lección
    lesson_type = args.type or 'default'
    emoji = EMOJIS.get(lesson_type, '🎌')
    color_id = EVENT_COLORS.get(lesson_type, '2')

    # Construir título
    title = args.title or f"🎌 Estudio Japonés — Sesión N5"
    if not title.startswith('🎌') and not title.startswith(emoji):
        title = f"{emoji} {title}"

    # Construir descripción rica
    description_parts = [
        f"🎌 Escuela de Japonés — Nivel JLPT N5",
        f"",
        f"📚 Contenido: {args.content or 'Sesión de estudio de japonés'}",
        f"⏱ Duración estimada: {args.duration} minutos",
    ]
    if args.objective:
        description_parts.append(f"🎯 Objetivo: {args.objective}")
    if args.preparation:
        description_parts.append(f"📋 Preparación: {args.preparation}")

    description_parts.extend([
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"Tipo de sesión: {lesson_type.capitalize()}",
        f"Agendado por: Sensei AI 🤖",
        f"",
        f"がんばってください！ (¡Esfuérzate!)",
    ])
    description = "\n".join(description_parts)

    # Crear el evento
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': timezone,
        },
        'colorId': color_id,
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': config.get('reminder_minutes', 10)},
            ],
        },
    }

    # Insertar en Google Calendar
    service = get_calendar_service()
    calendar_id = config.get('calendar_id', 'primary')

    try:
        created_event = service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()

        # Mostrar confirmación
        day_names_es = {
            0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
            4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
        }
        day_name = day_names_es[event_date.weekday()]

        print("\n" + "=" * 50)
        print("📅 SESIÓN AGENDADA EN GOOGLE CALENDAR")
        print("=" * 50)
        print(f"📌 {title}")
        print(f"📆 {day_name} {event_date.strftime('%d/%m/%Y')} a las {study_time}")
        print(f"⏱ Duración: {args.duration} minutos")
        if args.content:
            print(f"📚 Contenido: {args.content}")
        if args.objective:
            print(f"🎯 Objetivo: {args.objective}")
        print(f"\n🔗 Ver evento: {created_event.get('htmlLink', 'N/A')}")
        print("=" * 50)
        print("\n¡Hasta entonces, がんばって！🎌\n")

        # Registrar en historial del estudiante
        log_scheduled_session(event_date, args.duration, lesson_type, args.content or '')

        return created_event

    except HttpError as e:
        print(f"❌ Error al crear el evento: {e}")
        # Mostrar datos del evento para creación manual
        print("\n📋 Crea el evento manualmente con estos datos:")
        print(f"   Título: {title}")
        print(f"   Fecha: {event_date} a las {study_time}")
        print(f"   Duración: {args.duration} minutos")
        sys.exit(1)


def log_scheduled_session(event_date, duration, lesson_type, content):
    """Registra la sesión agendada en el historial del estudiante."""
    if not STUDENT_FILE.exists():
        return
    try:
        with open(STUDENT_FILE, 'r', encoding='utf-8') as f:
            student = json.load(f)
        if 'session_history' not in student:
            student['session_history'] = []
        student['session_history'].append({
            'scheduled_date': event_date.isoformat(),
            'scheduled_duration_minutes': duration,
            'type': lesson_type,
            'content': content,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        })
        with open(STUDENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(student, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # No crítico si falla el logging


def main():
    parser = argparse.ArgumentParser(
        description='Agenda una sesión de estudio de japonés en Google Calendar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Sesión de gramática mañana a las 7am (30 min)
  python3 scripts/schedule_lesson.py \\
      --title "Partículas は y が" \\
      --duration 30 \\
      --type grammar \\
      --objective "Distinguir は y が en contexto"

  # Sesión de vocabulario en fecha específica
  python3 scripts/schedule_lesson.py \\
      --title "Vocabulario de la casa" \\
      --duration 20 \\
      --type vocabulary \\
      --date 2024-01-20 \\
      --start-time "08:00"
        """
    )

    parser.add_argument('--title', help='Título de la sesión (ej: "Partículas は y が")')
    parser.add_argument('--duration', type=int, default=30,
                        help='Duración en minutos (default: 30)')
    parser.add_argument('--content', help='Descripción del contenido de la lección')
    parser.add_argument('--objective', help='Objetivo de aprendizaje de la sesión')
    parser.add_argument('--preparation', help='Preparación necesaria antes de la sesión')
    parser.add_argument('--type', choices=['grammar', 'vocabulary', 'kanji', 'quiz', 'conversation', 'review'],
                        default='default', help='Tipo de sesión (afecta el color del evento)')
    parser.add_argument('--date', help='Fecha del evento en formato YYYY-MM-DD (default: próximo día laborable)')
    parser.add_argument('--start-time', dest='start_time',
                        help='Hora de inicio en formato HH:MM (default: 07:00)')

    args = parser.parse_args()
    create_study_event(args)


if __name__ == '__main__':
    main()
