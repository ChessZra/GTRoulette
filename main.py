import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from data import Data as d
URL = 'https://growdice.co/games/roulette'
COOKIE_NAME = 'cf_clearance'
COOKIE_VALUE = 'Cg0wOmXw1I4r7yiinuasn3OYi7k8jfNUNQI58OEyUvs-1689887363-0-0.2.1689887363'
HTML = ['//a[@class="sc-17p4ij6-0 iQPzOp" and contains(text(), "Play Now!")]', "//div[@class='sc-1fxen5m-6 ACtPJ']", 'Players', '<div color="#ff3d2f" size="25" class="sc-11d3dnr-4 bSgUuU"></div>', '<div color="#5cc536" size="25" class="sc-11d3dnr-4 kexHTK"></div>', '<div color="#342c2c" size="25" class="sc-11d3dnr-4 cPVHxE"></div>', '<div class="sc-di5iv0-6 cPYNJK">']

def handle_cookies(driver):
    d.cprint(f"\tdef HandleCookies(driver):\nDeleting unwanted cookies")
 
    # Save the desired cookie before clearing all cookies
    desired_cookie = None
    for cookie in driver.get_cookies():
        if cookie['value'] == COOKIE_VALUE:
            desired_cookie = cookie
            break

    # Clear all cookies
    driver.delete_all_cookies()

    # Add back the desired cookie if found
    if desired_cookie:
        driver.add_cookie(desired_cookie)

# This is a recursive function that handles the overlay. The first appearance in the website.
def wait_for_overlay(driver, wait):
    try:
        overlay = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'preloaderLogo')))
    except:
        d.cprint("Overlay timed out, error handling: cookies")
        handle_cookies(driver)
        time.sleep(1)
        wait_for_overlay(driver, wait)

def place_bet(driver, round_info):
    data_instance = d()
    bet_color = data_instance.algorithm_execution(round_info)


    return bet_color
def scrape_live_bets():

    chrome_options = Options()
    chrome_options.executable_path = 'webdriver/chromedriver' 
    try:
        # Initialize Chrome WebDriver
        driver = webdriver.Chrome(options=chrome_options)

        # BEGIN 
        driver.get(URL)
        driver.add_cookie({'name': COOKIE_NAME, 'value': COOKIE_VALUE})
        wait = WebDriverWait(driver, 5)  # Maximum wait time of 5 seconds

        # OVERLAY 
        wait_for_overlay(driver, wait)

        # BUTTON
        play_now_button = wait.until(EC.element_to_be_clickable((By.XPATH, HTML[0])))
        play_now_button.click()  # Click the "Play Now!" button
        time.sleep(1)  # Wait for the page to load (you can adjust the delay as needed)

        # POPUP
        element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, HTML[1]))).click()
        
        # SIGN IN
        input("****** IMPORTANT ******\nSign in to the website then press ENTER to proceed!")
        print(driver.page_source)
        d.cprint("Success! Starting data mining and bot!")
        
        # LIVE DATA
        iteration, win_count, loss_count = 0, 0, 0
        while True:
            page_source = driver.page_source # Update page source in this line

            red_total_bet, green_total_bet, black_total_bet, has_bet, bet_color = 0, 0, 0, False, None
            while 'Rolling' not in page_source: 
                page_source = driver.page_source
                continue

            d.cprint('.... Starting new game ....')
            while "Rolling" in page_source:
                page_source = driver.page_source # Update page source in this line

                total_players_html = HTML[2]
                indices_total_players = [i for i in range(len(page_source)) if page_source.startswith(total_players_html, i)]
                for i, n in enumerate(indices_total_players):
                    if i == 0:
                        red_total_bet = float(page_source[n + 31: n + 35])
                    elif i == 1:
                        green_total_bet = float(page_source[n + 31: n + 35])
                    elif i == 2:
                        black_total_bet = float(page_source[n + 31: n + 35]) 

                # Place the bet in the last second
                if not has_bet:
                    try:
                        rolling_in_statement = page_source[page_source.find('Rolling'):page_source.find('Rolling') + 15]
                        time_left_rolling = float(rolling_in_statement[-4:-1]) 
                        if time_left_rolling <= 0.4:
                            bet_color = place_bet(driver, [None, red_total_bet, green_total_bet, black_total_bet, None])
                            has_bet = True
                    except:
                        continue
                time.sleep(0.1)

            if red_total_bet == green_total_bet == black_total_bet: 
                print("No one joined the game, not counting this one")
                continue # If no one bets, then all the bets are the same, so repeat the algorithm

            print("The final bets are", red_total_bet, green_total_bet, black_total_bet)
            while 'Rolling' not in page_source: 
                page_source = driver.page_source
                continue
            recent_scores = [i for i in range(len(page_source)) if page_source.startswith(HTML[6], i)]
            color_red, color_black, color_green = 'ff3d2f', '342c2c', '5cc536'
            latest_score = page_source[recent_scores[-1] + 55: recent_scores[-1] + 61]

            winner = None
            if latest_score == color_red:
                winner = 'RED'
                d.cprint("Red won!")
            elif latest_score == color_black:
                winner = 'BLACK'
                d.cprint("Black won!")
            elif latest_score == color_green:
                winner = 'GREEN'
                d.cprint("Green won!")
            
            if winner == bet_color:
                win_count += 1
            else:
                loss_count += 1
            d.cprint(f'Win count: {win_count}\nLoss count: {loss_count}')

            output = ''
            if iteration == 0:
                output += f'count,red,green,black,winner\n'
            output += f'{iteration},{red_total_bet},{green_total_bet},{black_total_bet},{winner}\n'

            d.output_stream(output)
            iteration += 1
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_live_bets()
