# 🎌 Japanese Teacher — Instrucciones del Proyecto

## Descripción
Este repositorio es una **escuela de japonés inteligente** construida con agentes y skills de Claude Code.
El objetivo es guiar al estudiante desde cero (N5) hasta el nivel avanzado (N1) del JLPT, con lecciones adaptativas, quizzes personalizados y recordatorios de estudio via Google Calendar.

## Idioma
**Todas las explicaciones se dan en español.** El japonés se muestra en kanji/kana con furigana y romaji cuando es necesario.

## Estructura del Proyecto

```
.claude/           → Instrucciones del proyecto (aquí estás)
skills/            → Skills especializadas de Claude Code
agents/            → Definiciones de agentes y subagentes
data/jlpt/         → Datos de vocabulario, gramática y kanji por nivel JLPT
data/srs/          → Sistema de Repetición Espaciada (SRS)
data/progress/     → Progreso del estudiante
scripts/           → Scripts de utilidad (calendario, SRS, JMdict)
lessons/           → Lecciones estructuradas en markdown
.agents/workflows/ → Workflows de Claude Code
```

## Agentes Disponibles

| Agente | Rol |
|--------|-----|
| `agents/teacher/` | **Sensei** — Coordinador principal, evalúa y delega |
| `agents/grammar_tutor/` | Especialista en gramática japonesa |
| `agents/vocab_trainer/` | Entrenador de vocabulario con SRS |
| `agents/kanji_master/` | Maestro de kanji y escritura |
| `agents/examiner/` | Examinador JLPT, genera y evalúa tests |

## Skills Disponibles

| Skill | Función |
|-------|---------|
| `skills/grammar/` | Explicar patrones gramaticales |
| `skills/vocabulary/` | Enseñar vocabulario con SRS |
| `skills/kanji/` | Enseñar kanji con radicales y mnemónicos |
| `skills/pronunciation/` | Guía de pronunciación y pitch accent |
| `skills/conversation/` | Práctica de conversación contextualizada |
| `skills/quiz/` | Generar y evaluar quizzes tipo JLPT |
| `skills/calendar/` | Programar recordatorios en Google Calendar |

## Datos

- **Fuente**: JMdict (vocabulario) + KanjiDic2 (kanji) — bases de datos abiertas de la Electronic Dictionary Research and Development Group (EDRDG)
- **Nivel actual**: N5 (expansión a N4-N1 en fases futuras)
- **Formato**: JSON estructurado, compatible con Anki export

## Cómo Usar

1. **Iniciar como estudiante nuevo**:
   ```bash
   ./scripts/init_student.sh
   ```

2. **Hablar con el Sensei**:
   Invoca el agente teacher: `@agents/teacher`

3. **Programar estudio en Google Calendar**:
   ```bash
   python3 scripts/setup_calendar.py
   python3 scripts/schedule_lesson.py
   ```

4. **Review diario**:
   ```bash
   ./scripts/daily_review.sh
   ```

## Convenciones

- Los **archivos de datos** van en `data/` — nunca hardcodear vocab en el código
- Las **explicaciones** siempre incluyen: forma japonesa, furigana, romaji, significado en español, ejemplo en contexto
- El **nivel** actual del estudiante se almacena en `data/progress/student.json`
- La **duración de la lección** la decide el agente Sensei según la complejidad del contenido (15-60 min)

## Reglas de los Agentes

1. Siempre identificar el nivel actual del estudiante antes de responder
2. Nunca mezclar vocabulario de niveles superiores sin avisar
3. En cada lección, incluir al menos: explicación, 3 ejemplos, 1 ejercicio práctico
4. Al final de cada lección, proponer agendar la siguiente sesión en Google Calendar
5. El Sensei decide la duración estimada antes de crear el evento de calendario
