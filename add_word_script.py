import csv
import json
from glob import glob

from manager import vocabulary_manager
from manager import word_manager

def process_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            groups = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {filepath}: {e}")
            return

        for group in groups:
            group_name = group.get("group_name")
            word_list = group.get("word_list", [])
            group_id = vocabulary_manager.get_or_create_group(group_name)["id"]

            for entry in word_list:
                word_manager.add_word(
                    group_id=group_id,
                    word=entry["word"],
                    part_of_speech=entry["part_of_speech"],
                    meaning_en=entry["meaning_en"],
                    meaning_th=entry["meaning_th"],
                    examples=entry.get("examples"),
                    synonyms=entry.get("synonyms"),
                    antonyms=entry.get("antonyms"),
                    word_forms=entry.get("word_forms"),
                    difficulty=entry.get("difficulty"),
                    frequency=entry.get("frequency")
                )

def process_csv_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Group words by group_name
        groups = {}
        for row in reader:
            group_name = row['group_name']
            if group_name not in groups:
                groups[group_name] = []
            
            # Split examples by <br> if they exist
            examples = row.get('example', '').split('<br>') if row.get('example') else []
            
            # Split synonyms, antonyms, variations by comma if they exist
            synonyms = [s.strip() for s in row.get('synonyms', '').split(',') if s.strip()] if row.get('synonyms') else []
            antonyms = [a.strip() for a in row.get('antonyms', '').split(',') if a.strip()] if row.get('antonyms') else []
            word_forms = [w.strip() for w in row.get('variations', '').split(',') if w.strip()] if row.get('variations') else []
            
            groups[group_name].append({
                'word': row['word'],
                'part_of_speech': row['part_of_speech'],
                'meaning_en': row['meaning_en'],
                'meaning_th': row['meaning_th'],
                'examples': examples,
                'synonyms': synonyms,
                'antonyms': antonyms,
                'word_forms': word_forms,
                'difficulty': row.get('difficulty'),
                'frequency': row.get('frequency')
            })
        
        # Process each group
        for group_name, word_list in groups.items():
            group_id = vocabulary_manager.get_or_create_group(group_name)["id"]
            
            for entry in word_list:
                word_manager.add_word(
                    group_id=group_id,
                    word=entry["word"],
                    part_of_speech=entry["part_of_speech"],
                    meaning_en=entry["meaning_en"],
                    meaning_th=entry["meaning_th"],
                    examples=entry.get("examples"),
                    synonyms=entry.get("synonyms"),
                    antonyms=entry.get("antonyms"),
                    word_forms=entry.get("word_forms"),
                    difficulty=entry.get("difficulty"),
                    frequency=entry.get("frequency")
                )

def load_all_vocab():
    # Process JSON files
    json_files = glob("docs/vocab/*.json")
    for filepath in json_files:
        print(f"📘 Processing JSON: {filepath}")
        process_json_file(filepath)
    
    # Process CSV files
    csv_files = glob("docs/vocab/*.csv")
    for filepath in csv_files:
        print(f"📄 Processing CSV: {filepath}")
        process_csv_file(filepath)


if __name__ == "__main__":
    load_all_vocab()