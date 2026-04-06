---
description: Programar un recordatorio de estudio de japonés en Google Calendar
---

# Workflow: Agendar Estudio (schedule_study)

## Objetivo
Crear un evento de estudio en Google Calendar para la próxima sesión de japonés, con la duración y el contenido apropiados decididos por el agente.

## Cuándo Usar
- Al final de cada lección automáticamente
- Cuando el estudiante pida "agenda mi próxima sesión"
- Para crear la rutina diaria de estudio matutino

## Pasos

### 1. Determinar el contenido de la próxima sesión
Basándose en `data/progress/student.json`:
- ¿Qué lección sigue en el currículo?
- ¿Hay tarjetas SRS que vencen mañana o pasado?
- ¿Hay áreas débiles identificadas en quizzes recientes?

### 2. Estimar la duración
Usa la tabla de `skills/calendar/SKILL.md`:

| Contenido planificado | Minutos |
|-----------------------|---------|
| Solo repaso SRS (<10 tarjetas) | 15 |
| Solo repaso SRS (10-20 tarjetas) | 20-25 |
| Gramática nueva (1 patrón) | 25-30 |
| Vocabulario nuevo (10 palabras) | 20-25 |
| Kanji nuevos (5-8 kanji) | 25-30 |
| Lección combinada | 40-50 |
| Quiz de práctica | 15-20 |

### 3. Determinar el tipo de sesión
Selecciona el tipo para el color del evento:
- `grammar` — si es principalmente gramática
- `vocabulary` — si es principalmente vocabulario
- `kanji` — si es principalmente kanji
- `review` — si es repaso SRS o quiz
- `conversation` — si es práctica conversacional

### 4. Ejecutar el script de agendado

// turbo
```bash
python3 scripts/schedule_lesson.py \
    --title "🎌 Estudio Japonés — [TEMA]" \
    --duration [MINUTOS] \
    --type [TIPO] \
    --content "[DESCRIPCIÓN DEL CONTENIDO]" \
    --objective "[OBJETIVO DE APRENDIZAJE]"
```

### 5. Confirmar al estudiante
Después de ejecutar el script, informa al estudiante:
```
📅 ¡Tu próxima sesión está en el calendario!
[Detalles del evento creado]
がんばって！🎌
```

## Notas
- Las sesiones se crean siempre en días laborables (Lunes-Viernes)
- La hora por defecto es 07:00 (configurable en `data/progress/student.json`)
- Si hay error de autenticación, pedirle al estudiante que ejecute `python3 scripts/setup_calendar.py`
