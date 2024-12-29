import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def start_driver():
    """
    Initializes and returns a Chrome WebDriver instance with specified options.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Launch browser in full screen
    options.add_argument("--disable-notifications")  # Disable browser notifications
    # Uncomment the line below to enable headless mode (no GUI)
    # options.add_argument("--headless")

    # Disable images, stylesheets, cookies, and set JavaScript enabled
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.cookies": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.javascript": 1,
    }
    options.add_experimental_option("prefs", prefs)

    # Set page load strategy to 'eager' to start interacting with the page as soon as it's ready
    options.page_load_strategy = 'eager'

    # Initialize the WebDriver using ChromeDriverManager to handle driver binaries
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def check_and_accept_popup(driver):
    """
    Checks for a specific popup iframe on the Transfermarkt website and accepts it if found.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    try:
        wait = WebDriverWait(driver, 5)  # Reduced wait time for efficiency
        # Locate the iframe containing the popup
        iframe = wait.until(
            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'privacy-mgmt.com')]"))
        )
        driver.switch_to.frame(iframe)  # Switch to the iframe context
        # Locate and click the 'Accept' button within the popup
        accept_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Kabul et']"))
        )
        accept_button.click()
        driver.switch_to.default_content()  # Switch back to the main content
        print("Popup found and accepted.")
    except TimeoutException:
        # Popup not found within the timeout period
        print("Popup not found.")
    except NoSuchElementException:
        # Specific elements within the popup not found
        print("Popup element not found.")
    except Exception as e:
        print(f"An error occurred while checking for the popup: {e}")


def main():
    """
    Main function to execute the script.
    Reads player data from an input CSV, navigates to Transfermarkt to fetch age and market value,
    and writes the results to an output CSV.
    """
    # Paths to input and output CSV files
    INPUT_CSV = r'C:\Users\mbaki\Desktop\Proje\data\raw\20_21\20_21_teams_and_players.csv'  # Path to your input CSV
    OUTPUT_CSV = r'C:\Users\mbaki\Desktop\Proje\data\raw\20_21\20_21_marketvalue_and_age.csv'  # Path to your output CSV

    # Initialize the WebDriver
    driver = start_driver()
    wait = WebDriverWait(driver, 5)  # Reduced wait time for efficiency

    try:
        # Navigate to the main page of Transfermarkt
        driver.get('https://www.transfermarkt.com.tr/')

        # Check for and accept any popups
        check_and_accept_popup(driver)

        # Read the input CSV containing player information
        try:
            df_input = pd.read_csv(INPUT_CSV)
        except FileNotFoundError:
            print(f"Error: The file '{INPUT_CSV}' was not found.")
            driver.quit()
            return

        # List to store the results
        results = []

        # Iterate over each player in the input CSV
        for index, row in df_input.iterrows():
            season = row['Season']
            team_name = row['Team Name']
            player_name = row['Player Name']
            player_rating = row['Player Rating']

            print(f"Processing: {player_name} ({team_name})")

            try:
                # Locate the search input field and enter the player's name
                search_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="schnellsuche"]/input')))
                search_input.clear()
                search_input.send_keys(player_name)
                search_input.send_keys(Keys.RETURN)  # Press Enter to initiate the search

                # Wait for the player's age element to load and retrieve its text
                age_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="yw0"]/table/tbody/tr/td[4]'))
                )
                age = age_element.text.strip()

                # Wait for the player's market value element to load and retrieve its text
                market_value_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="yw0"]/table/tbody/tr/td[6]'))
                )
                market_value = market_value_element.text.strip()

                # Append the retrieved data to the results list
                results.append({
                    'Team Name': team_name,
                    'Player Name': player_name,
                    'Age': age,
                    'Market Value': market_value
                })

                print(f"Success: {player_name} - Age: {age}, Market Value: {market_value}")

                # Navigate back to the main page for the next search
                driver.get('https://www.transfermarkt.com.tr/')

            except Exception as e:
                print(f"Error: An error occurred while processing {player_name}. Error: {e}")
                # Optionally, append 'N/A' for age and market value if an error occurs
                results.append({
                    'Team Name': team_name,
                    'Player Name': player_name,
                    'Age': 'N/A',
                    'Market Value': 'N/A'
                })

            # Add a short wait between searches to avoid overloading the website
            time.sleep(0.5)  # Reduced wait time from 1 second to 0.5 seconds

        # Convert the results list to a DataFrame and save it to the output CSV
        df_output = pd.DataFrame(results)
        df_output.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

        print(f"All data has been saved to '{OUTPUT_CSV}'.")

    finally:
        # Close the WebDriver
        driver.quit()


if __name__ == "__main__":
    main()
