from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

def search_and_scrape_reviews(app_name, max_scrolls=20):
    """Search for an app on Google Play Store and scrape reviews."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get("https://play.google.com/store")
        time.sleep(3)
        
        search_icon = driver.find_element(By.XPATH, '//i[@aria-hidden="true" and contains(text(), "search")]')
        search_icon.click()
        search_box = driver.find_element(By.XPATH, '//input[@aria-label="Search Google Play"]')
        search_box.send_keys(app_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "details?id=")]'))
            )
            
            app_links = driver.find_elements(By.XPATH, '//a[contains(@href, "details?id=")]')
            print(f"Found {len(app_links)} app links.")
            
            for link in app_links:
                print(f"Link Text: {link.text}, Link Href: {link.get_attribute('href')}")
                if app_name.lower() in link.text.lower():
                    print(f"Clicking on the link for {app_name}.")
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(5)
                    break
            else:
                raise Exception(f"No link found for the app {app_name}.")
            
            current_url = driver.current_url
            print(f"Current URL: {current_url}")
            if "details?id=" not in current_url:
                raise Exception("Navigation to app page failed.")
            
            print("Navigated to app page successfully!")

        except Exception as e:
            print(f"Error during app link navigation: {e}")
            driver.quit()
            return

        try:
            reviews_button = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//span[text()="See all reviews"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", reviews_button)
            time.sleep(2)
            driver.execute_script("arguments[0].click();", reviews_button)
            print("Clicked on the 'See all reviews' button successfully!")
        except Exception as e:
            print(f"Error while locating or clicking the 'See all reviews' button: {e}")
            driver.quit()
            return

        for _ in range(max_scrolls):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        reviews = []
        ratings = []
        dates = []

        try:
            review_elements = soup.find_all("div", class_="h3YV2d")
            rating_elements = soup.find_all("div", {"role": "img", "aria-label": True})
            date_elements = soup.find_all("span", class_="bp9Aid")

            for i in range(len(review_elements)):
                try:
                    review = review_elements[i].text.strip() if review_elements[i] else "No review"
                    rating = float(rating_elements[i]["aria-label"].split()[1]) if i < len(rating_elements) else None
                    date = date_elements[i].text.strip() if i < len(date_elements) else "No date"
                except Exception as e:
                    print(f"Skipping a review due to an error: {e}")
                    continue

                reviews.append(review)
                ratings.append(rating)
                dates.append(date)

        except Exception as e:
            print(f"Error extracting data: {e}")

        min_length = min(len(reviews), len(ratings), len(dates))
        reviews = reviews[:min_length]
        ratings = ratings[:min_length]
        dates = dates[:min_length]

        df = pd.DataFrame({"Review": reviews, "Rating": ratings, "Date": dates})
        output_file = "google_play_reviews.csv"
        df.to_csv(output_file, index=False)
        print(f"Scraped {len(reviews)} reviews and saved them to {output_file}.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

app_name = input("Enter the app name to search on Google Play Store: ")
search_and_scrape_reviews(app_name)
