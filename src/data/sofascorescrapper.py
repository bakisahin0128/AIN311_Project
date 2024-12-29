from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time
import csv
import os


# Chrome WebDriver initializer
def start_driver():
    """
    Initializes and returns a Chrome WebDriver instance with specified options.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Launch browser in full screen
    options.add_argument("--disable-notifications")  # Disable browser notifications
    # options.add_argument("--headless")  # Uncomment to run in headless mode

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# Login to Sofascore site
def sofascore_login():
    """
    Navigates to the Sofascore website and returns the WebDriver instance.

    Returns:
        webdriver.Chrome: WebDriver instance after accessing the Sofascore homepage.
    """
    driver = start_driver()
    url = "https://www.sofascore.com/en/"
    driver.get(url)
    print(f"Accessed {url}.")

    return driver


def search_league(driver, league_name="Trendyol Süper Lig"):
    """
    Searches for a specified league on Sofascore and selects the first search result.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        league_name (str, optional): Name of the league to search for. Defaults to "Trendyol Süper Lig".
    """
    try:
        # Locate the search box using XPath
        search_box_xpath = '//*[@id="search-input"]'
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, search_box_xpath))
        )
        search_box.send_keys(league_name)

        # Locate and click the first search result
        first_result_xpath = '//*[@id="__next"]/header/div[1]/div/div[2]/div/div/div[2]/div[1]/div/div/a/div'
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, first_result_xpath))
        )
        first_result.click()
        print(f"Searched for '{league_name}' and clicked the first result.")

    except Exception as e:
        print("An error occurred while searching for the league:", str(e))


def handle_matches_popup(driver):
    """
    Closes the matches popup by clicking the specified button and scrolls the page slightly upwards.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    try:
        # XPath of the popup close button
        popup_button_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[1]/div/div[2]/div[3]/div/div/div/div[3]/button'

        # Find and click the popup close button
        popup_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, popup_button_xpath))
        )
        popup_button.click()
        print("Clicked and closed the popup button.")

        # Scroll the page upwards by 150 pixels
        driver.execute_script("window.scrollBy(0, -150);")
        print("Scrolled the page upwards by 150 pixels.")

    except TimeoutException:
        print("Popup button was not found within the timeout period.")
    except Exception as e:
        print("An error occurred while handling the popup:", str(e))


def navigate_to_matches_section(driver):
    """
    Scrolls the webpage to bring the matches section into view.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    try:
        # XPath of the matches section
        matches_section_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[1]/div'

        # Locate the matches section and scroll it into view
        matches_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, matches_section_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", matches_section)
        print("Successfully scrolled to the matches section.")
    except TimeoutException:
        print("Matches section was not found within the timeout period.")
    except Exception as e:
        print("An error occurred while navigating to the matches section:", str(e))


def sanitize_file_name(file_name):
    """
    Sanitizes a string to be a valid file name by replacing invalid characters.

    Args:
        file_name (str): Original file name.

    Returns:
        str: Sanitized file name.
    """
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        file_name = file_name.replace(char, '_')
    return file_name


def create_or_append_csv(base_path, file_name, headers, data):
    """
    Creates a new CSV file with headers or appends data to an existing CSV file.

    Args:
        base_path (str): Directory where the CSV file will be saved.
        file_name (str): Name of the CSV file.
        headers (list): List of column headers for the CSV.
        data (list): Data row to append to the CSV.
    """
    # Create the full file path
    file_path = os.path.join(base_path, file_name)
    os.makedirs(base_path, exist_ok=True)  # Create directory if it doesn't exist

    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write headers if the file is new
        if not file_exists:
            writer.writerow(headers)

        # Append the data row
        writer.writerow(data)


def navigate_and_scrape_seasons(driver):
    """
    Navigates through available seasons, extracts data from each season, and processes it.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    try:
        # XPath of the button to open season selection
        button_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div[2]/div/div/div/div/button'
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        button.click()
        print("Clicked the button to open season selection.")

        # XPath of the seasons list
        list_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div[2]/div/div/div/div/div/div/div/ul'
        season_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
        )

        # Iterate through the seasons (starting from index 4 up to 5)
        for i in range(4, min(5, len(season_items))):
            season_xpath = f'({list_xpath})/li[{i + 1}]'
            season_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, season_xpath))
            )
            season_name = season_element.text
            season_element.click()
            print(f"Switched to season '{season_name}'.")
            time.sleep(3)

            # Scroll down by 3500 pixels
            scroll_down(driver, 3500)
            print("Scrolled the page down by 3500 pixels.")

            time.sleep(2)
            # Handle any potential popup
            handle_matches_popup(driver)

            # Scroll to the matches section
            navigate_to_matches_section(driver)

            # Scrape data for each week within the season
            navigate_and_scrape_weeks(driver, season_name)

            # Navigate back to the seasons list
            driver.back()
            print(f"Exited season '{season_name}' and returned to the list.")

            # Re-open the season selection button for the next iteration
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button.click()

    except Exception as e:
        print("An error occurred while navigating and scraping seasons:", str(e))


def scroll_down(driver, pixels):
    """
    Scrolls the webpage down by a specified number of pixels.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        pixels (int): Number of pixels to scroll down.
    """
    try:
        driver.execute_script(f"window.scrollBy(0, {pixels});")
        print(f"Scrolled the page down by {pixels} pixels.")
    except Exception as e:
        print("An error occurred while scrolling the page:", str(e))


def scrape_team_and_player_data(driver, season_name):
    """
    Extracts team and player data from the table and saves it to a CSV file.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        season_name (str): Name of the current season being scraped.
    """
    try:
        # Define the base directory path for saving data
        base_path = os.path.join(r"C:\Users\mbaki\Desktop\Proje\data\raw", sanitize_file_name(season_name))
        os.makedirs(base_path, exist_ok=True)  # Create directory if it doesn't exist

        # Define CSV file name and headers
        csv_file_name = f"{sanitize_file_name(season_name)}_teams_and_players.csv"
        csv_headers = ["Season", "Team Name", "Player Name", "Player Rating"]

        page_number = 1
        while True:
            try:
                # XPath of the table body containing team and player data
                table_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[5]/div/div[4]/div/table/tbody'
                table_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, table_xpath))
                )
                rows = table_element.find_elements(By.XPATH, './tr')  # All rows in the table

                # Iterate through each row to extract data
                for i, row in enumerate(rows, start=1):
                    try:
                        # Extract team name from the image alt attribute
                        team_name_xpath = f'./td[2]/a/img'
                        team_name_element = row.find_element(By.XPATH, team_name_xpath)
                        team_name = team_name_element.get_attribute('alt')

                        # Extract player name from the title attribute
                        player_name_xpath = f'./td[3]'
                        player_name_element = row.find_element(By.XPATH, player_name_xpath)
                        player_name = player_name_element.get_attribute('title')

                        # Extract player rating; default to "0" if not available
                        try:
                            rating_xpath = f'./td[9]/div/div/span'
                            rating_element = row.find_element(By.XPATH, rating_xpath)
                            player_rating = rating_element.get_attribute('aria-valuenow')
                        except Exception:
                            player_rating = "0"  # Set to 0 if rating is unavailable

                        # Prepare the row data for CSV
                        csv_row = [season_name, team_name, player_name, player_rating]
                        create_or_append_csv(base_path, csv_file_name, csv_headers, csv_row)

                    except Exception as e:
                        print(f"Error extracting data from row {i}:", str(e))

                # XPath of the 'Next' button to navigate through table pages
                next_button_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[5]/div/div[4]/div/div/button[2]'
                next_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, next_button_xpath))
                )

                # Check if the 'Next' button is disabled, indicating the last page
                if next_button.get_attribute('disabled'):
                    print("Reached the last page. Completed processing.")
                    break

                # Click the 'Next' button to go to the next page
                next_button.click()
                print(f"Moved to page {page_number}.")
                time.sleep(2)  # Wait for the next page to load

            except Exception as e:
                print("An error occurred while processing the table or button:", str(e))
                break
            page_number += 1

        print(f"All data saved to '{csv_file_name}'.")

    except TimeoutException:
        print("Table was not found within the timeout period.")
    except Exception as e:
        print("An error occurred while extracting team and player data:", str(e))


def navigate_and_scrape_weeks(driver, season_name):
    """
    Iterates through each week in the current season to extract and save match data.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        season_name (str): Name of the current season being scraped.
    """
    try:
        # XPath of the week navigation button and week name display
        week_button_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[1]/div/div[1]/button[1]'
        week_name_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[1]/div/div[2]/span'
        max_weeks = 43  # Maximum number of weeks to process

        for _ in range(max_weeks):  # Iterate until all weeks are processed
            try:
                # Retrieve the current week's name
                week_name_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, week_name_xpath))
                )
                week_name = week_name_element.text  # Name of the current week
                print(f"Processing data for week '{week_name}'...")

                # Extract and save data from the current week
                scrape_data_from_week(driver, week_name, season_name)

                # Click the button to navigate to the next week
                week_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, week_button_xpath))
                )
                week_button.click()

            except TimeoutException:
                # If the week button is not found, assume the season has ended
                print("Week button not found. The season has ended.")
                break
            except Exception as e:
                print("An error occurred while navigating weeks:", str(e))
                break

    except Exception as e:
        print("An error occurred while navigating and scraping weeks:", str(e))


def get_matches(driver, match_table_xpath):
    """
    Retrieves all match elements from the matches table.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        match_table_xpath (str): XPath of the matches table.

    Returns:
        list: List of match WebElement objects.
    """
    matches_xpath = f"{match_table_xpath}/a"
    matches = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, matches_xpath))
    )
    return matches


def get_basic_match_info(driver, matches_xpath, i):
    """
    Retrieves basic information about a specific match, skipping if the match is postponed or abandoned.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        matches_xpath (str): Base XPath for matches.
        i (int): Index of the match to retrieve information for.

    Returns:
        tuple or None: Tuple containing match date, home team, away team, home score, and away score.
                       Returns None if the match is postponed or abandoned.
    """
    try:
        # XPath of the specific match
        match_xpath = f"{matches_xpath}[{i}]"
        match_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, match_xpath))
        )

        # Check if the match is "Postponed" or "Abandoned"
        postponed_xpath = f"{match_xpath}/div/div/div[2]/div/span[1]/bdi"
        try:
            postponed_element = match_element.find_element(By.XPATH, ".//div/div/div[2]/div/span[1]/bdi")
            postponed_text = postponed_element.text.strip()
            if postponed_text in ["Postponed", "Abandoned"]:
                print(f"Match {i} is marked as '{postponed_text}', skipping.")
                return None  # Skip postponed or abandoned matches
        except Exception:
            # If "Postponed" or "Abandoned" label is not present, continue
            pass

        # Extract match details
        match_date_xpath = f"{match_xpath}/div/div/div[2]/bdi"
        home_team_xpath = f"{match_xpath}/div/div/div[4]/div/div[1]/div[1]/bdi"
        away_team_xpath = f"{match_xpath}/div/div/div[4]/div/div[1]/div[2]/bdi"
        home_score_xpath = f"{match_xpath}/div/div/div[4]/div/div[3]/div[1]/span[1]"
        away_score_xpath = f"{match_xpath}/div/div/div[4]/div/div[3]/div[2]/span[1]"

        match_date = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, match_date_xpath))
        ).text.strip()
        home_team = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, home_team_xpath))
        ).text.strip()
        away_team = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, away_team_xpath))
        ).text.strip()
        home_score = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, home_score_xpath))
        ).text.strip()
        away_score = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, away_score_xpath))
        ).text.strip()

        return match_date, home_team, away_team, home_score, away_score

    except TimeoutException:
        print(f"Match {i} information could not be retrieved (timeout).")
        return None
    except Exception as e:
        print(f"An error occurred while retrieving match {i} information:", str(e))
        return None


def navigate_to_performance_tab(driver):
    """
    Navigates to the performance tab within a match's detailed view.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    performance_tab_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div/div/h2[2]'
    performance_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, performance_tab_xpath))
    )
    performance_tab.click()
    time.sleep(1)  # Wait briefly for the tab to load


def get_performance_values(driver):
    """
    Extracts performance metrics and player information from the performance tab.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        dict: Dictionary containing home and away performance metrics, formations, and player names.
    """
    # Define XPaths for various performance metrics and elements
    home_performance_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div/div/span/div'
    away_performance_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[5]/div/div[1]/div/div/div/div/span/div'
    home_formation_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div[2]/span'
    away_formation_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[5]/div/div[2]/span'
    scrollbar_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[3]/div'

    def get_performance(driver, xpath):
        """
        Retrieves the performance value using JavaScript to access computed styles.

        Args:
            driver (webdriver.Chrome): Selenium WebDriver instance.
            xpath (str): XPath of the element to retrieve the performance value from.

        Returns:
            float or None: Performance value as a float, or None if conversion fails.
        """
        script = (
            "return window.getComputedStyle("
            "document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue, "
            "'::after'"
            ").getPropertyValue('content');"
        )
        performance = driver.execute_script(script, xpath).strip('"')
        try:
            return float(performance)
        except ValueError:
            return None  # Return None if conversion fails

    try:
        # Wait for the scrollbar element and define the action chain
        scrollbar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, scrollbar_xpath))
        )
        action = ActionChains(driver)

        # Scroll the scrollbar 60 pixels down
        action.click_and_hold(scrollbar).move_by_offset(0, 60).release().perform()
        time.sleep(1)  # Wait for the scroll action to take effect

        # Retrieve home team performance
        home_performance = get_performance(driver, home_performance_xpath)

        # Retrieve home team formation
        home_formation = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, home_formation_xpath))
        ).text

        # Extract home team players' names
        home_players_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[3]/div[1]//span[@class="Text biiPGw"]'
        home_players_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, home_players_xpath))
        )
        home_players = [player.text for player in home_players_elements]

        # Scroll the scrollbar an additional 150 pixels down
        action.click_and_hold(scrollbar).move_by_offset(0, 150).release().perform()
        time.sleep(1)  # Wait for the scroll action to take effect

        # Retrieve away team performance
        away_performance = get_performance(driver, away_performance_xpath)

        # Retrieve away team formation
        away_formation = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, away_formation_xpath))
        ).text

        # Extract away team players' names
        away_players_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[4]/div[1]//span[@class="Text biiPGw"]'
        away_players_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, away_players_xpath))
        )
        away_players = [player.text for player in away_players_elements]

        return {
            'home_performance': home_performance,
            'home_formation': home_formation,
            'home_players': home_players,
            'away_performance': away_performance,
            'away_formation': away_formation,
            'away_players': away_players
        }

    except Exception as e:
        print("An error occurred while retrieving performance values:", str(e))
        return {
            'home_performance': None,
            'home_formation': None,
            'home_players': [],
            'away_performance': None,
            'away_formation': None,
            'away_players': []
        }


def scrape_data_from_week(driver, week_name, season_name):
    """
    Extracts match data from a specific week and saves it to the corresponding season's CSV file.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        week_name (str): Name of the current week being scraped.
        season_name (str): Name of the current season being scraped.
    """
    try:
        print(f"Starting data extraction for week '{week_name}' in season '{season_name}'.")

        # XPath of the matches table
        match_table_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[1]/div/div[2]'

        # Retrieve all match elements
        matches = get_matches(driver, match_table_xpath)

        # Define the base directory path for saving data
        base_path = os.path.join(r"C:\Users\mbaki\Desktop\Proje\data\raw", sanitize_file_name(season_name))
        os.makedirs(base_path, exist_ok=True)  # Create directory if it doesn't exist

        # Define CSV file name and headers
        csv_file_name = f"{sanitize_file_name(season_name)}.csv"
        csv_headers = [
            "Season", "Week", "Match Date", "Home Team", "Away Team",
            "Home Goals", "Away Goals",
            "Home Performance", "Away Performance",
            "Home Formation", "Away Formation",
            "Home Players", "Away Players"
        ]

        # Base XPath for individual matches
        matches_xpath = f"{match_table_xpath}/a"
        for i, match in enumerate(matches, start=1):
            try:
                # Retrieve basic match information
                basic_info = get_basic_match_info(driver, matches_xpath, i)
                if basic_info is None:
                    continue  # Skip matches that are postponed or abandoned

                match_date, home_team, away_team, home_score, away_score = basic_info

                # Click the match to open its detailed view
                match.click()

                # Navigate to the performance tab
                navigate_to_performance_tab(driver)

                # Extract performance metrics and player information
                performance_data = get_performance_values(driver)
                home_performance = performance_data.get('home_performance', None)
                away_performance = performance_data.get('away_performance', None)
                home_formation = performance_data.get('home_formation', None)
                away_formation = performance_data.get('away_formation', None)
                home_players = performance_data.get('home_players', [])
                away_players = performance_data.get('away_players', [])

                # Convert player lists to semicolon-separated strings for CSV
                home_players_str = "; ".join(home_players)
                away_players_str = "; ".join(away_players)

                # Prepare the row data for CSV
                csv_row = [
                    season_name,
                    week_name,
                    match_date,
                    home_team,
                    away_team,
                    home_score,
                    away_score,
                    home_performance,
                    away_performance,
                    home_formation,
                    away_formation,
                    home_players_str,
                    away_players_str
                ]

                # Write the row to the CSV file
                create_or_append_csv(
                    base_path,
                    csv_file_name,
                    csv_headers,
                    csv_row
                )

                print(f"Successfully extracted and saved data for match {i}.")

            except Exception as e:
                print(f"An error occurred while extracting data for match {i}:", str(e))
                # Additional error handling can be implemented here

        print(f"Data for week '{week_name}' has been saved to '{csv_file_name}'.")

    except TimeoutException:
        print(f"Data for week '{week_name}' could not be found within the timeout period.")
    except Exception as e:
        print(f"An error occurred while extracting data for week '{week_name}':", str(e))


if __name__ == "__main__":
    # Initialize the WebDriver and access the Sofascore website
    driver = sofascore_login()

    # Search for the specified league and click the first search result
    search_league(driver, "Trendyol Süper Lig")

    # Navigate through available seasons and scrape data
    navigate_and_scrape_seasons(driver)

    # Optionally, close the browser after scraping is complete (uncomment the line below)
    # driver.quit()
