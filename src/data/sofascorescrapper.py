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
    """Starts and returns the Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Launch browser in full screen
    options.add_argument("--disable-notifications")  # Disable notifications
    # options.add_argument("--headless")  # Uncomment to run in headless mode

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# Login to Sofascore site
def sofascore_login():
    """Logs into the Sofascore website."""
    driver = start_driver()
    url = "https://www.sofascore.com/en/"
    driver.get(url)
    print(f"Accessed {url}.")

    return driver


def search_league(driver, league_name="Trendyol Süper Lig"):
    """
    Searches for a league name in Sofascore and selects the first result.
    :param driver: Selenium WebDriver instance
    :param league_name: Name of the league to search for (default: "Trendyol Süper Lig")
    """
    try:
        # Locate the search box
        search_box_xpath = '//*[@id="search-input"]'
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, search_box_xpath))
        )
        search_box.send_keys(league_name)

        # Select the first result
        first_result_xpath = '//*[@id="__next"]/header/div[1]/div/div/div[2]/div/div/div[2]/div[1]/div/div/a/div'
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, first_result_xpath))
        )
        first_result.click()
        print(f"Searched for '{league_name}' and clicked the first result.")

    except Exception as e:
        print("An error occurred:", str(e))


def handle_matches_popup(driver):
    """
    Clicks the specified button in the matches section to close the popup.
    Then scrolls the page slightly upwards.
    :param driver: Selenium WebDriver instance
    """
    try:
        # XPath of the button
        popup_button_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[1]/div/div[2]/div[3]/div/div/div/div[3]/button'

        # Find and click the button
        popup_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, popup_button_xpath))
        )
        popup_button.click()
        print("Clicked and closed the popup button.")

        # Scroll the page upwards (e.g., -150 pixels)
        driver.execute_script("window.scrollBy(0, -150);")
        print("Scrolled the page upwards by 150 pixels.")

    except TimeoutException:
        print("Popup button was not found in time.")
    except Exception as e:
        print("An error occurred:", str(e))


def navigate_to_matches_section(driver):
    """
    Scrolls to the matches section for the specified season.
    :param driver: Selenium WebDriver instance
    """
    try:
        # XPath of the matches section
        matches_section_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[1]/div'

        # Find the matches section and scroll into view
        matches_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, matches_section_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", matches_section)
        print("Successfully scrolled to the matches section.")
    except TimeoutException:
        print("Matches section was not found.")
    except Exception as e:
        print("An error occurred:", str(e))


def sanitize_file_name(file_name):
    """
    Creates a valid file name by removing invalid characters.
    :param file_name: Original file name
    :return: Sanitized file name
    """
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        file_name = file_name.replace(char, '_')
    return file_name


# Function to create or append to CSV files
def create_or_append_csv(base_path, file_name, headers, data):
    """
    Creates or appends to a specified CSV file at the given path.
    :param base_path: Directory where the file will be saved
    :param file_name: Name of the CSV file
    :param headers: Column headers for the CSV
    :param data: Data row to append (list)
    """
    # Create file path
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
    Navigates through seasons, extracts data from each tab and week.
    :param driver: Selenium WebDriver instance
    """
    try:
        button_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div[2]/div/div/div/div/button'
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        button.click()
        print("Clicked the button to open season selection.")

        list_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div[2]/div/div/div/div/div/div/div/ul'
        season_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
        )

        for i in range(1, min(6, len(season_items))):  # Skip the first item, up to 5 tabs
            season_xpath = f'({list_xpath})/li[{i + 1}]'
            season_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, season_xpath))
            )
            season_name = season_element.text
            season_element.click()
            print(f"Switched to season '{season_name}'.")
            time.sleep(3)

            # Scroll down by a certain pixel amount
            scroll_down(driver, 3500)  # Scroll down 3500 pixels
            print("Scrolled the page down by 3500 pixels.")

            time.sleep(2)
            # Click and close the popup button
            handle_matches_popup(driver)
            # Focus on the table containing teams and players
            # scrape_team_and_player_data(driver, season_name)

            # Scroll to the matches section
            navigate_to_matches_section(driver)

            # Navigate through weeks and save data
            navigate_and_scrape_weeks(driver, season_name)

            driver.back()
            print(f"Exited season '{season_name}' and returned to the list.")

            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button.click()

    except Exception as e:
        print("An error occurred:", str(e))


def scroll_down(driver, pixels):
    """
    Scrolls the page down by a specified number of pixels.
    :param driver: Selenium WebDriver instance
    :param pixels: Number of pixels to scroll down
    """
    try:
        driver.execute_script(f"window.scrollBy(0, {pixels});")
        print(f"Scrolled the page down by {pixels} pixels.")
    except Exception as e:
        print("An error occurred while scrolling the page:", str(e))


def scrape_team_and_player_data(driver, season_name):
    """
    Extracts data of teams and players from the table and navigates through pages.
    :param driver: Selenium WebDriver instance
    :param season_name: Name of the current season being scraped
    """
    try:
        # Create directory path for the current season
        base_path = os.path.join(r"C:\Users\mbaki\Desktop\Proje\data\raw", sanitize_file_name(season_name))
        os.makedirs(base_path, exist_ok=True)  # Create directory if it doesn't exist

        sanitized_season_name = sanitize_file_name(season_name)  # Sanitized file name
        csv_file_name = f"{sanitized_season_name}_teams_and_players.csv"
        csv_headers = ["Season", "Team Name", "Player Name", "Player Rating"]
        snumber = 1
        while True:
            try:
                # Locate the table and get all rows
                table_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[5]/div/div[4]/div/table/tbody'
                table_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, table_xpath))
                )
                rows = table_element.find_elements(By.XPATH, './tr')  # All rows in the table

                for i, row in enumerate(rows, start=1):
                    try:
                        # Extract team name
                        team_name_xpath = f'./td[2]/a/img'
                        team_name_element = row.find_element(By.XPATH, team_name_xpath)
                        team_name = team_name_element.get_attribute('alt')

                        # Extract player name
                        player_name_xpath = f'./td[3]'
                        player_name_element = row.find_element(By.XPATH, player_name_xpath)
                        player_name = player_name_element.get_attribute('title')

                        # Extract player rating
                        try:
                            rating_xpath = f'./td[10]/div/div/span'
                            rating_element = row.find_element(By.XPATH, rating_xpath)
                            player_rating = rating_element.get_attribute('aria-valuenow')
                        except Exception:
                            player_rating = "0"  # Set to 0 if error occurs

                        # Row to write to CSV
                        csv_row = [season_name, team_name, player_name, player_rating]
                        create_or_append_csv(base_path, csv_file_name, csv_headers, csv_row)

                    except Exception as e:
                        print(f"Error extracting data from row {i}:", str(e))

                # Click the button to change the page
                next_button_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[5]/div/div[4]/div/div/button[2]'
                next_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, next_button_xpath))
                )

                # If the button has the "disabled" attribute, exit the loop
                if next_button.get_attribute('disabled'):
                    print("Reached the last page. Completed processing.")
                    break

                # Click the button to go to the next page
                next_button.click()
                print(f"Moved to page {snumber}.")
                time.sleep(2)  # Wait for the page to load

            except Exception as e:
                print("An error occurred while processing the table or button:", str(e))
                break
            snumber += 1
        print(f"All data saved to '{csv_file_name}'.")

    except TimeoutException:
        print("Table was not found.")
    except Exception as e:
        print("An error occurred while extracting team and player data:", str(e))


def navigate_and_scrape_weeks(driver, season_name):
    """
    Clicks through weeks sequentially to extract and save their data.
    First retrieves the current week's name, then changes the week and saves its data.
    :param driver: Selenium WebDriver instance
    :param season_name: Name of the current season being scraped
    """
    try:
        week_button_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[1]/div/div[1]/button[1]'
        week_name_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[1]/div/div[2]/span'
        n = 500
        while True:  # Continue until all weeks are processed
            n -= 1
            try:
                if n <= 600:
                    # Get the week's name
                    week_name_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, week_name_xpath))
                    )
                    week_name = week_name_element.text  # Name of the week
                    print(f"Processing data for week '{week_name}'...")

                    # Extract and save data from the week
                    scrape_data_from_week(driver, week_name, season_name)

                # Change the week
                week_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, week_button_xpath))
                )
                week_button.click()
                # print(f"Exited week '{week_name}' in season '{season_name}', moving to the next week.")

            except TimeoutException:
                # If the week button is not found, the season has ended
                print("Week button not found. The season has ended.")
                break

    except Exception as e:
        print("An error occurred:", str(e))


def get_matches(driver, match_table_xpath):
    matches_xpath = f"{match_table_xpath}/a"
    matches = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, matches_xpath))
    )
    return matches


def get_basic_match_info(driver, matches_xpath, i):
    """
    Retrieves basic match information. Returns None if the match is "Postponed".
    """
    try:
        # XPath of the specific match
        match_xpath = f"{matches_xpath}[{i}]"
        match_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, match_xpath))
        )

        # Check if the match is "Postponed"
        ertelendi_xpath = f"{match_xpath}/div/div/div[2]/div/span[1]/bdi"
        try:
            ertelendi_element = match_element.find_element(By.XPATH, f".//div/div/div[2]/div/span[1]/bdi")
            ertelendi_text = ertelendi_element.text.strip()
            if ertelendi_text == "Postponed":
                print(f"Match {i} is marked as 'Postponed', skipping.")
                return None  # Return None to skip this match
            if ertelendi_text == "Abandoned":
                print(f"Match {i} is marked as 'Postponed', skipping.")
                return None  # Return None to skip this match
        except Exception:
            # If "Postponed" label is not present, continue
            pass

        # Continue extracting match information
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
    performance_tab_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div/div/h2[2]'
    performance_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, performance_tab_xpath))
    )
    performance_tab.click()
    time.sleep(1)


def get_performance_values(driver):
    # Define XPaths
    home_performance_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div[1]/div/div/div/div/span/div'
    away_performance_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[5]/div/div[1]/div/div/div/div/span/div'
    home_formation_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div/div[2]/span'
    away_formation_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[5]/div/div[2]/span'
    scrollbar_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[3]/div'

    # Function to get performance data using JavaScript
    def get_performance(driver, xpath):
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
            return None  # Return None or a default value if conversion fails

    # Wait for the scrollbar element and define the action
    scrollbar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, scrollbar_xpath))
    )
    action = ActionChains(driver)

    # 1. Scroll the scrollbar 60 pixels down
    action.click_and_hold(scrollbar).move_by_offset(0, 60).release().perform()
    time.sleep(1)  # Wait for the scroll action

    # 2. Get home team performance
    home_performance = get_performance(driver, home_performance_xpath)

    # 3. Get home team formation
    home_formation = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, home_formation_xpath))
    ).text

    # 4. Extract home team players' names
    home_players_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[3]/div[1]//span[@class="Text biiPGw"]'
    home_players_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, home_players_xpath))
    )
    home_players = [player.text for player in home_players_elements]

    # 5. Scroll the scrollbar 150 pixels down
    action.click_and_hold(scrollbar).move_by_offset(0, 150).release().perform()
    time.sleep(1)  # Wait for the scroll action

    # 6. Get away team performance
    away_performance = get_performance(driver, away_performance_xpath)

    # 7. Get away team formation
    away_formation = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, away_formation_xpath))
    ).text

    # 8. Extract away team players' names
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


def scrape_data_from_week(driver, week_name, season_name):
    """
    Extracts match data from a week and saves it to the corresponding season's CSV file.
    """
    try:
        print(f"Starting data extraction for week '{week_name}' in season '{season_name}'.")

        # XPath of the matches table
        match_table_xpath = '//*[@id="__next"]/main/div/div[3]/div/div[1]/div[1]/div[3]/div[3]/div/div[1]/div/div[2]'

        # Get matches
        matches = get_matches(driver, match_table_xpath)

        # Create directory path for the current season
        base_path = os.path.join(r"C:\Users\mbaki\Desktop\Proje\data\raw", sanitize_file_name(season_name))
        os.makedirs(base_path, exist_ok=True)  # Create directory if it doesn't exist

        sanitized_season_name = sanitize_file_name(season_name)  # Sanitized file name
        csv_file_name = f"{sanitized_season_name}.csv"
        csv_headers = [
            "Season", "Week", "Match Date", "Home Team", "Away Team",
            "Home Goals", "Away Goals",
            "Home Performance", "Away Performance",
            "Home Formation", "Away Formation",
            "Home Players", "Away Players"
        ]

        # XPath for individual matches
        matches_xpath = f"{match_table_xpath}/a"
        for i, match in enumerate(matches, start=1):
            try:
                # Get basic match information
                basic_info = get_basic_match_info(driver, matches_xpath, i)
                if basic_info is None:
                    continue  # Skip "Postponed" matches

                match_date, home_team, away_team, home_score, away_score = basic_info

                # Click the match to open details
                match.click()

                # Navigate to the performance tab
                navigate_to_performance_tab(driver)

                # Get performance values
                performance_data = get_performance_values(driver)
                home_performance = performance_data.get('home_performance', None)
                away_performance = performance_data.get('away_performance', None)
                home_formation = performance_data.get('home_formation', None)
                away_formation = performance_data.get('away_formation', None)
                home_players = performance_data.get('home_players', [])
                away_players = performance_data.get('away_players', [])

                # Convert player lists to semicolon-separated strings
                home_players_str = "; ".join(home_players)
                away_players_str = "; ".join(away_players)

                # Row to write to CSV
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

                # Write to CSV
                create_or_append_csv(
                    base_path,
                    csv_file_name,
                    csv_headers,
                    csv_row
                )

                print(f"Successfully extracted and saved data for match {i}.")

            except Exception as e:
                print(f"An error occurred while extracting data for match {i}:", str(e))
                # Additional error handling can be added here

        print(f"Data for week '{week_name}' has been saved to '{csv_file_name}'.")

    except TimeoutException:
        print(f"Data for week '{week_name}' could not be found.")
    except Exception as e:
        print(f"An error occurred while extracting data for week '{week_name}':", str(e))


if __name__ == "__main__":
    # Initialize the driver and access the site
    driver = sofascore_login()

    # Search for the league and click the first result
    search_league(driver, "Trendyol Süper Lig")

    # Navigate through seasons
    navigate_and_scrape_seasons(driver)

    # Optionally, close the browser after testing (commented out for development purposes)
    # driver.quit()