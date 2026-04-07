#!/bin/bash
# Auto-generado por setup_reminders.sh — no editar manualmente
PROJECT_ROOT="/home/manuel/japanese_teacher"
STUDENT_FILE="$PROJECT_ROOT/data/progress/student.json"

# Obtener tarjetas SRS pendientes
SRS_DUE=$(python3 -c "
import json
from datetime import date
try:
    with open('$STUDENT_FILE') as f:
        d = json.load(f)
    today = date.today().isoformat()
    due = sum(1 for c in d.get('srs_deck', []) if c.get('next_review', '9999') <= today)
    name = d['student']['name']
    lesson = d.get('progress', {}).get('current_lesson', 1)
    print(f'{name}|{due}|{lesson}')
except:
    print('Estudiante|0|1')
" 2>/dev/null || echo "Estudiante|0|1")

NAME=$(echo "$SRS_DUE" | cut -d'|' -f1)
DUE=$(echo "$SRS_DUE" | cut -d'|' -f2)
LESSON=$(echo "$SRS_DUE" | cut -d'|' -f3)

if [ "$DUE" -gt 0 ] 2>/dev/null; then
    BODY="🔄 $DUE tarjetas SRS pendientes\n📖 Continuar Lección $LESSON\n\nAbre Claude Code y escribe: /start_lesson"
else
    BODY="📖 Lección $LESSON lista para hoy\n\nAbre Claude Code y escribe: /start_lesson"
fi

# Enviar la notificación
DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus" \
notify-send \
    --urgency=normal \
    --expire-time=30000 \
    --app-name="Escuela de Japonés" \
    "🎌 ¡Es hora de estudiar, $NAME!" \
    "$BODY"

# Mostrar también en terminal si está disponible
echo "🎌 Recordatorio de estudio enviado — $(date)"
