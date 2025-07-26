import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


import time



def scrape_website(website):
    print("Connecting to Scraping Browser...")
    
    chrome_driver_path = "./chromedriver.exe"
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service= Service(chrome_driver_path), options=options)
    try:
        driver.get(website)
        print("Page Loaded...")
        html = driver.page_source
        time.sleep(10)
        
        return html
    finally:
        driver.quit()
    

def extract_body_content(html_content):
    # Extract body content from HTML
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content):
    # Remove unnecessary characters and tags from body content
    soup = BeautifulSoup(body_content,"html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    
    return cleaned_content


def remove_unwanted_sections(html_content):
    """Remove header, footer, reviews, and other unwanted sections from the HTML content"""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Common class names and IDs for headers, footers, and reviews
    unwanted_selectors = [
        'header', 'footer',  # Standard HTML5 tags
        '[class*="header"]', '[class*="footer"]',  # Classes containing these words
        '[id*="header"]', '[id*="footer"]',
        '[class*="nav"]', '[id*="nav"]',  # Navigation elements
        '[class*="menu"]', '[id*="menu"]',
        '[class*="review"]', '[id*="review"]',  # Review sections
        '[class*="comment"]', '[id*="comment"]',
        '[class*="rating"]', '[id*="rating"]'
    ]
    
    # Remove elements matching the selectors
    for selector in unwanted_selectors:
        elements = soup.select(selector)
        for element in elements:
            element.decompose()
    
    return str(soup)


# LLM can process maximum 8000 character in one batch

def split_dom_content(dom_content, max_length=6000):
    # Use list comprehension instead of set for faster sequential access
    # Pre-calculate length once for better performance
    content_length = len(dom_content)
    return [
        dom_content[i:i + max_length] 
        for i in range(0, content_length, max_length)
    ]