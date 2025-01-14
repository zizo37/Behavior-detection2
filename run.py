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
import tkinter as tk
from tkinter import ttk, messagebox

# Import existing modules
from login import login
from scrape import scrape_comments
from mongo import test_mongo_connection
from cleaning import remove_duplicates, clean_text
from analysis import custom_keyword_score
from conclusions import save_analyzed_data
from report_generator import generate_report, save_report

class LinkedInURLInput:
    def __init__(self):
        self.url = None
        self.window = tk.Tk()
        self.window.title("LinkedIn Post Analyzer")
        self.window.geometry("600x200")
        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # URL input
        ttk.Label(main_frame, text="Enter LinkedIn Post URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.url_entry = ttk.Entry(main_frame, width=70)
        self.url_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Status label
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))

        # Analyze button
        ttk.Button(main_frame, text="Start Analysis", command=self.start_analysis).grid(row=3, column=0, sticky=tk.W)

    def start_analysis(self):
        self.url = self.url_entry.get().strip()
        if not self.url:
            messagebox.showerror("Error", "Please enter a LinkedIn post URL")
            return
        if not self.url.startswith("https://www.linkedin.com/"):
            messagebox.showerror("Error", "Please enter a valid LinkedIn URL")
            return
        
        self.status_label.config(text="URL accepted. Starting analysis...")
        self.window.after(1000, self.close_window)

    def close_window(self):
        self.window.destroy()

    def get_url(self):
        self.window.mainloop()
        return self.url

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
    try:
        print("\n[DEBUG] Launching Streamlit dashboard...")
        python_executable = sys.executable
        streamlit_command = [python_executable, "-m", "streamlit", "run", "dashboard.py"]
        
        if platform.system() == "Windows":
            subprocess.Popen(streamlit_command, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(streamlit_command, start_new_session=True)
            
        print("[SUCCESS] Streamlit dashboard launched. Please wait a moment for it to open in your browser.")
        
    except Exception as e:
        print(f"[ERROR] Failed to launch Streamlit dashboard: {str(e)}")
        print("You can manually launch the dashboard by running: streamlit run dashboard.py")

def scrape_and_analyze(driver, post_url, mongo_uri, db_name):
    # Phase 1: Scrape data
    print("\n=== Phase 1: Data Collection ===")
    print("[DEBUG] Starting comment extraction...")
    comments = scrape_comments(driver, post_url)
    print(f"[SUCCESS] Successfully scraped {len(comments)} comments")
    
    # Store in MongoDB
    print("[DEBUG] Saving comments to MongoDB...")
    test_mongo_connection(mongo_uri, 'json', db_name)
    
    # Phase 2: Analyze data
    print("\n=== Phase 2: Data Analysis ===")
    output_dir = 'output7'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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

    # Generate and save reports
    output_file = os.path.join(output_dir, 'custom_analyzed_comments.json')
    save_analyzed_data(analyzed_comments, output_file)
    
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
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    
    # Validate required environment variables
    required_vars = {
        "LINKEDIN_EMAIL": linkedin_email,
        "LINKEDIN_PASSWORD": linkedin_password,
        "MONGO_URI": mongo_uri,
        "DB_NAME": db_name
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print(f"[ERROR] Missing required environment variables: {', '.join(missing_vars)}")
        return

    # Get LinkedIn post URL from user
    url_input = LinkedInURLInput()
    post_url = url_input.get_url()
    
    if not post_url:
        print("[ERROR] No URL provided. Exiting...")
        return

    try:
        # Initialize driver and login
        driver = setup_firefox_driver()
        if not login(driver, linkedin_email, linkedin_password):
            print("[ERROR] Login failed, stopping execution")
            driver.quit()
            return

        # Execute scraping and analysis pipeline
        analyzed_comments, report = scrape_and_analyze(driver, post_url, mongo_uri, db_name)
        
        print("\n=== Process Complete ===")
        print(f"Successfully processed {len(analyzed_comments)} comments")
        
        # Launch Streamlit dashboard
        launch_streamlit_dashboard()
        
    except Exception as e:
        print(f"[ERROR] An error occurred during execution: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()