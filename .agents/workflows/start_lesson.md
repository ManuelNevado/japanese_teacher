---
description: Iniciar una lección de japonés con el Sensei
---

# Workflow: Iniciar Lección (start_lesson)

## Objetivo
Iniciar una sesión de aprendizaje de japonés con el Sensei, que evaluará el estado del estudiante y comenzará con el contenido apropiado.

## Pasos

### 1. Leer el perfil del estudiante
Lee el archivo `data/progress/student.json` para conocer:
- Nivel actual (N5 por defecto)
- Última lección completada
- Tarjetas SRS con repaso pendiente (`srs_deck` donde `next_review` ≤ hoy)
- Historial de quizzes recientes

### 2. Invocar al Sensei
Lee el archivo `agents/teacher/AGENT.md` y actúa como el Sensei:
- Saluda al estudiante por su nombre
- Pregunta cómo le fue desde la última vez
- Informa cuántas tarjetas SRS tiene pendientes

### 3. Repaso SRS (si hay tarjetas pendientes)
Si hay tarjetas con `next_review` ≤ hoy:
- Lee `skills/vocabulary/SKILL.md`
- Realiza el repaso de las tarjetas vencidas (máximo 10)
- Actualiza los intervalos en `student.json`

### 4. Selección del contenido nuevo
Según el `current_lesson` en `student.json`, selecciona la siguiente lección del currículo:
- Consulta el currículo en `agents/teacher/AGENT.md`
- Lee los datos correspondientes de `data/jlpt/n5/`

### 5. Enseñar el contenido
Delega al subagente apropiado según el tipo de contenido:
- Gramática → lee `agents/grammar_tutor/AGENT.md` + `skills/grammar/SKILL.md`
- Vocabulario → lee `agents/vocab_trainer/AGENT.md` + `skills/vocabulary/SKILL.md`
- Kanji → lee `agents/kanji_master/AGENT.md` + `skills/kanji/SKILL.md`

### 6. Cierre y agendado
Al terminar la lección:
- Presenta el resumen de lo aprendido
- Actualiza `data/progress/student.json` con el progreso
- Ejecuta el workflow de agendado:
  ```bash
  python3 scripts/schedule_lesson.py \
      --title "Estudio Japonés — [próximo tema]" \
      --duration [duración_estimada] \
      --type [tipo_de_lección] \
      --content "[descripción]" \
      --objective "[objetivo]"
  ```
