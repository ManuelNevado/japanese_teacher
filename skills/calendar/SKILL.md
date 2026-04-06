---
name: study-reminder-scheduler
description: Agenda recordatorios de estudio de japonés. Tiene dos modos — Linux nativo (sin GCP, recomendado) y Google Calendar (requiere GCP). Úsala al final de cada lección para programar la próxima sesión.
---

# Skill: Study Reminder Scheduler 📅

## Descripción
Programa recordatorios de estudio usando el mejor método disponible. **Prioriza siempre el método Linux nativo** (`notify-send` + systemd/cron) ya que no requiere ninguna cuenta externa ni configuración de APIs.

---

## ⭐ Método Principal: Linux Nativo (sin GCP)

### Comprobar si está configurado
Lee `data/progress/student.json` → campo `calendar_settings.reminder_method`:
- `"linux_native"` → Recordatorios ya configurados ✅
- No existe o es `null` → Pedir al estudiante que configure con:

```bash
# Instalar (solo una vez):
sudo apt install libnotify-bin

# Configurar recordatorio diario:
bash scripts/setup_reminders.sh              # usa la hora de student.json
bash scripts/setup_reminders.sh --time 07:30 # cambiar la hora
```

El script detecta automáticamente si usar **systemd user timer** o **cron**.

### Para agendar la próxima sesión (método Linux)

No hay que hacer nada extra: el recordatorio diario ya corre automáticamente a la hora configurada y lee `student.json` para saber qué tarjetas SRS hay pendientes y en qué lección está el estudiante.

Al final de la lección, simplemente di:
```
📅 Tu recordatorio diario está activo a las [hora].
   Mañana recibirás una notificación con lo que falta revisar.
   Puedes comprobarlo con: bash scripts/daily_review.sh
```

---

## Método Alternativo: Google Calendar (requiere GCP)

Solo usar este método si el estudiante quiere los eventos en su Google Calendar para verlos en el móvil.

### Prerrequisitos
Antes de usar este método, el estudiante debe ejecutar:
```bash
python3 scripts/setup_calendar.py
```

Esto configura las credenciales OAuth y guarda el token en `~/.config/japanese_teacher/calendar_token.json`.

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
