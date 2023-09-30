from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def search_google_web_automation(query):
    # Set up Chrome WebDriver options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")  # Disable GPU acceleration for headless mode
    options.add_argument("--no-sandbox")  # Disable sandboxing for headless mode

    # Create Chrome WebDriver using ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Linux",  # Change platform to Linux
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

    # Don't forget to close the driver when you're done with it
    driver.quit()

    return results[:3]
