from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os

#Extrait les commentaires d'un post LinkedIn
def scrape_comments(driver, post_url):
    try:
        print(f"[DEBUG] Navigating to post: {post_url}")
        driver.get(post_url)
        
        print("[DEBUG] Waiting for comments section to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "comments-comment-entity"))
        )
        
        scroll_to_load_comments(driver)
        
        print("[DEBUG] Finding comment elements...")
        comments = driver.find_elements(By.CLASS_NAME, "comments-comment-entity")
        print(f"[INFO] Found {len(comments)} comments")
        
        comments_data = []
        for index, comment in enumerate(comments, 1):
            try:
                print(f"[DEBUG] Processing comment {index}/{len(comments)}")
                
                author_element = comment.find_element(By.CSS_SELECTOR, "span.comments-comment-meta__description-title")
                author = author_element.text if author_element else "Unknown Author"
                
                profile_link_element = comment.find_element(By.CSS_SELECTOR, "a.comments-comment-meta__image-link")
                profile_link = profile_link_element.get_attribute("href") if profile_link_element else "No Profile Link"
                
                text_element = comment.find_element(By.CSS_SELECTOR, "span.comments-comment-item__main-content")
                text = text_element.text if text_element else "No text"
                
                timestamp_element = comment.find_element(By.CSS_SELECTOR, "time.comments-comment-meta__data")
                timestamp = timestamp_element.text if timestamp_element else "No timestamp"
                
                comment_data = {
                    "author": author,
                    "profile_link": profile_link,
                    "text": text,
                    "timestamp": timestamp,
                    "post_url": post_url
                }
                comments_data.append(comment_data)
                print(f"[SUCCESS] Comment {index} processed")
                
            except Exception as e:
                print(f"[ERROR] Failed to process comment {index}: {str(e)}")
                continue
        
        #Sauvegarde les données en JSON
        if comments_data:
            print("[DEBUG] Saving comments to JSON file...")

            if not os.path.exists('json'):
                os.makedirs('json')
            
            next_file_number = 1
            while os.path.exists(f'json/comments_data_of_post_{next_file_number}.json'):
                next_file_number += 1
            
            with open(f'json/comments_data_of_post_{next_file_number}.json', 'w') as json_file:
                json.dump(comments_data, json_file, indent=4)
            print(f"[SUCCESS] Saved {len(comments_data)} comments to JSON file {next_file_number}")
        
        return comments_data
        
    except Exception as e:
        print(f"[ERROR] Failed to scrape post: {str(e)}")
        return [] 

def scroll_to_load_comments(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height