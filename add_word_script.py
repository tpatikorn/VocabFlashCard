import os
import json
from glob import glob

from manager.vocabulary_manager import VocabularyManager
from manager.word_manager import WordManager

# Assuming WordManager is defined elsewhere and instantiated
word_manager = WordManager()
vocab_manager = VocabularyManager()

def process_vocab_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            groups = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {filepath}: {e}")
            return

        for group in groups:
            group_name = group.get("group_name")
            word_list = group.get("word_list", [])
            group_id = vocab_manager.get_or_create_group(group_name)["id"]

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
    vocab_files = glob("docs/vocab/*.json")
    for filepath in vocab_files:
        print(f"📘 Processing: {filepath}")
        process_vocab_file(filepath)

if __name__ == "__main__":
    load_all_vocab()