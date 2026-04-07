---
title: Plan de Migración a Arquitectura Web (Japanese Teacher)
tags:
  - architecture
  - AI
  - web
  - planning
date: 2026-04-07
---

# Plan Técnico: Migración a Aplicación Web Interactiva

## 📌 Resumen Ejecutivo
El sistema actual funciona de maravilla como un proyecto CLI impulsado por el binario de Anthropic (`claude`). Sin embargo, su evolución natural es convertirse en una aplicación cliente-servidor (Web App). Esto permitirá tener componentes nativos para interactuar, una UI reactiva que muestre en tiempo real el progreso de los JSONs, y renderizado perfecto del furigana en japonés (usando `<ruby>`).

---

## 🏗 Arquitectura Propuesta

La transición supone dividir la aplicación en **Frontend (La "Clase")** y **Backend (El "Cerebro")**.

### 1. El Backend (API de Python / FastAPI)
Python es el lenguaje ideal porque ya contiene el parser JSON del proyecto (`save_progress.py`), scripts integrados en bash para lógica secundaria y excelente SDK oficial de Anthropic.

- **Framework**: `FastAPI` (extremadamente veloz, genera documentación interactiva con Swagger, facilita la creación de llamadas de streaming asíncronas).
- **Core de Inteligencia**: Sustituiremos `Claude Code` por la librería `anthropic-sdk-python`. 
- **Tool Calling Directo**: FastAPI registrará funciones nativas (como `save_progress(dict)`) que el LLM puede invocar bajo demanda de manera limpia.
- **Rutas clave**:
  - `GET /student/progress` → Sirve la UI para cargar el dashboard.
  - `POST /chat/sensei` → Recibe el mensaje del usuario, adjunta el contexto del estudiante, y llama a la Anthropic API.
  - `POST /sync/calendar` → Reutiliza tu `setup_calendar.py` en un endpoint HTTP.

### 2. El Frontend (Next.js / React)
La experiencia del estudiante necesita ser rica y sin fricciones. 

- **Framework**: `Next.js` o `Vite + React`.
- **Estructura UI**:
  - **Barra Lateral Izquierda**: Stats del estudiante, el progreso de SRS del día, racha actual, % kanjis completados.
  - **Ventana Central (Chat)**: Un clon de la interfaz tipo "Mensajes de iMessage" para chatear con "Sensei".
  - **Panel Frontal (Ejercicios)**: Cuando Sensei lance un quiz o kanji, el frontend pinta botones interactivos reales.
- **Renderizado Adaptativo (Furigana)**: Se puede usar un componente wrapper Markdown que reconozca los formatos `[漢字]{かんじ}` y devuelva un nodo HTML `<ruby>`.

---

## 🗺️ Fases de Implementación Recomendada

### Fase 1: Consolidación del Backend (El wrapper API)
No rompemos nada del proyecto original todavía, lo englobamos.
- [ ] Iniciar un proyecto `FastAPI`.
- [ ] Transcribir los `AGENT.md` (Sensei, Grammar, Vocab...) a constantes de texto de Python que serán los `system_prompts`.
- [ ] Migrar las funciones de lectura/escritura (`save_progress.py`) para que devuelvan/reciban variables en vez de leer de SysArgs.
- [ ] Crear el endpoint asíncrono para comunicarse usando la API de Claude (streaming de la respuesta text/event-stream HTTP).

### Fase 2: Desarrollo Frontend (Dashboard & Chat)
- [ ] Desplegar una plantilla en blanco de Vite/React.
- [ ] Crear el "State Manager" para leer `student.json` vía HTTP e hidratar la barra lateral (los kanji conocidos, los mazos activos, rachas).
- [ ] Implementar la ventana de chat y el parser de Markdown personalizado.
- [ ] Conectar la UI de chat con el endpoint FastAPI para enviar mensajes y renderizar las respuestas de Sensei.

### Fase 3: Modernización Sensorial (El "Plus")
- [ ] Refactor del "Quiz": Sensei actualmente hace preguntas con texto plano. Lo ideal será que Sensei emita un llamado a la herramienta (tool_call) como `launch_quiz(data)`. La API enviará esos metadatos al front y el front generará formularios clickables interactivos.
- [ ] Despliegue de Text-to-Speech (TTS): Conectar a ElevenLabs o Google TTS para que cuando Sensei hable japonés en los mensajes, la web pueda generar audio narrado de la frase en tiempo real.

---

> [!note] Beneficios Críticos
> **Reducción de latencia y errores**: En la CLI, todo depende de que Claude *lea* tus archivos. En FastAPI, nosotros forzamos qué contexto viaja al modelo, lo cual controla radicalmente el *Token Count*.
> **Estética UX/UI**: El japonés es muy visual, las tarjetas de SRS (Repaso Espaciado) serían preciosas en CSS.
> **Multidispositivo**: Si pones tu servidor expuesto localmente o online, podrías acceder a la escuela y chatear con Sensei desde el móvil.

## 🔗 Referencias
- [[API de Anthropic Tool Use|Documentación oficial de Tools]]
- Contexto actual: `student.json`
