import os
import json
from analysis import custom_keyword_score
from cleaning import clean_text

def save_analyzed_data(analyzed_comments, output_file):
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(analyzed_comments, file, indent=4, ensure_ascii=False)
        print(f"Analyzed data saved to: {output_file}")
    except Exception as e:
        print(f"Error saving analyzed data: {e}")