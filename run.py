import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import json
from datetime import datetime
import subprocess
import sys
import platform

# Import scraping modules
from login import login
from scrape import scrape_comments
from mongo import test_mongo_connection

# Import analysis modules
from cleaning import remove_duplicates, clean_text
from analysis import custom_keyword_score
from conclusions import save_analyzed_data
from report_generator import generate_report, save_report




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



def launch_streamlit_dashboard():
    """Launch the Streamlit dashboard in a new process"""
    try:
        print("\n[DEBUG] Launching Streamlit dashboard...")
        
        # Determine the Python executable path
        python_executable = sys.executable
        
        # Construct the Streamlit command
        streamlit_command = [python_executable, "-m", "streamlit", "run", "dashboard.py"]
        
        # Use different start methods based on the operating system
        if platform.system() == "Windows":
            subprocess.Popen(streamlit_command, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(streamlit_command, start_new_session=True)
            
        print("[SUCCESS] Streamlit dashboard launched. Please wait a moment for it to open in your browser.")
        
    except Exception as e:
        print(f"[ERROR] Failed to launch Streamlit dashboard: {str(e)}")
        print("You can manually launch the dashboard by running: streamlit run dashboard.py")



def scrape_and_store_data(driver, post_url, mongo_uri, db_name):
    """Scrape LinkedIn data and store in MongoDB"""
    print("\n=== Phase 1: Data Collection ===")
    
    # Scrape comments
    print("[DEBUG] Starting comment extraction...")
    comments = scrape_comments(driver, post_url)
    print(f"[SUCCESS] Successfully scraped {len(comments)} comments")
    
    # Store in MongoDB
    print("[DEBUG] Saving comments to MongoDB...")
    test_mongo_connection(mongo_uri, 'json', db_name)
    
    return comments

def analyze_data(comments):
    """Analyze the collected comments and generate reports"""
    print("\n=== Phase 2: Data Analysis ===")
    
    output_dir = 'output7'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process and analyze comments
    print("[DEBUG] Processing and analyzing comments...")
    analyzed_comments = []
    
    for comment in comments:
        cleaned_text = clean_text(comment.get('text', ''))
        custom_analysis = custom_keyword_score(cleaned_text)
        
        analyzed_comment = {
            'author': comment.get('author', 'Unknown'),
            'original_text': comment.get('text', ''),
            'cleaned_text': cleaned_text,
            'timestamp': comment.get('timestamp', 'Unknown'),
            'analysis': custom_analysis
        }
        analyzed_comments.append(analyzed_comment)

    # Save analyzed comments
    output_file = os.path.join(output_dir, 'custom_analyzed_comments.json')
    save_analyzed_data(analyzed_comments, output_file)
    
    # Generate and save report
    duplicate_count = len(comments) - len(analyzed_comments)
    report = generate_report(comments, analyzed_comments, duplicate_count)
    report_file = os.path.join(output_dir, 'analysis_report.json')
    save_report(report, report_file)
    
    print(f"[SUCCESS] Analysis complete:")
    print(f"- Total comments analyzed: {len(analyzed_comments)}")
    print(f"- Duplicates removed: {duplicate_count}")
    print(f"- Analysis report saved to: {report_file}")
    
    return analyzed_comments, report

def main():
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment variables
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    post_url = os.getenv("POST_URL")
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    
    # Validate required environment variables
    required_vars = {
        "LINKEDIN_EMAIL": linkedin_email,
        "LINKEDIN_PASSWORD": linkedin_password,
        "POST_URL": post_url,
        "MONGO_URI": mongo_uri,
        "DB_NAME": db_name
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print(f"[ERROR] Missing required environment variables: {', '.join(missing_vars)}")
        return

    try:
        # Initialize driver and login
        driver = setup_firefox_driver()
        if not login(driver, linkedin_email, linkedin_password):
            print("[ERROR] Login failed, stopping execution")
            driver.quit()
            return

        # Phase 1: Scrape and store data
        comments = scrape_and_store_data(driver, post_url, mongo_uri, db_name)
        
        # Phase 2: Analyze data and generate reports
        analyzed_comments, report = analyze_data(comments)
        
        print("\n=== Process Complete ===")
        print(f"Successfully processed {len(comments)} comments")
        
        # Phase 3: Launch Streamlit dashboard
        launch_streamlit_dashboard()
        
    except Exception as e:
        print(f"[ERROR] An error occurred during execution: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()