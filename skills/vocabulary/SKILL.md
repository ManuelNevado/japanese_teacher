---
name: japanese-vocabulary-trainer
description: Enseña vocabulario japonés con sistema de repetición espaciada (SRS). Úsala para presentar palabras nuevas, repasar vocabulario existente, o gestionar el mazo de tarjetas del estudiante.
---

# Skill: Japanese Vocabulary Trainer 語彙トレーナー

## Descripción
Presenta vocabulario japonés de forma rica y memorable, con contexto cultural, ejemplos en oraciones reales, y gestión del sistema SRS para maximizar la retención a largo plazo.

## Fuente de Datos
Los datos provienen de `data/jlpt/n5/vocabulary.json` (formato JMdict). Siempre lee este archivo antes de presentar vocabulario para asegurarte de usar datos precisos.

---

## Protocolo de Presentación de Vocabulario

### Formato de Tarjeta de Vocabulario

Para cada palabra nueva, presenta la información en este formato:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇯🇵 [Kanji/Kana]
   Lectura: [hiragana]  |  Romaji: [romaji]
   Tipo: [Sustantivo / Verbo / Adjetivo-i / Adjetivo-na / Adverbio]
   Nivel: JLPT N[X]

📖 Significado: [significado en español]
   (Alternativas: [otros significados si aplica])

💬 Ejemplo:
   [Oración en japonés]
   [Furigana]
   [Romaji]
   → [Traducción en español]

🧠 Tip de memoria: [mnemónico o truco para recordarla]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Grupos Semánticos N5
Organiza el vocabulario por categorías cuando presentes listas:

| Categoría | Ejemplos |
|-----------|---------|
| 🏠 Casa y familia | 家、母、父、兄、姉 |
| 🍱 Comida y bebida | 食べ物、水、ご飯、肉、魚 |
| 🏫 Escuela | 学校、先生、学生、本、ペン |
| 🚃 Transporte | 電車、バス、車、駅、道 |
| ⏰ Tiempo | 今、明日、昨日、毎日、時間 |
| 🌈 Colores | 赤、青、白、黒、黄色 |
| 🔢 Números | 一、二、三...百、千、万 |
| 📍 Ubicación | ここ、そこ、あそこ、どこ |
| 🙋 Personas | 人、男、女、子供、友達 |
| ❓ Interrogativos | 何、誰、どこ、いつ、どう |

---

## Sistema de Repetición Espaciada (SRS)

### Algoritmo SM-2 Simplificado
Cada tarjeta tiene:
- **intervalo**: días hasta el próximo repaso
- **facilidad**: factor de facilidad (2.5 inicial)
- **repeticiones**: número de repasos exitosos

### Calidad de Respuesta (0-5)
| Puntuación | Descripción |
|------------|-------------|
| 5 | Perfecto, sin dudas |
| 4 | Correcto con pequeña duda |
| 3 | Correcto con dificultad |
| 2 | Incorrecto pero se recordó al ver |
| 1 | Incorrecto |
| 0 | Total olvido |

### Cálculo del Intervalo
```
Si repetición = 1: intervalo = 1 día
Si repetición = 2: intervalo = 6 días
Si repetición > 2: intervalo = intervalo_anterior × facilidad

Nueva facilidad = facilidad + (0.1 - (5 - calidad) × (0.08 + (5 - calidad) × 0.02))
```

### Actualizar el Mazo
Cuando el estudiante repase, actualiza `data/progress/student.json` con los nuevos intervalos.

---

## Modos de Uso

### Modo: Aprender Palabras Nuevas
Presenta 5-10 palabras nuevas siguiendo el formato de tarjeta. Siempre incluye el tip de memoria.

### Modo: Repaso SRS
1. Lee `data/progress/student.json` para ver qué tarjetas vencen hoy
2. Muestra el japonés primero → pide al estudiante el significado
3. Revela la respuesta y pide que autoevalúe (0-5)
4. Actualiza el intervalo según SM-2

### Modo: Vocabulario por Tema
Cuando el estudiante pida vocabulario de una categoría específica, filtra `data/jlpt/n5/vocabulary.json` por campo semántico.

---

## Reglas Importantes

- **Máximo 10 palabras nuevas por sesión** — no sobrecargar la memoria de trabajo
- **Siempre contexto**: nunca presentar una palabra sin ejemplo en oración
- **Furigana obligatorio**: siempre que aparezca kanji
- **Kana priority**: si la palabra se escribe normalmente en kana (ej: ありがとう), no forzar kanji

---

## Notas Pedagógicas

- Los **falsos amigos** del inglés deben señalarse explícitamente (ej: マンション ≠ mansión)
- Las **palabras de origen extranjero** (katakana) son más fáciles — indícalo
- Los **kago** (palabras de origen chino) vs **yamato kotoba** (nativo japonés) tienen patrones distintos
- Anima al estudiante cuando progrese en su mazo SRS
