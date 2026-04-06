#!/bin/bash
# daily_review.sh — Muestra el estado de hoy: qué viene, qué repasar, racha de estudio
# Ejecuta esto cada mañana o antes de abrir Claude Code

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STUDENT_FILE="$PROJECT_ROOT/data/progress/student.json"

if [ ! -f "$STUDENT_FILE" ]; then
    echo "❌ No hay perfil de estudiante. Ejecuta: bash scripts/init_student.sh"
    exit 1
fi

TODAY=$(date +%Y-%m-%d)
DAY_ES=$(LC_TIME=es_ES.UTF-8 date +"%A %d de %B" 2>/dev/null || date +"%A %d/%m/%Y")

echo ""
echo "🎌 ════════════════════════════════════════════"
echo "       ESCUELA DE JAPONÉS — $DAY_ES"
echo "   ════════════════════════════════════════════"
echo ""

python3 - <<EOF
import json
from datetime import date, datetime
from pathlib import Path

student_file = Path("$STUDENT_FILE")
vocab_file = Path("$PROJECT_ROOT/data/jlpt/n5/vocabulary.json")
today = date.today().isoformat()

with open(student_file, 'r', encoding='utf-8') as f:
    student = json.load(f)

name = student['student']['name']
progress = student.get('progress', {})
srs_deck = student.get('srs_deck', [])
quiz_history = student.get('quiz_history', [])
session_history = student.get('session_history', [])

# Tarjetas SRS vencidas
due_cards = [c for c in srs_deck if c.get('next_review', '9999') <= today]
overdue = [c for c in due_cards if c.get('next_review', today) < today]

# Última sesión
last_session = session_history[-1] if session_history else None
last_quiz = quiz_history[-1] if quiz_history else None

# Racha
streak = student['student'].get('current_streak_days', 0)
total_min = student['student'].get('total_study_minutes', 0)

print(f"  👤 Estudiante: {name}")
print(f"  📍 Nivel: JLPT N5 — Módulo {progress.get('current_module', 1)}, Lección {progress.get('current_lesson', 1)}")
print()

# Estado del SRS
if due_cards:
    print(f"  🔄 REPASO PENDIENTE: {len(due_cards)} tarjetas")
    if overdue:
        print(f"     ⚠️  {len(overdue)} tarjetas con retraso (de días anteriores)")
    print(f"     Palabras: {', '.join(c['word'] for c in due_cards[:8])}{'...' if len(due_cards) > 8 else ''}")
else:
    print(f"  ✅ Sin repasos pendientes hoy")
print()

# Estadísticas de progreso
vocab_count = len(progress.get('vocabulary_known', []))
kanji_count = len(progress.get('kanji_known', []))
grammar_count = len(progress.get('grammar_known', []))
print(f"  📊 Tu progreso:")
print(f"     🗃  Vocabulario:  {vocab_count} palabras  {'█' * min(vocab_count // 40, 20)}{'░' * (20 - min(vocab_count // 40, 20))} ({vocab_count}/800)")
print(f"     ✍️  Kanji:        {kanji_count}/80 {'█' * min(kanji_count, 20)}{'░' * (20 - min(kanji_count, 20))}")
print(f"     📖 Gramática:    {grammar_count} patrones")
print()

# Última sesión
if last_session:
    print(f"  📅 Última sesión: {last_session.get('date', '—')} ({last_session.get('duration_minutes', '?')} min)")
    print(f"     ↳ {last_session.get('summary', '—')}")
else:
    print(f"  📅 Sin sesiones registradas aún")

# Último quiz
if last_quiz:
    pct = last_quiz.get('percentage', 0)
    emoji = '🌟' if pct >= 90 else '✅' if pct >= 70 else '⚠️'
    print(f"  {emoji} Último quiz ({last_quiz.get('type', '?')}): {last_quiz.get('score', 0)}/{last_quiz.get('total', 0)} ({pct}%) — {last_quiz.get('date', '—')}")
print()

# Racha y tiempo
print(f"  🔥 Racha: {streak} días consecutivos  {'🔥' * min(streak, 10)}")
print(f"  ⏱  Total estudiado: {total_min // 60}h {total_min % 60}min")
print()

# Recomendación de hoy
print(f"  🎯 Para hoy el Sensei recomienda:")
if due_cards:
    print(f"     1. Repaso SRS: {len(due_cards)} tarjetas (~{max(10, len(due_cards) * 1)} min)")
lesson = progress.get('current_lesson', 1)
module = progress.get('current_module', 1)
print(f"     2. Lección M{module}L{lesson} (continuar donde lo dejaste)")
print()
print(f"  💡 En Claude Code escribe: /start_lesson")
print(f"     El Sensei retomará desde donde lo dejaste.")
EOF

echo ""
echo "   ════════════════════════════════════════════"
echo "         がんばってください！🎌"
echo "   ════════════════════════════════════════════"
echo ""
