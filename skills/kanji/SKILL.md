---
name: japanese-kanji-master
description: Enseña kanji japoneses usando radicales, lecturas ON/kun, vocabulario asociado y mnemónicos en español. Úsala para presentar kanji nuevos, explicar su composición o practicar escritura.
---

# Skill: Kanji Master 漢字マスター

## Descripción
Enseña kanji de forma sistemática usando el método de radicales y mnemónicos visuales. Los datos provienen de `data/jlpt/n5/kanji.json` (formato KanjiDic2).

---

## Protocolo de Presentación de Kanji

### Formato de Ficha de Kanji

```
╔══════════════════════════════════════╗
║            漢字: [KANJI]              ║
╠══════════════════════════════════════╣
║ Significado: [en español]            ║
║ Nivel JLPT:  N[X]   Strokes: [N]    ║
╠══════════════════════════════════════╣
║ 🔊 Lecturas                          ║
║   ON'yomi (音読み):  [katakana]      ║
║   kun'yomi (訓読み): [hiragana]      ║
╠══════════════════════════════════════╣
║ 🧩 Radicales                         ║
║   [radical1] + [radical2] = kanji   ║
║   Significado: [historia visual]     ║
╠══════════════════════════════════════╣
║ 📚 Vocabulario con este kanji        ║
║   • [vocab1]: [significado]          ║
║   • [vocab2]: [significado]          ║
║   • [vocab3]: [significado]          ║
╠══════════════════════════════════════╣
║ 🧠 Mnemónico en español              ║
║   [historia corta y memorable]       ║
╚══════════════════════════════════════╝
```

---

## Los 80 Kanji de N5

Domina estos kanji antes de pasar a N4. Están agrupados temáticamente:

### Números y Cantidades
| Kanji | Significado | ON | kun |
|-------|-------------|-----|-----|
| 一 | uno | イチ | ひと- |
| 二 | dos | ニ | ふた- |
| 三 | tres | サン | み- |
| 四 | cuatro | シ | よ-, よっ- |
| 五 | cinco | ゴ | いつ- |
| 六 | seis | ロク | むっ- |
| 七 | siete | シチ | なな- |
| 八 | ocho | ハチ | やっ- |
| 九 | nueve | キュウ/ク | ここの- |
| 十 | diez | ジュウ | とお |
| 百 | cien | ヒャク | — |
| 千 | mil | セン | — |
| 万 | diez mil | マン/バン | — |

### Tiempo
| Kanji | Significado | ON | kun |
|-------|-------------|-----|-----|
| 日 | día/sol | ニチ/ジツ | ひ, か |
| 月 | luna/mes | ゲツ/ガツ | つき |
| 年 | año | ネン | とし |
| 時 | hora/tiempo | ジ | とき |
| 分 | minuto/parte | フン/ブン | わか-る |
| 週 | semana | シュウ | — |
| 今 | ahora | コン/キン | いま |

### Personas y Familia
| Kanji | Significado | ON | kun |
|-------|-------------|-----|-----|
| 人 | persona | ジン/ニン | ひと |
| 男 | hombre | ダン/ナン | おとこ |
| 女 | mujer | ジョ/ニョ | おんな |
| 子 | niño/hijo | シ/ス | こ |
| 父 | padre | フ | ちち |
| 母 | madre | ボ | はは |

### Lugares y Naturaleza
| Kanji | Significado | ON | kun |
|-------|-------------|-----|-----|
| 山 | montaña | サン | やま |
| 川 | río | セン | かわ |
| 木 | árbol | ボク/モク | き |
| 火 | fuego | カ | ひ |
| 水 | agua | スイ | みず |
| 金 | oro/dinero | キン/コン | かね |
| 土 | tierra | ド/ト | つち |
| 空 | cielo | クウ | そら |
| 雨 | lluvia | ウ | あめ |
| 国 | país | コク | くに |

---

## Método de Descomposición por Radicales

### Radicales Fundamentales (部首)
Estos radicales aparecen en los kanji N5:

| Radical | Nombre | Significado | Aparece en |
|---------|--------|-------------|-----------|
| 亻 | にんべん | persona | 休、仕 |
| 口 | くち | boca | 言、名 |
| 日 | にちへん | sol/día | 時、明 |
| 木 | きへん | árbol | 机、校 |
| 水/氵 | さんずい | agua | 海、泳 |
| 女 | おんなへん | mujer | 好、姉 |
| 山 | やまへん | montaña | 岩、岡 |
| 手/扌 | てへん | mano | 持、打 |

### Cómo Usar los Radicales para Memorizar

Para el kanji **明** (brillante/mañana):
- Componentes: 日 (sol) + 月 (luna)
- Historia: "Cuando el sol 日 y la luna 月 aparecen juntos, iluminan todo → **brillante/mañana**"

Para el kanji **休** (descanso):
- Componentes: 亻(persona) + 木 (árbol)
- Historia: "Una persona 亻 descansa apoyada en un árbol 木 → **descansar**"

---

## Orden de Trazos (Stroke Order)

Reglas generales (no mostrar imagen, describir):
1. De arriba hacia abajo
2. De izquierda a derecha
3. Horizontal antes que vertical (cuando se cruzan)
4. El marco exterior antes que el interior
5. Cierra el marco después del interior

---

## Notas Pedagógicas para el Agente

- **Nunca enseñar kanji sin vocabulario**: siempre mínimo 3 palabras que lo usen
- **Mnemónico siempre en español**: hacerlo visual y ligeramente absurdo para mejor retención
- **Progresión recomendada**: empezar por kanji con pocos trazos (一、二、三) y radicales simples
- **Reconocimiento antes que escritura**: en la era digital, reconocer es más práctico que escribir
- Si el estudiante pregunta cómo escribir a mano, describe los trazos en orden
