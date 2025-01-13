import re
import emoji

def clean_text(text):
    if not isinstance(text, str):
        return ""

    # Basic cleaning while preserving meaningful content
    text = emoji.demojize(text)
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = ' '.join(text.split())
    return text.strip()

def remove_duplicates(comments):
    seen_texts = set()
    unique_comments = []
    
    for comment in comments:
        # Handle the case where the key has a trailing space
        text = comment.get('text ', '') or comment.get('text', '')
        cleaned_text = clean_text(text)
        
        if cleaned_text and cleaned_text not in seen_texts:
            seen_texts.add(cleaned_text)
            unique_comments.append(comment)
    
    return unique_comments