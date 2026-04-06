#!/usr/bin/env python3
"""
save_progress.py
----------------
Actualiza el progreso del estudiante en data/progress/student.json.
Es invocado por los agentes al final de cada sesión para guardar el estado.

Uso (los agentes lo llaman con estos argumentos):

  # Marcar una lección como completada
  python3 scripts/save_progress.py --lesson 3 --module 1

  # Añadir palabras aprendidas al mazo SRS
  python3 scripts/save_progress.py --learned-words "学校,先生,学生,友達"

  # Actualizar tarjetas SRS (repaso)
  python3 scripts/save_progress.py --srs-review "学校:4,先生:5,学生:3"

  # Registrar resultado de quiz
  python3 scripts/save_progress.py --quiz-result vocabulary --score 8 --total 10

  # Añadir kanji conocidos
  python3 scripts/save_progress.py --learned-kanji "日,月,山,川,木"

  # Registrar gramática trabajada
  python3 scripts/save_progress.py --learned-grammar "g001,g002,g005"

  # Todo a la vez al cerrar sesión
  python3 scripts/save_progress.py \\
      --lesson 3 --module 1 \\
      --learned-words "電車,駅,車" \\
      --session-minutes 35 \\
      --session-summary "Partículas に y で — muy bien"
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
STUDENT_FILE = PROJECT_ROOT / 'data' / 'progress' / 'student.json'
VOCAB_FILE = PROJECT_ROOT / 'data' / 'jlpt' / 'n5' / 'vocabulary.json'


def load_student():
    if not STUDENT_FILE.exists():
        print(f"❌ No existe perfil de estudiante. Ejecuta: bash scripts/init_student.sh")
        sys.exit(1)
    with open(STUDENT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_student(data):
    with open(STUDENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sm2_interval(interval, ease, repetitions, quality):
    """Calcula el nuevo intervalo SRS con el algoritmo SM-2."""
    if quality < 3:
        return 1, ease, 0
    new_ease = max(1.3, ease + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if repetitions == 0:
        new_interval = 1
    elif repetitions == 1:
        new_interval = 6
    else:
        new_interval = round(interval * new_ease)
    return new_interval, new_ease, repetitions + 1


def add_srs_words(student, words_str):
    """Añade palabras nuevas al mazo SRS."""
    words = [w.strip() for w in words_str.split(',') if w.strip()]
    deck = {card['word']: card for card in student.get('srs_deck', [])}
    today = date.today().isoformat()
    added = []

    # Cargar datos de vocabulario para enriquecer las tarjetas
    vocab_lookup = {}
    if VOCAB_FILE.exists():
        with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
        vocab_lookup = {v['word']: v for v in vocab_data.get('vocabulary', [])}

    for word in words:
        if word not in deck:
            vocab_info = vocab_lookup.get(word, {})
            deck[word] = {
                "word": word,
                "reading": vocab_info.get('reading', ''),
                "meaning": vocab_info.get('meanings', [''])[0] if vocab_info.get('meanings') else '',
                "level": "N5",
                "interval_days": 1,
                "ease_factor": 2.5,
                "repetitions": 0,
                "next_review": today,
                "last_reviewed": None,
                "added_date": today
            }
            added.append(word)
        # Si ya existe, no sobreescribir (mantener progreso SRS)

    student['srs_deck'] = list(deck.values())

    # También registrar en vocabulary_known
    known = set(student.get('progress', {}).get('vocabulary_known', []))
    known.update(words)
    student.setdefault('progress', {})['vocabulary_known'] = list(known)

    if added:
        print(f"✅ Añadidas al mazo SRS: {', '.join(added)} ({len(added)} palabras)")
    else:
        print(f"ℹ️  Todas las palabras ya estaban en el mazo")
    return student


def update_srs_reviews(student, reviews_str):
    """Actualiza los intervalos SRS tras un repaso. Formato: 'palabra:calidad,...'"""
    reviews = {}
    for item in reviews_str.split(','):
        item = item.strip()
        if ':' in item:
            word, quality = item.rsplit(':', 1)
            reviews[word.strip()] = int(quality.strip())

    deck = {card['word']: card for card in student.get('srs_deck', [])}
    today = date.today().isoformat()

    for word, quality in reviews.items():
        if word in deck:
            card = deck[word]
            new_interval, new_ease, new_reps = sm2_interval(
                card.get('interval_days', 1),
                card.get('ease_factor', 2.5),
                card.get('repetitions', 0),
                quality
            )
            next_review = (date.today() + timedelta(days=new_interval)).isoformat()
            deck[word].update({
                'interval_days': new_interval,
                'ease_factor': round(new_ease, 2),
                'repetitions': new_reps,
                'next_review': next_review,
                'last_reviewed': today
            })
            print(f"  📅 {word}: próximo repaso en {new_interval} días ({next_review})")

    student['srs_deck'] = list(deck.values())
    return student


def add_quiz_result(student, quiz_type, score, total, duration=None):
    """Registra el resultado de un quiz."""
    percentage = round((score / total) * 100) if total > 0 else 0
    entry = {
        "date": date.today().isoformat(),
        "type": quiz_type,
        "level": "N5",
        "score": score,
        "total": total,
        "percentage": percentage,
        "duration_minutes": duration
    }
    student.setdefault('quiz_history', []).append(entry)
    emoji = "🌟" if percentage >= 90 else "✅" if percentage >= 70 else "⚠️"
    print(f"  {emoji} Quiz {quiz_type}: {score}/{total} ({percentage}%)")
    return student


def mark_lesson_complete(student, lesson_num, module_num):
    """Marca una lección como completada y avanza el cursor."""
    lesson_id = f"M{module_num}L{lesson_num}"
    completed = student.setdefault('progress', {}).setdefault('completed_lessons', [])
    if lesson_id not in completed:
        completed.append(lesson_id)
    student['progress']['current_lesson'] = lesson_num + 1
    student['progress']['current_module'] = module_num
    print(f"  ✅ Lección {lesson_id} completada — siguiente: M{module_num}L{lesson_num + 1}")
    return student


def log_session(student, summary, minutes):
    """Registra el resumen de la sesión."""
    entry = {
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "duration_minutes": minutes,
        "lesson": student.get('progress', {}).get('current_lesson'),
        "module": student.get('progress', {}).get('current_module')
    }
    student.setdefault('session_history', []).append(entry)
    student['student']['total_study_minutes'] = (
        student['student'].get('total_study_minutes', 0) + (minutes or 0)
    )
    # Actualizar racha
    last_sessions = student.get('session_history', [])
    if len(last_sessions) >= 2:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        prev_date = last_sessions[-2].get('date', '')
        if prev_date == yesterday:
            student['student']['current_streak_days'] = student['student'].get('current_streak_days', 0) + 1
        elif prev_date != date.today().isoformat():
            student['student']['current_streak_days'] = 1
        longest = student['student'].get('longest_streak_days', 0)
        current = student['student'].get('current_streak_days', 1)
        if current > longest:
            student['student']['longest_streak_days'] = current
    print(f"  📝 Sesión registrada: {minutes} min — \"{summary}\"")
    return student


def main():
    parser = argparse.ArgumentParser(
        description='Guarda el progreso del estudiante',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--lesson', type=int, help='Número de lección completada')
    parser.add_argument('--module', type=int, default=1, help='Número del módulo (default: 1)')
    parser.add_argument('--learned-words', help='Palabras nuevas separadas por coma: "学校,先生"')
    parser.add_argument('--srs-review', help='Resultado del repaso: "学校:4,先生:5"')
    parser.add_argument('--quiz-result', help='Tipo de quiz: vocabulary|grammar|kanji|mixed')
    parser.add_argument('--score', type=int, help='Preguntas correctas')
    parser.add_argument('--total', type=int, help='Total de preguntas')
    parser.add_argument('--learned-kanji', help='Kanji aprendidos: "日,月,山"')
    parser.add_argument('--learned-grammar', help='IDs de gramática trabajada: "g001,g002"')
    parser.add_argument('--session-minutes', type=int, help='Duración de la sesión en minutos')
    parser.add_argument('--session-summary', help='Resumen breve de la sesión')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    student = load_student()
    print(f"\n💾 Guardando progreso de {student['student']['name']}...")

    if args.lesson:
        student = mark_lesson_complete(student, args.lesson, args.module)

    if args.learned_words:
        student = add_srs_words(student, args.learned_words)

    if args.srs_review:
        student = update_srs_reviews(student, args.srs_review)

    if args.quiz_result and args.score is not None and args.total is not None:
        student = add_quiz_result(student, args.quiz_result, args.score, args.total, args.session_minutes)

    if args.learned_kanji:
        kanji_list = [k.strip() for k in args.learned_kanji.split(',') if k.strip()]
        known = set(student.get('progress', {}).get('kanji_known', []))
        known.update(kanji_list)
        student.setdefault('progress', {})['kanji_known'] = list(known)
        print(f"  ✅ Kanji añadidos: {', '.join(kanji_list)}")

    if args.learned_grammar:
        grammar_list = [g.strip() for g in args.learned_grammar.split(',') if g.strip()]
        known = set(student.get('progress', {}).get('grammar_known', []))
        known.update(grammar_list)
        student.setdefault('progress', {})['grammar_known'] = list(known)
        print(f"  ✅ Gramática registrada: {', '.join(grammar_list)}")

    if args.session_summary or args.session_minutes:
        student = log_session(
            student,
            args.session_summary or "Sesión de estudio",
            args.session_minutes or 0
        )

    save_student(student)

    # Mostrar estado actual
    progress = student.get('progress', {})
    srs_deck = student.get('srs_deck', [])
    today = date.today().isoformat()
    due_today = sum(1 for c in srs_deck if c.get('next_review', '9999') <= today)

    print(f"\n{'='*45}")
    print(f"📊 Estado actual de {student['student']['name']}")
    print(f"{'='*45}")
    print(f"  📚 Módulo {progress.get('current_module', 1)}, Lección {progress.get('current_lesson', 1)}")
    print(f"  🗃  Vocabulario: {len(progress.get('vocabulary_known', []))} palabras")
    print(f"  ✍️  Kanji: {len(progress.get('kanji_known', []))}/80")
    print(f"  📖 Gramática: {len(progress.get('grammar_known', []))} patrones")
    print(f"  🔄 Tarjetas SRS pendientes hoy: {due_today}")
    total_min = student['student'].get('total_study_minutes', 0)
    print(f"  ⏱  Tiempo total: {total_min // 60}h {total_min % 60}min")
    print(f"  🔥 Racha actual: {student['student'].get('current_streak_days', 0)} días")
    print(f"{'='*45}\n")


if __name__ == '__main__':
    main()
