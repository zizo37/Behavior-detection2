from selenium.webdriver.common.by import By
import time

#Gère l'authentification à LinkedIn
def login(driver, email, password):
    try:
        print("[DEBUG] Navigating to LinkedIn login page...")
        driver.get('https://www.linkedin.com/login')
        time.sleep(3)
        
        print("[DEBUG] Finding and filling email field...")
        email_field = driver.find_element(By.ID, 'username')
        #Simule une saisie humaine
        for char in email:
            email_field.send_keys(char)
            time.sleep(0.05) 
        print("[SUCCESS] Email entered")
        
        print("[DEBUG] Finding and filling password field...")
        password_field = driver.find_element(By.ID, 'password')
        #Simule une saisie humaine
        for char in password:
            password_field.send_keys(char)
            time.sleep(0.05) 
        print("[SUCCESS] Password entered")
        
        print("[DEBUG] Clicking login button...")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        time.sleep(5)
        
        #Gère les cas particuliers 
        if "checkpoint" in driver.current_url:
            print("[WARNING] LinkedIn has flagged your login as suspicious. Please solve the problem.")
            input("Press Enter once you've solved the problem...")
            print("[DEBUG] Continuing with login...")
            time.sleep(2)
            if "feed" in driver.current_url:
                print("[SUCCESS] Login successful")
                return True
            else:
                print("[WARNING] Login might have failed - unexpected URL")
                time.sleep(8)
                return False
        elif "feed" in driver.current_url:
            #Vérifie le succès de la connexion
            print("[SUCCESS] Login successful")
            return True
        else:
            print("[WARNING] Login might have failed - unexpected URL")
            time.sleep(8)
            return False
            
    except Exception as e:
        print(f"[ERROR] Login failed: {str(e)}")
        return False