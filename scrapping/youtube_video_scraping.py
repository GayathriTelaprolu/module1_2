import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_youtube_comments(video_url, max_comments=50):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Open the YouTube video URL
    driver.get(video_url)
    time.sleep(5)  # Allow time for the page to load
    
    # Scroll to load more comments
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    scroll_pause_time = 5

    # List to store the comments
    comment_texts = []

    # Extract comments until we reach the desired number
    while len(comment_texts) < max_comments:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(scroll_pause_time)
        
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'yt-formatted-string#content-text'))
            )
        except Exception as e:
            print(f"An error occurred while waiting for comments: {e}")
            driver.quit()
            return []

        # Extract comments and append them to the list
        comments = driver.find_elements(By.CSS_SELECTOR, 'span.yt-core-attributed-string--white-space-pre-wrap')

        for comment in comments:
            if len(comment_texts) >= max_comments:
                break
            text = comment.text
            emojis = comment.find_elements(By.CSS_SELECTOR, 'img.yt-core-image')
            
            # Replace emoji images with their alt text (emoji description)
            for emoji in emojis:
                text += emoji.get_attribute('alt')
            
            comment_texts.append(text)

        # Check if there are no new comments being loaded
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Close the browser
    driver.quit()

    # Return only the first 'max_comments' comments
    return comment_texts[:max_comments]

# Main function to scrape comments and save to CSV
if __name__ == "__main__":
    video_url = 'https://www.youtube.com/watch?v=Mu-eK72ioDk'  # Replace with your video URL
    
    # Scrape the first 50 comments
    max_comments = 50
    comments = scrape_youtube_comments(video_url, max_comments=max_comments)
    
    # Save comments to a CSV file
    if comments:
        df = pd.DataFrame(comments, columns=["Comments"])
        df.to_csv('youtube_comments.csv', index=False, encoding='utf-8')
        print(f"First {max_comments} comments have been successfully saved to 'youtube_comments.csv'")
    else:
        print("No comments found.")
