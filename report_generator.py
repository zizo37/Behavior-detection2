# # report_generator.py

# import json
# from collections import Counter
# from datetime import datetime

# def analyze_comment_types(analyzed_comments):
#     """Analyze different types of comments including positive, aggressive, and sarcastic"""
#     positive_count = 0
#     aggressive_count = 0
#     sarcastic_count = 0
#     pure_neutral_count = 0
    
#     for comment in analyzed_comments:
#         analysis = comment['analysis']
#         supportive_score = analysis.get('supportive_score', 0)
#         critical_score = analysis.get('critical_score', 0)
        
#         # Identify positive comments (high supportive score, low critical score)
#         if supportive_score > 2 and critical_score < 1:
#             positive_count += 1
            
#         # Identify aggressive comments (high critical score, low supportive score)
#         if critical_score > 2 and supportive_score < 1:
#             aggressive_count += 1
            
#         # Identify potential sarcastic comments (both supportive and critical present)
#         if supportive_score > 0 and critical_score > 0:
#             sarcastic_count += 1
            
#         # Identify pure neutral comments (no sentiment at all)
#         if supportive_score == 0 and critical_score == 0:
#             pure_neutral_count += 1
    
#     total = len(analyzed_comments)
#     return {
#         'comment_types': {
#             'positive_comments': {
#                 'count': positive_count,
#                 'percentage': round((positive_count / total) * 100, 2) if total else 0
#             },
#             'aggressive_comments': {
#                 'count': aggressive_count,
#                 'percentage': round((aggressive_count / total) * 100, 2) if total else 0
#             },
#             'sarcastic_comments': {
#                 'count': sarcastic_count,
#                 'percentage': round((sarcastic_count / total) * 100, 2) if total else 0
#             },
#             'pure_neutral_comments': {
#                 'count': pure_neutral_count,
#                 'percentage': round((pure_neutral_count / total) * 100, 2) if total else 0
#             }
#         }
#     }

# # def analyze_sentiment_intensity(analyzed_comments):
# #     """Analyze the intensity of sentiments in comments"""
# #     intensity_levels = {
# #         'very_positive': 0,  # supportive_score > 5
# #         'moderately_positive': 0,  # supportive_score between 2 and 5
# #         'slightly_positive': 0,  # supportive_score between 0 and 2
# #         'very_negative': 0,  # critical_score > 5
# #         'moderately_negative': 0,  # critical_score between 2 and 5
# #         'slightly_negative': 0,  # critical_score between 0 and 2
# #         'mixed': 0  # both scores present
# #     }
    
# #     for comment in analyzed_comments:
# #         supportive = comment['analysis'].get('supportive_score', 0)
# #         critical = comment['analysis'].get('critical_score', 0)
        
# #         if supportive > 0 and critical > 0:
# #             intensity_levels['mixed'] += 1
# #         elif supportive > 5:
# #             intensity_levels['very_positive'] += 1
# #         elif supportive > 2:
# #             intensity_levels['moderately_positive'] += 1
# #         elif supportive > 0:
# #             intensity_levels['slightly_positive'] += 1
# #         elif critical > 5:
# #             intensity_levels['very_negative'] += 1
# #         elif critical > 2:
# #             intensity_levels['moderately_negative'] += 1
# #         elif critical > 0:
# #             intensity_levels['slightly_negative'] += 1
    
# #     total = len(analyzed_comments)
# #     return {
# #         'sentiment_intensity': {
# #             level: {
# #                 'count': count,
# #                 'percentage': round((count / total) * 100, 2) if total else 0
# #             }
# #             for level, count in intensity_levels.items()
# #         }
# #     }

# report_generator.py

import json
from collections import Counter
from datetime import datetime

def generate_keyword_stats(analyzed_comments):
    """Generate statistics about keyword usage"""
    positive_keywords = Counter()
    negative_keywords = Counter()
    all_words = Counter()
    
    for comment in analyzed_comments:
        # Use the found keywords from our sentiment analysis
        found_keywords = comment['analysis'].get('found_keywords', {'positive': [], 'negative': []})
        
        # Update counters with actual positive/negative keywords
        positive_keywords.update(found_keywords['positive'])
        negative_keywords.update(found_keywords['negative'])
        
        # For most used words, still use all words from cleaned text
        words = comment['cleaned_text'].lower().split()
        all_words.update(words)
    
    # Remove common words from most_used_words
    common_words = {'the', 'and', 'to', 'is', 'you', 'a', 'for', 'of', 'i', 
                   'your', 'are', 'in', 'that', 'this', 'these', 'but', 'on',
                   'with', 'my', 'it', 'at', 'be', 'as', 'or', 'by', 'an',
                   'they', 'we', 'what', 'how', 'when', 'where', 'who', 'which',
                   'there', 'here', 'from', 'his', 'her', 'their', 'our', 'its'}
    
    meaningful_words = {word: count for word, count in all_words.items() 
                       if word not in common_words}
    
    return {
        'most_common_positive': positive_keywords.most_common(10),
        'most_common_negative': negative_keywords.most_common(10),
        'most_used_words': Counter(meaningful_words).most_common(20)
    }

def analyze_sentiment_distribution(analyzed_comments):
    """Analyze the distribution of sentiment scores in the analyzed comments."""
    positive = 0
    negative = 0
    neutral = 0
    
    for comment in analyzed_comments:
        score = comment['analysis'].get('sentiment_score', 0)
        if score > 0:
            positive += 1
        elif score < 0:
            negative += 1
        else:
            neutral += 1

    total = len(analyzed_comments)
    return {
        'positive': round((positive / total) * 100, 2) if total else 0,
        'negative': round((negative / total) * 100, 2) if total else 0,
        'neutral': round((neutral / total) * 100, 2) if total else 0
    }

def analyze_comment_lengths(analyzed_comments):
    """Analyze the distribution of comment lengths"""
    lengths = [len(comment['cleaned_text'].split()) for comment in analyzed_comments]
    return {
        'average_length': round(sum(lengths) / len(lengths) if lengths else 0, 2),
        'shortest': min(lengths) if lengths else 0,
        'longest': max(lengths) if lengths else 0,
        'distribution': {
            'short (1-10 words)': sum(1 for l in lengths if l <= 10),
            'medium (11-30 words)': sum(1 for l in lengths if 10 < l <= 30),
            'long (31+ words)': sum(1 for l in lengths if l > 30)
        }
    }

def analyze_user_engagement(analyzed_comments):
    """Analyze user engagement patterns"""
    authors = Counter()
    for comment in analyzed_comments:
        authors[comment['author']] += 1
    
    return {
        'total_unique_authors': len(authors),
        'most_active_authors': authors.most_common(5),
        'engagement_distribution': {
            'single_comment': sum(1 for count in authors.values() if count == 1),
            'multiple_comments': sum(1 for count in authors.values() if count > 1)
        }
    }

def analyze_temporal_patterns(analyzed_comments):
    """Analyze temporal patterns in comments"""
    hourly_distribution = Counter()
    daily_distribution = Counter()
    
    for comment in analyzed_comments:
        try:
            timestamp = datetime.fromisoformat(comment['timestamp'].replace('Z', '+00:00'))
            hourly_distribution[timestamp.hour] += 1
            daily_distribution[timestamp.strftime('%Y-%m-%d')] += 1
        except (ValueError, AttributeError):
            continue
    
    return {
        'hourly_distribution': dict(sorted(hourly_distribution.items())),
        'daily_distribution': dict(sorted(daily_distribution.items())),
        'peak_hour': max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else None
    }

def analyze_comment_types(analyzed_comments):
    """Analyze different types of comments including positive, aggressive, and sarcastic"""
    positive_count = 0
    aggressive_count = 0
    sarcastic_count = 0
    pure_neutral_count = 0
    
    # Lists to store comments with their scores
    positive_comments = []
    aggressive_comments = []
    
    for comment in analyzed_comments:
        analysis = comment['analysis']
        supportive_score = analysis.get('supportive_score', 0)
        critical_score = analysis.get('critical_score', 0)
        
        # Store comment data for ranking
        comment_data = {
            'text': comment['cleaned_text'],
            'supportive_score': supportive_score,
            'critical_score': critical_score,
            'author': comment['author']
        }
        
        # Identify positive comments (high supportive score, low critical score)
        if supportive_score > 2 and critical_score < 1:
            positive_count += 1
            positive_comments.append(comment_data)
            
        # Identify aggressive comments (high critical score, low supportive score)
        if critical_score > 2 and supportive_score < 1:
            aggressive_count += 1
            aggressive_comments.append(comment_data)
            
        # Identify potential sarcastic comments (both supportive and critical present)
        if supportive_score > 0 and critical_score > 0:
            sarcastic_count += 1
            
        # Identify pure neutral comments (no sentiment at all)
        if supportive_score == 0 and critical_score == 0:
            pure_neutral_count += 1
    
    # Sort comments by their respective scores
    top_positive = sorted(positive_comments, key=lambda x: x['supportive_score'], reverse=True)[:5]
    top_aggressive = sorted(aggressive_comments, key=lambda x: x['critical_score'], reverse=True)[:5]
    
    total = len(analyzed_comments)
    return {
        'comment_types': {
            'positive_comments': {
                'count': positive_count,
                'percentage': round((positive_count / total) * 100, 2) if total else 0,
                'top_5': [{
                    'text': comment['text'],
                    'author': comment['author'],
                    'supportive_score': comment['supportive_score']
                } for comment in top_positive]
            },
            'aggressive_comments': {
                'count': aggressive_count,
                'percentage': round((aggressive_count / total) * 100, 2) if total else 0,
                'top_5': [{
                    'text': comment['text'],
                    'author': comment['author'],
                    'critical_score': comment['critical_score']
                } for comment in top_aggressive]
            },
            'sarcastic_comments': {
                'count': sarcastic_count,
                'percentage': round((sarcastic_count / total) * 100, 2) if total else 0
            },
            'pure_neutral_comments': {
                'count': pure_neutral_count,
                'percentage': round((pure_neutral_count / total) * 100, 2) if total else 0
            }
        }
    }
def analyze_sentiment_intensity(analyzed_comments):
    """Analyze the intensity of sentiments in comments"""
    intensity_levels = {
        'very_positive': 0,  # supportive_score > 5
        'moderately_positive': 0,  # supportive_score between 2 and 5
        'slightly_positive': 0,  # supportive_score between 0 and 2
        'very_negative': 0,  # critical_score > 5
        'moderately_negative': 0,  # critical_score between 2 and 5
        'slightly_negative': 0,  # critical_score between 0 and 2
        'mixed': 0  # both scores present
    }
    
    for comment in analyzed_comments:
        supportive = comment['analysis'].get('supportive_score', 0)
        critical = comment['analysis'].get('critical_score', 0)
        
        if supportive > 0 and critical > 0:
            intensity_levels['mixed'] += 1
        elif supportive > 5:
            intensity_levels['very_positive'] += 1
        elif supportive > 2:
            intensity_levels['moderately_positive'] += 1
        elif supportive > 0:
            intensity_levels['slightly_positive'] += 1
        elif critical > 5:
            intensity_levels['very_negative'] += 1
        elif critical > 2:
            intensity_levels['moderately_negative'] += 1
        elif critical > 0:
            intensity_levels['slightly_negative'] += 1
    
    total = len(analyzed_comments)
    return {
        'sentiment_intensity': {
            level: {
                'count': count,
                'percentage': round((count / total) * 100, 2) if total else 0
            }
            for level, count in intensity_levels.items()
        }
    }

# def generate_report(original_comments, analyzed_comments, duplicate_count):
#     """Generate a comprehensive analysis report with enhanced metrics"""
#     report = {
#         'general_statistics': {
#             'total_comments_collected': len(original_comments),
#             'total_comments_analyzed': len(analyzed_comments),
#             'duplicates_removed': duplicate_count,
#             'completion_rate': round((len(analyzed_comments) / len(original_comments) * 100), 2) if original_comments else 0
#         },
#         'sentiment_analysis': analyze_sentiment_distribution(analyzed_comments),
#         'comment_type_analysis': analyze_comment_types(analyzed_comments),
#         'sentiment_intensity': analyze_sentiment_intensity(analyzed_comments),
#         'keyword_statistics': generate_keyword_stats(analyzed_comments),
#         'comment_length_analysis': analyze_comment_lengths(analyzed_comments),
#         'user_engagement': analyze_user_engagement(analyzed_comments),
#         'temporal_analysis': analyze_temporal_patterns(analyzed_comments),
#         'data_quality': {
#             'empty_comments': sum(1 for c in analyzed_comments if not c['cleaned_text']),
#             'average_sentiment_score': round(
#                 sum(c['analysis']['sentiment_score'] for c in analyzed_comments) / len(analyzed_comments)
#                 if analyzed_comments else 0,
#                 2
#             )
#         },
#         'report_metadata': {
#             'generated_at': datetime.now().isoformat(),
#             'version': '1.1'
#         }
#     }
    
#     return report

def save_report(report, output_file):
    """Save the report to a JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        print(f"Report successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving report: {e}")


def generate_report(original_comments, analyzed_comments, duplicate_count):
    """Generate a comprehensive analysis report with enhanced metrics"""
    report = {
        'general_statistics': {
            'total_comments_collected': len(original_comments),
            'total_comments_analyzed': len(analyzed_comments),
            'duplicates_removed': duplicate_count,
            'completion_rate': round((len(analyzed_comments) / len(original_comments) * 100), 2) if original_comments else 0
        },
        'sentiment_analysis': analyze_sentiment_distribution(analyzed_comments),
        'comment_type_analysis': analyze_comment_types(analyzed_comments),
        'sentiment_intensity': analyze_sentiment_intensity(analyzed_comments),
        'keyword_statistics': generate_keyword_stats(analyzed_comments),
        'comment_length_analysis': analyze_comment_lengths(analyzed_comments),
        'user_engagement': analyze_user_engagement(analyzed_comments),
        'temporal_analysis': analyze_temporal_patterns(analyzed_comments),
        'data_quality': {
            'empty_comments': sum(1 for c in analyzed_comments if not c['cleaned_text']),
            'average_sentiment_score': round(
                sum(c['analysis']['sentiment_score'] for c in analyzed_comments) / len(analyzed_comments)
                if analyzed_comments else 0,
                2
            )
        },
        'report_metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '1.1'
        }
    }
    
    return report