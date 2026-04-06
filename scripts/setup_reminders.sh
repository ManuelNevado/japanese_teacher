#!/bin/bash
# setup_reminders.sh
# -------------------
# Configura recordatorios de estudio de japonés sin necesidad de GCP ni Google Calendar API.
# Usa notificaciones de escritorio nativas de Linux (notify-send) + systemd user timer o cron.
#
# Métodos disponibles (se elige el mejor automáticamente):
#   1. systemd --user timer  (más fiable, recomendado)
#   2. cron                  (fallback universal)
#
# Requisitos:
#   sudo apt install libnotify-bin   # para notify-send
#
# Uso:
#   bash scripts/setup_reminders.sh              # instala el recordatorio de hoy
#   bash scripts/setup_reminders.sh --time 08:00 # cambia la hora
#   bash scripts/setup_reminders.sh --remove      # elimina el recordatorio

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STUDENT_FILE="$PROJECT_ROOT/data/progress/student.json"
NOTIFY_SCRIPT="$PROJECT_ROOT/scripts/notify_study.sh"

# --- Leer configuración del estudiante ---
STUDY_TIME="07:00"
STUDENT_NAME="Estudiante"
if [ -f "$STUDENT_FILE" ]; then
    STUDY_TIME=$(python3 -c "
import json
with open('$STUDENT_FILE') as f:
    d = json.load(f)
print(d.get('calendar_settings', {}).get('default_study_time', '07:00'))
" 2>/dev/null || echo "07:00")
    STUDENT_NAME=$(python3 -c "
import json
with open('$STUDENT_FILE') as f:
    d = json.load(f)
print(d['student']['name'])
" 2>/dev/null || echo "Estudiante")
fi

# --- Parsear argumentos ---
REMOVE=false
for arg in "$@"; do
    case "$arg" in
        --time=*) STUDY_TIME="${arg#--time=}" ;;
        --time)   shift; STUDY_TIME="$1" ;;
        --remove) REMOVE=true ;;
    esac
done

HOUR="${STUDY_TIME%%:*}"
MINUTE="${STUDY_TIME##*:}"

echo "🎌 Configurador de Recordatorios — Escuela de Japonés"
echo "======================================================"

# --- Verificar notify-send ---
if ! command -v notify-send &>/dev/null; then
    echo ""
    echo "⚠️  notify-send no está instalado. Instálalo primero:"
    echo "   sudo apt install libnotify-bin"
    echo ""
    echo "Luego vuelve a ejecutar este script."
    exit 1
fi

# --- Crear el script de notificación ---
mkdir -p "$(dirname "$NOTIFY_SCRIPT")"
cat > "$NOTIFY_SCRIPT" << 'NOTIFY_EOF'
#!/bin/bash
# Auto-generado por setup_reminders.sh — no editar manualmente
PROJECT_ROOT="PROJECT_ROOT_PLACEHOLDER"
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
NOTIFY_EOF

# Reemplazar el placeholder con la ruta real
sed -i "s|PROJECT_ROOT_PLACEHOLDER|$PROJECT_ROOT|g" "$NOTIFY_SCRIPT"
chmod +x "$NOTIFY_SCRIPT"

# --- Eliminar recordatorio existente ---
remove_systemd_timer() {
    systemctl --user stop japanese-study.timer 2>/dev/null || true
    systemctl --user disable japanese-study.timer 2>/dev/null || true
    rm -f ~/.config/systemd/user/japanese-study.{timer,service}
    systemctl --user daemon-reload 2>/dev/null || true
    echo "✅ Timer systemd eliminado"
}

remove_cron() {
    crontab -l 2>/dev/null | grep -v "japanese_teacher\|study-japanese" | crontab - 2>/dev/null || true
    echo "✅ Entrada cron eliminada"
}

if [ "$REMOVE" = true ]; then
    echo "🗑  Eliminando recordatorios..."
    remove_systemd_timer
    remove_cron
    echo "Recordatorios de estudio de japonés eliminados."
    exit 0
fi

# --- Método 1: systemd --user timer (preferido) ---
setup_systemd_timer() {
    mkdir -p ~/.config/systemd/user

    # Service
    cat > ~/.config/systemd/user/japanese-study.service << EOF
[Unit]
Description=Recordatorio de estudio de japonés
After=graphical-session.target

[Service]
Type=oneshot
ExecStart=$NOTIFY_SCRIPT
Environment=DISPLAY=:0
EOF

    # Timer (Lunes a Viernes a la hora configurada)
    cat > ~/.config/systemd/user/japanese-study.timer << EOF
[Unit]
Description=Recordatorio diario de estudio de japonés
Requires=japanese-study.service

[Timer]
OnCalendar=Mon-Fri *-*-* ${HOUR}:${MINUTE}:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

    systemctl --user daemon-reload
    systemctl --user enable --now japanese-study.timer
    echo "✅ Timer systemd activado"
    echo ""
    systemctl --user list-timers japanese-study.timer --no-pager 2>/dev/null || true
}

# --- Método 2: cron (fallback) ---
setup_cron() {
    # Eliminar entrada anterior si existe
    crontab -l 2>/dev/null | grep -v "japanese_teacher" | crontab - 2>/dev/null || true

    CRON_LINE="${MINUTE} ${HOUR} * * 1-5 DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/\$(id -u)/bus bash $NOTIFY_SCRIPT"
    (crontab -l 2>/dev/null; echo "# Japanese Teacher study reminder"; echo "$CRON_LINE") | crontab -
    echo "✅ Cron job añadido"
    echo "   $(crontab -l | grep japanese_teacher)"
}

# Intentar systemd primero, caer a cron si falla
echo ""
echo "⏰ Configurando recordatorio a las $STUDY_TIME (Lunes-Viernes)..."
echo ""

if systemctl --user status &>/dev/null 2>&1; then
    setup_systemd_timer
    METHOD="systemd timer"
else
    echo "ℹ️  systemd no disponible, usando cron..."
    setup_cron
    METHOD="cron"
fi

# --- Actualizar hora en student.json ---
if [ -f "$STUDENT_FILE" ]; then
    python3 -c "
import json
with open('$STUDENT_FILE', 'r') as f:
    d = json.load(f)
d.setdefault('calendar_settings', {})['default_study_time'] = '$STUDY_TIME'
d['calendar_settings']['reminder_method'] = 'linux_native'
with open('$STUDENT_FILE', 'w') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
" 2>/dev/null && echo "✅ Hora actualizada en student.json"
fi

echo ""
echo "======================================================"
echo "✅ ¡Recordatorio configurado con $METHOD!"
echo ""
echo "📋 Resumen:"
echo "   Hora:    $STUDY_TIME (Lunes a Viernes)"
echo "   Método:  $METHOD"
echo "   Script:  $NOTIFY_SCRIPT"
echo ""
echo "🔔 Recibirás una notificación de escritorio cada día"
echo "   indicándote cuántas tarjetas SRS tienes pendientes"
echo "   y en qué lección estás."
echo ""
echo "💡 Comandos útiles:"
echo "   Ver próxima alarma:  systemctl --user list-timers japanese-study.timer"
echo "   Probar ahora:        bash $NOTIFY_SCRIPT"
echo "   Cambiar hora:        bash scripts/setup_reminders.sh --time 08:30"
echo "   Eliminar:            bash scripts/setup_reminders.sh --remove"
echo "======================================================"
