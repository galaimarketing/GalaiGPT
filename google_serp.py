from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

def search_google_web_automation(query, chrome_driver_path):
    try:
        # Set up Chrome WebDriver with options
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode (no GUI)
        options.add_argument("--disable-gpu")  # Disable GPU acceleration
        options.add_argument("--no-sandbox")  # Disable sandboxing for Linux
        options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage for Linux
        options.add_argument("--disable-infobars")  # Disable infobars
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Specify the path to your Chrome WebDriver executable
        driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
        
        # Use stealth mode to make the bot appear more like a human user
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Linux x86_64",  # Change this to match your Linux platform
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        n_pages = 2
        results = []
        counter = 0
        for page in range(1, n_pages):
            url = (
                "http://www.google.com/search?q="
                + str(query)
                + "&start="
                + str((page - 1) * 10)
            )

            driver.get(url)
            time.sleep(2)  # Wait for the page to load (adjust as needed)
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            search = soup.find_all("div", class_="tF2Cxc")
            for h in search:
                counter = counter + 1
                title = h.h3.text
                link = h.a.get("href")
                rank = counter
                results.append(
                    {
                        "title": h.h3.text,
                        "url": link,
                        "domain": urlparse(link).netloc,
                        "rank": rank,
                    }
                )
        
        driver.quit()  # Close the WebDriver when done
        return results[:3]
    except Exception as e:
        return str(e)

# Example usage:
chrome_driver_path = "/workspaces/galaigpt/usr/local/bin/chromedriver" 
search_query = "Your search query here"
search_results = search_google_web_automation(search_query, chrome_driver_path)
for result in search_results:
    print(result)
