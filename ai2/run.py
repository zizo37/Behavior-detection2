import os
import json
from cleaning import remove_duplicates, clean_text
from analysis import custom_keyword_score
from conclusions import save_analyzed_data
from report_generator import generate_report

def load_json_data(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return []

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Loaded {len(data)} comments from {file_path}")
            return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def process_comments(file_path):
    data = load_json_data(file_path)
    print(f"Processing {len(data)} comments")
    
    unique_data = remove_duplicates(data)
    print(f"After removing duplicates: {len(unique_data)} comments")
    analyzed_comments = []

    for i, comment in enumerate(unique_data, 1):
        # Note the space after the keys to match your JSON structure
        author = comment.get('author ', '').strip()
        text = comment.get('text ', '').strip()
        timestamp = comment.get('timestamp ', '').strip()

        if not text:  # Skip empty comments
            continue

        cleaned_text = clean_text(text)
        custom_analysis = custom_keyword_score(cleaned_text)

        analyzed_comment = {
            'author': author or 'Unknown',
            'original_text': text,
            'cleaned_text': cleaned_text,
            'timestamp': timestamp or 'Unknown',
            'analysis': custom_analysis
        }
        analyzed_comments.append(analyzed_comment)
        
        # Progress indicator
        if i % 100 == 0:
            print(f"Processed {i} comments...")

    return analyzed_comments

import os
import json
from cleaning import remove_duplicates, clean_text
from analysis import custom_keyword_score
from conclusions import save_analyzed_data
from report_generator import generate_report, save_report

def main():
    output_dir = 'output7'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = ['json/comments_data_of_post_4.json']
    
    all_analyzed_comments = []
    original_comments = []
    
    for file_path in files:
        print(f"\nProcessing file: {file_path}")
        # Load original comments
        data = load_json_data(file_path)
        original_comments.extend(data)
        
        # Process and analyze
        analyzed_comments = process_comments(file_path)
        all_analyzed_comments.extend(analyzed_comments)
        print(f"Processed {len(analyzed_comments)} comments from {file_path}")

    # Save analyzed comments
    output_file = os.path.join(output_dir, 'custom_analyzed_comments.json')
    save_analyzed_data(all_analyzed_comments, output_file)
    
    # Calculate duplicates
    duplicate_count = len(original_comments) - len(all_analyzed_comments)
    
    # Generate and save report
    report = generate_report(original_comments, all_analyzed_comments, duplicate_count)
    report_file = os.path.join(output_dir, 'analysis_report.json')
    save_report(report, report_file)
    
    print(f"\nTotal comments processed: {len(all_analyzed_comments)}")
    print(f"Duplicates removed: {duplicate_count}")
    print(f"Analysis report saved to: {report_file}")

if __name__ == "__main__":
    main()