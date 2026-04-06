#!/bin/bash
# init_student.sh — Inicializa el perfil del estudiante

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROGRESS_DIR="$PROJECT_ROOT/data/progress"
TEMPLATE="$PROGRESS_DIR/student_template.json"
STUDENT_FILE="$PROGRESS_DIR/student.json"

echo "🎌 ¡Bienvenido a la Escuela de Japonés!"
echo "========================================"
echo ""

# Si ya existe, preguntar si quiere sobreescribir
if [ -f "$STUDENT_FILE" ]; then
    read -p "⚠️  Ya existe un perfil de estudiante. ¿Sobreescribir? (s/N): " confirm
    if [[ ! "$confirm" =~ ^[sS]$ ]]; then
        echo "Operación cancelada. Tu perfil existente se mantiene."
        exit 0
    fi
fi

# Obtener nombre del estudiante
read -p "👤 ¿Cuál es tu nombre? " student_name
if [ -z "$student_name" ]; then
    student_name="Estudiante"
fi

# Obtener hora preferida de estudio
echo ""
echo "⏰ ¿A qué hora prefieres estudiar? (formato HH:MM)"
read -p "   Hora de estudio [07:00]: " study_time
if [ -z "$study_time" ]; then
    study_time="07:00"
fi

# Obtener zona horaria
echo ""
echo "🌍 Zona horaria (ejemplos: Europe/Madrid, America/Mexico_City, America/Buenos_Aires)"
read -p "   Zona horaria [Europe/Madrid]: " timezone
if [ -z "$timezone" ]; then
    timezone="Europe/Madrid"
fi

# Crear el perfil usando Python para manejar JSON correctamente
python3 - <<EOF
import json
import shutil
from pathlib import Path
from datetime import date

template = Path("$TEMPLATE")
student_file = Path("$STUDENT_FILE")

# Copiar template
shutil.copy(template, student_file)

# Cargar y personalizar
with open(student_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

data['student']['name'] = "$student_name"
data['student']['start_date'] = date.today().isoformat()
data['calendar_settings']['default_study_time'] = "$study_time"
data['calendar_settings']['timezone'] = "$timezone"

with open(student_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Perfil creado para: {data['student']['name']}")
EOF

echo ""
echo "========================================"
echo "✅ ¡Perfil inicializado con éxito!"
echo ""
echo "📋 Resumen de tu configuración:"
echo "   Nombre:       $student_name"
echo "   Nivel:        JLPT N5 (nivel inicial)"
echo "   Hora estudio: $study_time"
echo "   Zona horaria: $timezone"
echo "   Días estudio: Lunes a Viernes"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Configura Google Calendar:"
echo "      python3 scripts/setup_calendar.py"
echo ""
echo "   2. ¡Empieza a aprender con el Sensei!"
echo "      (Abre Claude Code e invoca: @agents/teacher)"
echo ""
echo "がんばってください！(¡Mucho ánimo!) 🎌"
