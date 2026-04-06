---
name: google-calendar-study-scheduler
description: Programa recordatorios de estudio de japonés en Google Calendar. Crea eventos matutinos en días laborables con la duración adecuada según el contenido de la lección. Úsala al final de cada lección para agendar la siguiente sesión de estudio.
---

# Skill: Google Calendar Study Scheduler 📅

## Descripción
Integra Google Calendar para crear recordatorios de estudio automáticos. Los agentes estiman la duración de la sesión según el contenido planificado y crean el evento con todos los detalles relevantes para que el estudiante llegue preparado.

---

## Prerrequisitos

Antes de usar esta skill, verifica que el estudiante ha ejecutado:
```bash
python3 scripts/setup_calendar.py
```

Esto configura las credenciales de la API de Google Calendar y guarda el token en `~/.config/japanese_teacher/calendar_token.json`.

---

## Cómo Estimar la Duración de la Lección

El agente Sensei estima la duración basándose en el contenido:

| Tipo de Contenido | Duración Estimada |
|-------------------|------------------|
| Introducción a hiragana/katakana (10 chars) | 20 minutos |
| Vocabulario nuevo (5-10 palabras) | 15 minutos |
| Vocabulario nuevo (11-20 palabras) | 25 minutos |
| Patrón gramatical simple (1 patrón) | 20 minutos |
| Patrón gramatical complejo (1-2 patrones) | 30 minutos |
| Quiz de repaso | 10-15 minutos |
| Práctica de conversación | 20-30 minutos |
| Kanji nuevos (5-10 kanji) | 25 minutos |
| Lección combinada (vocab + gramática) | 40-50 minutos |
| Lección completa N5 | 50-60 minutos |

**Regla**: Redondea siempre a múltiplos de 5 minutos. Máximo recomendado: 60 minutos.

---

## Protocolo de Agendado

### Al Final de Cada Lección

1. **Estima la duración** de la próxima sesión basada en el contenido planificado
2. **Determina el horario**: Primera hora del día laboral (lunes-viernes)
   - Horario por defecto: **7:00 AM** (configurable en `data/progress/student.json`)
3. **Selecciona el próximo día laborable** disponible
4. **Crea el evento** usando el script de calendario

### Formato del Evento de Google Calendar

```
Título: 🎌 Estudio Japonés — [Tema de la lección]
Descripción:
  📚 Contenido: [descripción del contenido]
  ⏱ Duración estimada: [X] minutos
  🎯 Objetivo: [qué aprenderás hoy]
  📋 Preparación: [si hay algo que hacer antes]
  
  Skill a trabajar: [grammar/vocabulary/kanji/etc]
  Nivel: JLPT N5

Inicio: [fecha] a las [hora]
Fin: [fecha] a las [hora + duración]
Color: Verde (estudio) / Azul (repaso) / Amarillo (quiz)
Recordatorio: 10 minutos antes
```

### Llamada al Script

```bash
python3 scripts/schedule_lesson.py \
  --title "Estudio Japonés — [tema]" \
  --duration [minutos] \
  --date [YYYY-MM-DD] \
  --start-time "07:00" \
  --content "[descripción]" \
  --objective "[objetivo]" \
  --color [verde|azul|amarillo]
```

---

## Colores de Evento por Tipo de Sesión

| Tipo | Color | Código |
|------|-------|--------|
| Lección nueva | 🟢 Verde (Sage) | `"sage"` |
| Repaso SRS | 🔵 Azul (Peacock) | `"peacock"` |
| Quiz / Examen | 🟡 Amarillo (Banana) | `"banana"` |
| Práctica conversación | 🔴 Rojo (Tomato) | `"tomato"` |
| Kanji session | 🟣 Morado (Grape) | `"grape"` |

---

## Configuración del Estudiante

En `data/progress/student.json`, el estudiante puede configurar:

```json
{
  "calendar_settings": {
    "default_study_time": "07:00",
    "study_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
    "calendar_id": "primary",
    "timezone": "Europe/Madrid",
    "reminder_minutes": 10,
    "max_session_minutes": 60
  }
}
```

---

## Respuesta al Estudiante

Cuando crees el evento, comunica:

```
📅 Próxima sesión agendada en Google Calendar:

📌 [Título del evento]
📆 [Día, fecha] a las [hora]
⏱ Duración: [X] minutos
🎯 Trabajaremos: [contenido]

El evento ya está en tu calendario con un recordatorio de 10 minutos.
¡Hasta mañana, がんばって！🎌
```

---

## Manejo de Errores

| Error | Acción |
|-------|--------|
| Token no encontrado | Pedir al usuario ejecutar `setup_calendar.py` |
| Permiso denegado | Verificar scopes en la configuración OAuth |
| Conflicto de horario | Buscar el siguiente slot disponible |
| Sin conexión | Mostrar los datos del evento para crear manualmente |

---

## Notas para el Agente

- **No agendar los fines de semana** a menos que el estudiante lo solicite explícitamente
- La hora de **7:00 AM** es el default — respetar la configuración del estudiante
- Si el estudiante está saturado, sugiere una sesión más corta en lugar de saltar el día
- Al crear el evento, usa siempre el calendario `primary` a menos que se especifique otro
- Incluye siempre el emoji 🎌 en el título para identificar fácilmente los eventos de japonés
