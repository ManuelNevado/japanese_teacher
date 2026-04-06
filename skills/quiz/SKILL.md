---
name: japanese-quiz-engine
description: Genera y evalúa quizzes de japonés tipo JLPT. Crea preguntas de vocabulario, gramática y comprensión. Registra los resultados en el perfil del estudiante. Úsala para evaluar el progreso o practicar antes del examen.
---

# Skill: Quiz Engine クイズエンジン

## Descripción
Motor de quizzes que genera exámenes tipo JLPT adaptados al nivel del estudiante. Evalúa respuestas, calcula puntuación y registra resultados para seguimiento del progreso.

---

## Tipos de Quiz

### 1. Quiz de Vocabulario (語彙)

#### Pregunta: Significado de la palabra
```
Elige el significado correcto de: 学校

A) biblioteca
B) escuela ✓
C) hospital
D) tienda
```

#### Pregunta: Palabra correcta
```
¿Cuál es la palabra japonesa para "agua"?

A) 火 (hi)
B) 風 (kaze)
C) 水 (mizu) ✓
D) 土 (tsuchi)
```

#### Pregunta: Lectura correcta
```
¿Cómo se lee 日本語?

A) にほんご ✓
B) にっぽんご
C) じゅんご
D) にほんこ
```

### 2. Quiz de Gramática (文法)

#### Pregunta de partícula
```
田中さん ___ 学生です。

A) が
B) は ✓
C) を
D) で
```

#### Completar la oración
```
毎日学校___ 行きます。(voy a la escuela todos los días)

A) を
B) が
C) に ✓
D) は
```

#### Forma correcta del verbo
```
昨日、映画___ 見ました。

A) を ✓
B) が
C) に
D) で
```

### 3. Quiz de Kanji (漢字)

#### Reconocimiento
```
¿Qué significa este kanji? 山

A) río
B) montaña ✓
C) árbol
D) fuego
```

#### Escritura (selección múltiple)
```
¿Cómo se escribe "persona" en kanji?

A) 木
B) 山
C) 人 ✓
D) 口
```

### 4. Quiz de Comprensión (読解) — Mini textos N5

```
Lee el siguiente texto y responde:

田中さんは学生です。毎日学校に行きます。
学校は家から近いです。

¿Qué hace Tanaka-san todos los días?
A) Trabaja
B) Va a la escuela ✓
C) Va de compras
D) Estudia en casa
```

---

## Protocolo de Quiz

### Inicio del Quiz

```
📝 QUIZ [tipo] — Nivel N5
   Preguntas: [N]
   Tiempo estimado: [X] minutos
   
¿Listo para empezar? (sí/no)
```

### Durante el Quiz
- Presenta una pregunta a la vez
- Espera respuesta antes de continuar
- **No reveles la respuesta correcta** hasta el final (modo examen) o inmediatamente (modo aprendizaje)
- En **modo aprendizaje**: tras cada respuesta, explica por qué es correcta o incorrecta

### Al Finalizar

```
━━━━━━━━━━━━━━━━━━━━━━━
📊 RESULTADOS DEL QUIZ
━━━━━━━━━━━━━━━━━━━━━━━
Puntuación: [X]/[Total] ([%]%)
Tiempo: [X] minutos

✅ Correctas: [N]
❌ Incorrectas: [N]

📈 Evaluación:
  90-100%: ¡Excelente! Listo para avanzar
  70-89%:  Buen trabajo, repasa los errores
  50-69%:  Necesitas más práctica
  <50%:    Vuelve a repasar el material

🔍 Respuestas incorrectas:
  [Lista de preguntas fallidas con explicación]
━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Modos de Quiz

| Modo | Descripción | Cuándo Usar |
|------|-------------|-------------|
| **Aprendizaje** | Feedback inmediato tras cada pregunta | Practicar material nuevo |
| **Examen** | Sin feedback hasta el final | Simular condiciones de examen |
| **Repaso SRS** | Solo palabras/kanji con repaso pendiente | Review diario |
| **Temático** | Quiz de una categoría específica | Reforzar un tema concreto |
| **Aleatorio** | Mezcla de todo N5 | Repaso general |

---

## Registrar Resultados

Después de cada quiz, actualiza `data/progress/student.json`:

```json
{
  "quiz_history": [
    {
      "date": "2024-01-15",
      "type": "vocabulary",
      "level": "N5",
      "score": 8,
      "total": 10,
      "percentage": 80,
      "duration_minutes": 5,
      "incorrect_items": ["学校", "電車"]
    }
  ]
}
```

---

## Banco de Preguntas N5

Genera preguntas dinámicamente usando los datos de:
- `data/jlpt/n5/vocabulary.json` → para quizzes de vocabulario
- `data/jlpt/n5/grammar.json` → para quizzes de gramática  
- `data/jlpt/n5/kanji.json` → para quizzes de kanji

### Algoritmo de Selección
1. Lee el historial del estudiante en `data/progress/student.json`
2. Prioriza ítems con:
   - Nunca evaluados
   - Evaluados con resultado bajo (<70%)
   - SRS con fecha de repaso vencida
3. Incluye 20% de ítems conocidos para reforzar confianza

---

## Notas para el Agente

- **10-15 preguntas** es el tamaño ideal para mantener concentración
- **Nunca repetir** la misma pregunta en el mismo quiz
- Los distractores (respuestas incorrectas) deben ser plausibles, no obvios
- En quizzes de kanji, incluir siempre al menos 1 pregunta de lectura y 1 de significado
- Celebra cuando el estudiante mejora su puntuación respecto a la última vez
