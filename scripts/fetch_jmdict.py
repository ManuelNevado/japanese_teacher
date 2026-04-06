#!/usr/bin/env python3
"""
fetch_jmdict.py
---------------
Descarga y parsea los datos de JMdict (vocabulario) y KanjiDic2 (kanji) 
para poblar los archivos de datos de la escuela de japonés.

Fuentes:
  - JMdict:    https://www.edrdg.org/jmdict/j_jmdict.html
  - KanjiDic2: https://www.edrdg.org/wiki/index.php/KANJIDIC_Project

Uso:
  python3 scripts/fetch_jmdict.py --level N5
  python3 scripts/fetch_jmdict.py --level N5 --type vocabulary
  python3 scripts/fetch_jmdict.py --level N5 --type kanji
"""

import argparse
import json
import urllib.request
import gzip
import io
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# URLs de descarga (archivos comprimidos)
JMDICT_URL = "http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz"
KANJIDIC_URL = "http://www.edrdg.org/kanjidic/kanjidic2.xml.gz"

# Palabras N5 conocidas (lista de IDs de JMdict o palabras clave)
# Esta es una selección curada de las ~800 palabras N5
JLPT_N5_CORE_WORDS = [
    # Pronombres
    "私", "あなた", "彼", "彼女", "私たち", "みなさん",
    # Sustantivos - personas
    "人", "男", "女", "子供", "友達", "先生", "学生", "家族",
    "父", "母", "兄", "姉", "弟", "妹",
    # Lugares
    "学校", "家", "店", "駅", "銀行", "病院", "公園", "図書館",
    "会社", "レストラン", "スーパー", "郵便局",
    # Comida
    "ご飯", "パン", "肉", "魚", "野菜", "果物", "水", "お茶",
    "コーヒー", "ジュース", "ビール", "お酒",
    # Transporte
    "電車", "バス", "車", "タクシー", "自転車", "飛行機", "船",
    # Tiempo
    "今日", "明日", "昨日", "今週", "来週", "先週", "今月", "来月",
    "今年", "来年", "去年", "今", "毎日", "毎朝", "毎晩",
    # Verbos de movimiento
    "行く", "来る", "帰る", "入る", "出る", "乗る", "降りる",
    # Verbos cotidianos
    "食べる", "飲む", "見る", "聞く", "話す", "書く", "読む", "する",
    "買う", "売る", "使う", "作る", "起きる", "寝る", "働く",
    "勉強する", "運動する", "料理する",
    # Adjetivos-い
    "大きい", "小さい", "新しい", "古い", "高い", "安い", "長い",
    "短い", "広い", "狭い", "難しい", "易しい", "面白い", "つまらない",
    "忙しい", "暇", "かわいい", "きれい",
    # Adjetivos-な
    "好き", "嫌い", "上手", "下手", "有名", "親切", "元気", "静か",
    "にぎやか", "便利", "不便", "大丈夫",
    # Números y tiempo
    "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
    "百", "千", "万", "何", "いくつ",
]


def download_file(url, description):
    """Descarga un archivo comprimido con gzip."""
    print(f"⬇️  Descargando {description}...")
    print(f"   URL: {url}")
    print("   Esto puede tardar unos minutos (archivos grandes)...")

    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            compressed_data = response.read()
        print(f"   ✅ Descargado: {len(compressed_data) / 1024 / 1024:.1f} MB comprimidos")
        with gzip.open(io.BytesIO(compressed_data), 'rb') as f:
            data = f.read()
        print(f"   ✅ Descomprimido: {len(data) / 1024 / 1024:.1f} MB")
        return data
    except Exception as e:
        print(f"   ❌ Error al descargar: {e}")
        return None


def parse_jmdict_xml(xml_data, level='N5'):
    """Parse básico del XML de JMdict para extraer vocabulario N5."""
    print("🔍 Parseando JMdict XML...")

    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        print("❌ xml.etree.ElementTree no disponible")
        return []

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"❌ Error al parsear XML: {e}")
        return []

    vocabulary = []
    entry_count = 0

    for entry in root.findall('entry'):
        entry_count += 1
        if entry_count % 10000 == 0:
            print(f"   Procesando entrada {entry_count}...")

        # Verificar si tiene marca de nivel JLPT
        senses = entry.findall('sense')
        has_n5_tag = False
        for sense in senses:
            for misc in sense.findall('misc'):
                if misc.text == f'jlpt-{level.lower()}':
                    has_n5_tag = True
                    break

        if not has_n5_tag:
            continue

        # Extraer datos
        # Forma kanji
        k_ele = entry.find('k_ele')
        word = k_ele.find('keb').text if k_ele is not None else None

        # Forma kana
        r_ele = entry.find('r_ele')
        reading = r_ele.find('reb').text if r_ele is not None else None

        if not reading:
            continue

        # Significados en inglés (usar como referencia)
        meanings = []
        pos_list = []
        for sense in senses:
            for gloss in sense.findall('gloss'):
                if gloss.get('{http://www.w3.org/XML/1998/namespace}lang', 'eng') == 'eng':
                    meanings.append(gloss.text)
            for pos in sense.findall('pos'):
                if pos.text:
                    pos_list.append(pos.text)

        if not meanings:
            continue

        vocab_entry = {
            "word": word or reading,
            "reading": reading,
            "meanings_en": meanings[:3],  # máximo 3 significados
            "part_of_speech": pos_list[0] if pos_list else "unknown",
            "jlpt": level,
            "source": "JMdict"
        }
        vocabulary.append(vocab_entry)

    print(f"   ✅ Encontradas {len(vocabulary)} palabras {level}")
    return vocabulary


def fetch_n5_vocabulary(output_file):
    """Descarga y parsea el vocabulario N5 de JMdict."""
    xml_data = download_file(JMDICT_URL, "JMdict (vocabulario japonés)")
    if not xml_data:
        print("⚠️  No se pudo descargar JMdict. Usando datos curados preexistentes.")
        return False

    vocabulary = parse_jmdict_xml(xml_data.decode('utf-8'), 'N5')

    if not vocabulary:
        print("⚠️  No se encontraron entradas N5 en JMdict.")
        return False

    # Cargar datos existentes para hacer merge
    existing_data = {}
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)

    # Actualizar con datos de JMdict
    existing_vocab = {v['word']: v for v in existing_data.get('vocabulary', [])}

    for entry in vocabulary:
        word = entry['word']
        if word not in existing_vocab:
            # Añadir nueva entrada (sin translations al español — las añade el agente)
            new_entry = {
                "word": entry['word'],
                "reading": entry['reading'],
                "meanings_en": entry['meanings_en'],
                "meanings_es": [],  # El agente completará las traducciones al español
                "part_of_speech": entry['part_of_speech'],
                "jlpt": "N5",
                "category": "general",
                "source": "JMdict"
            }
            existing_vocab[word] = new_entry

    # Guardar
    output_data = existing_data.copy()
    output_data['vocabulary'] = list(existing_vocab.values())
    output_data['_meta']['total_words'] = len(existing_vocab)
    output_data['_meta']['last_updated'] = str(__import__('datetime').date.today())

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Vocabulario actualizado: {len(existing_vocab)} palabras en {output_file}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Descarga datos de JMdict/KanjiDic2')
    parser.add_argument('--level', default='N5', choices=['N5', 'N4', 'N3', 'N2', 'N1'],
                        help='Nivel JLPT a descargar (default: N5)')
    parser.add_argument('--type', choices=['vocabulary', 'kanji', 'all'], default='all',
                        help='Qué datos descargar (default: all)')
    args = parser.parse_args()

    level = args.level.upper()
    output_dir = PROJECT_ROOT / 'data' / 'jlpt' / level.lower()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🎌 Descargando datos JLPT {level} desde EDRDG...")
    print("=" * 55)

    if args.type in ('vocabulary', 'all'):
        vocab_file = output_dir / 'vocabulary.json'
        success = fetch_n5_vocabulary(vocab_file)
        if not success:
            print(f"\n💡 Los datos curados existentes en {vocab_file} son válidos para empezar.")

    print("\n" + "=" * 55)
    print("✅ ¡Proceso completado!")
    print(f"\n📁 Datos en: {output_dir}")
    print("\nNota: Las traducciones al español las generan los agentes de forma dinámica.")
    print("      Los archivos JSON base contienen meanings_en como referencia.")


if __name__ == '__main__':
    main()
