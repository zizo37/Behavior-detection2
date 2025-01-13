import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from login import login
from scrape import scrape_comments
from mongo import test_mongo_connection  

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
POST_URL = os.getenv("POST_URL")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

#Point d'entrée principal du programme

#Configure le driver Firefox
def setup_firefox_driver():
    try:
        print("[DEBUG] Setting up Firefox Developer Edition driver...")
        firefox_options = Options()
        
        service = Service(executable_path="C:/Users/DELL/OneDrive/Bureau/ai/Heec-prj-heec/scraping/geckodriver.exe")
        firefox_options.binary_location = "C:/Program Files/Firefox Developer Edition/firefox.exe"

        driver = webdriver.Firefox(service=service, options=firefox_options)
        print("[SUCCESS] Firefox Developer Edition driver initialized")
        return driver
    except Exception as e:
        print(f"[ERROR] Firefox Developer Edition driver setup failed: {str(e)}")
        raise

#Orchestre le processus complet (login → scraping → stockage)
#Gère les variables d'environnement
def main():
    driver = setup_firefox_driver()
    
    if login(driver, LINKEDIN_EMAIL, LINKEDIN_PASSWORD):
        print("[DEBUG] Starting comment extraction...")
        comments = scrape_comments(driver, POST_URL)
        print(f"[FINAL] Successfully scraped {len(comments)} comments")
        print("[DEBUG] Saving comments to MongoDB...")
        test_mongo_connection(MONGO_URI, 'json',DB_NAME)
    else:
        print("[ERROR] Login failed, stopping execution") 
    
    driver.quit()

if __name__ == "__main__":
    main()