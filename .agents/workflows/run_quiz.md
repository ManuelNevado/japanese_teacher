---
description: Ejecutar un quiz de japonés (vocabulario, gramática, kanji o mixto)
---

# Workflow: Ejecutar Quiz (run_quiz)

## Objetivo
Generar y ejecutar un quiz de japonés evaluando vocabulario, gramática, kanji o una mezcla, registrando los resultados en el perfil del estudiante.

## Pasos

### 1. Determinar el tipo de quiz
Preguntar al estudiante o usar el contexto:
- **Vocabulario**: palabras, lecturas, significados
- **Gramática**: partículas, conjugaciones, patrones
- **Kanji**: lectura, significado, vocabulario
- **Mixto**: combinación de los anteriores
- **Simulacro JLPT N5**: formato oficial completo

### 2. Leer datos necesarios
- Lee `data/progress/student.json` para historial y palabras débiles
- Lee `data/jlpt/n5/vocabulary.json` para vocabulario
- Lee `data/jlpt/n5/grammar.json` para gramática
- Lee `data/jlpt/n5/kanji.json` para kanji

### 3. Invocar al Examiner
Lee `agents/examiner/AGENT.md` y `skills/quiz/SKILL.md`.
Genera 10-15 preguntas priorizando:
- Ítems nunca evaluados
- Ítems con puntuación baja (<70%)
- Ítems SRS vencidos

### 4. Ejecutar el quiz
- Presenta preguntas una a una
- Espera respuesta del estudiante
- En modo aprendizaje: da feedback inmediato
- En modo examen: acumula respuestas para el final

### 5. Mostrar resultados
Usa el formato de informe de `agents/examiner/AGENT.md`:
- Puntuación total (X/N, porcentaje)
- Lista de respuestas incorrectas con explicación
- Evaluación cualitativa
- Recomendaciones de estudio

### 6. Actualizar progreso
Actualiza `data/progress/student.json`:
- Añade entrada en `quiz_history`
- Actualiza intervalos SRS de los ítems evaluados

### 7. Sugerir agenda
Si el quiz reveló debilidades, sugerir una sesión de refuerzo:
```bash
python3 scripts/schedule_lesson.py \
    --title "Repaso — [área débil identificada]" \
    --duration 20 \
    --type review
```
