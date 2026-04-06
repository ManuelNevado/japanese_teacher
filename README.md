<div align="center">

# 🎌 Japanese Teacher

**Una escuela de japonés impulsada por IA, construida con Claude Code**

Aprende japonés desde cero hasta JLPT N5 con un sistema de agentes especializados, Repetición Espaciada (SRS) y recordatorios diarios en Google Calendar.

[![Nivel](https://img.shields.io/badge/Nivel%20actual-JLPT%20N5-4CAF50?style=for-the-badge)](data/jlpt/n5/)
[![Idioma](https://img.shields.io/badge/Enseñanza-Español-2196F3?style=for-the-badge)](skills/)
[![Claude Code](https://img.shields.io/badge/Powered%20by-Claude%20Code-FF6B35?style=for-the-badge)](https://claude.ai)
[![Datos](https://img.shields.io/badge/Datos-JMdict%2FKanjiDic2-9C27B0?style=for-the-badge)](https://www.edrdg.org/)

</div>

---

## ¿Qué es Japanese Teacher?

Un sistema de aprendizaje de japonés con **agentes de IA cooperativos** que trabajan juntos para darte una experiencia de enseñanza personalizada:

- 🎓 **Sensei** — Tu profesor personal que adapta el ritmo y la dificultad a tu nivel
- 📖 **Grammar Tutor** — Especialista en gramática con ejercicios adaptativos
- 🗃 **Vocab Trainer** — Gestiona tu mazo de vocabulario con SRS (algoritmo SM-2)
- ✍️ **Kanji Master** — Enseña los 80 kanji N5 con radicales y mnemónicos en español
- 📝 **Examiner** — Simula exámenes JLPT reales y genera informes de progreso
- 📅 **Google Calendar** — Agenda recordatorios de estudio a las 7:00 AM cada día laborable

---

## Requisitos

- **[Claude Code](https://claude.ai)** (con acceso a agentes y skills)
- **Python 3.10+**
- **Git**
- **Cuenta de Google** (para la integración opcional de Calendar)

---

## Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/ManuelNevado/japanese_teacher.git
cd japanese_teacher
```

### 2. Instala las dependencias de Python

```bash
pip install -r requirements.txt
```

> Las dependencias son solo para Google Calendar. Si no quieres esta integración, puedes saltarte este paso.

### 3. Inicializa tu perfil de estudiante

```bash
bash scripts/init_student.sh
```

Este script interactivo te pedirá:
- Tu nombre
- Hora preferida de estudio (por defecto: 07:00)
- Tu zona horaria (por defecto: Europe/Madrid)

Crea el archivo `data/progress/student.json` con tu perfil personalizado.

---

## Configuración de Google Calendar (Opcional)

Para que el Sensei pueda agendar tus sesiones de estudio automáticamente:

### 1. Crea un proyecto en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo (p. ej. `japanese-teacher`)
3. En el menú lateral: **APIs y Servicios** → **Biblioteca**
4. Busca y activa **"Google Calendar API"**

### 2. Crea credenciales OAuth 2.0

1. Ve a **APIs y Servicios** → **Credenciales**
2. Clic en **Crear Credenciales** → **ID de cliente OAuth**
3. Tipo de aplicación: **Aplicación de escritorio**
4. Nombre: `Japanese Teacher`
5. Descarga el JSON generado

### 3. Coloca el archivo de credenciales

```bash
# Copia el JSON descargado a la raíz del proyecto con este nombre exacto:
cp ~/Downloads/client_secret_*.json ./credentials.json
```

> ⚠️ `credentials.json` está en `.gitignore` — nunca se subirá a GitHub.

### 4. Autoriza el acceso

```bash
python3 scripts/setup_calendar.py
```

Se abrirá el navegador para que autorices el acceso a tu Google Calendar. Solo necesitas hacerlo una vez.

### 5. Prueba el agendado

```bash
python3 scripts/schedule_lesson.py \
    --title "Primera lección de japonés" \
    --duration 30 \
    --type grammar \
    --objective "Aprender hiragana básico"
```

---

## Uso con Claude Code

### Workflows disponibles

Una vez en Claude Code, usa estos comandos slash:

| Comando | Descripción |
|---------|-------------|
| `/start_lesson` | Inicia una lección con el Sensei |
| `/run_quiz` | Ejecuta un quiz de práctica |
| `/schedule_study` | Agenda la próxima sesión en Google Calendar |

### Arquitectura de Agentes

```
Usuario
  └── /start_lesson
        └── Sensei (agents/teacher/)
              ├── → Grammar Tutor (agents/grammar_tutor/)
              │     └── skills/grammar/  
              ├── → Vocab Trainer (agents/vocab_trainer/)
              │     └── skills/vocabulary/
              ├── → Kanji Master (agents/kanji_master/)
              │     └── skills/kanji/
              └── → Examiner (agents/examiner/)
                    └── skills/quiz/
```

Al final de cada lección, el Sensei:
1. Estima la duración de la próxima sesión según el contenido
2. Llama a `skills/calendar/` para crear el evento en Google Calendar
3. Crea el evento a las **7:00 AM del próximo día laborable**

---

## Estructura del Proyecto

```
japanese_teacher/
├── .claude/
│   └── CLAUDE.md                  # Instrucciones del proyecto para Claude Code
├── .agents/
│   └── workflows/
│       ├── start_lesson.md        # /start_lesson
│       ├── run_quiz.md            # /run_quiz
│       └── schedule_study.md     # /schedule_study
├── skills/
│   ├── grammar/SKILL.md           # Explicar gramática japonesa
│   ├── vocabulary/SKILL.md        # Enseñar vocabulario + SRS
│   ├── kanji/SKILL.md             # Enseñar kanji con radicales
│   ├── pronunciation/SKILL.md     # Guía de pronunciación
│   ├── conversation/SKILL.md      # Práctica de conversación
│   ├── quiz/SKILL.md              # Motor de quizzes JLPT
│   └── calendar/SKILL.md          # Google Calendar integration
├── agents/
│   ├── teacher/AGENT.md           # Sensei — coordinador principal
│   ├── grammar_tutor/AGENT.md     # Tutor de gramática
│   ├── vocab_trainer/AGENT.md     # Entrenador de vocabulario
│   ├── kanji_master/AGENT.md      # Maestro de kanji
│   └── examiner/AGENT.md          # Examinador JLPT
├── data/
│   ├── jlpt/n5/
│   │   ├── vocabulary.json        # 50+ palabras core N5 (formato JMdict)
│   │   ├── grammar.json           # 15 patrones gramaticales N5
│   │   └── kanji.json             # Kanji N5 con mnemónicos (formato KanjiDic2)
│   └── progress/
│       └── student_template.json  # Plantilla del perfil de estudiante
├── scripts/
│   ├── init_student.sh            # Inicializar perfil del estudiante
│   ├── setup_calendar.py          # Configurar Google Calendar OAuth
│   ├── schedule_lesson.py         # Crear evento en Google Calendar
│   └── fetch_jmdict.py            # Descargar datos completos de JMdict/KanjiDic2
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Currículo N5

El Sensei te guía a través de este currículo estructurado:

| Módulo | Semanas | Contenido |
|--------|---------|-----------|
| 1 — Alfabetos | 1-3 | Hiragana (46) + Katakana (46) + Combinaciones |
| 2 — Bases | 4-8 | Números, verbos básicos (ます), partículas は・が・を・に・で |
| 3 — N5 Completo | 9-16 | 800 palabras, gramática N5, adjetivos い/な |
| 4 — Examen | 17-20 | Repaso integral + Simulacro JLPT N5 |

---

## Datos Abiertos de JMdict/KanjiDic2

Los datos incluidos provienen de bases de datos abiertas. Para obtener el dataset completo (800+ palabras N5):

```bash
python3 scripts/fetch_jmdict.py --level N5
```

**Fuentes:**
- [JMdict](https://www.edrdg.org/jmdict/j_jmdict.html) — Diccionario japonés-inglés
- [KanjiDic2](https://www.edrdg.org/wiki/index.php/KANJIDIC_Project) — Diccionario de kanji

**Licencia de datos:** [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — © Electronic Dictionary Research and Development Group (EDRDG)

---

## Colores de los Eventos de Calendar

| Tipo de sesión | Color | Cuándo |
|----------------|-------|--------|
| 📖 Gramática nueva | 🔵 Azul oscuro | Lección de gramática |
| 🗃 Vocabulario | 🟢 Verde | Palabras nuevas o SRS |
| ✍️ Kanji | 🟣 Morado | Sesión de kanji |
| 📝 Quiz | 🟡 Amarillo | Quiz de práctica o simulacro |
| 💬 Conversación | 🔴 Rojo | Práctica conversacional |
| 🔄 Repaso | 🔵 Lavanda | Review general |

---

## Contribuir

1. Fork del repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Añade nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

Ideas de contribución:
- Añadir lecciones en `lessons/n5/` (en formato Markdown)
- Completar los 80 kanji N5 en `data/jlpt/n5/kanji.json`
- Traducir significados al español en `vocabulary.json`
- Añadir soporte para niveles N4-N1

---

## Licencia

Este proyecto está bajo la licencia **MIT**.

Los datos de vocabulario y kanji están bajo **CC BY-SA 4.0** (EDRDG).

---

<div align="center">

*がんばってください！(¡Mucho ánimo!)* 🎌

**Hecho con ❤️ y Claude Code**

</div>
