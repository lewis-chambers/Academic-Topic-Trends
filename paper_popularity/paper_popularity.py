from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from matplotlib import pyplot as plt
from datetime import datetime
import os


def get_page(driver, url):
    driver.get(url)


def show_more(dates_div):
    button = dates_div.find_elements(By.TAG_NAME, 'button')
    if button:
        button[0].click()
        return True
    else:
        return False


def check_for_results(driver):
    page_id = None

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, 'filters'))
        )

        if "+ results" in driver.find_element(By.CLASS_NAME, 'search-body-results-text').get_attribute('innerHTML'):
            page_id = 103
        else:
            page_id = 100

    except TimeoutException:
        if "No results found" in driver.page_source:
            page_id = 101
        else:
            page_id = 600
    finally:
        return page_id


def pull_results(driver):
    years_div = None
    years_found = False
    for element in driver.find_elements(By.TAG_NAME, 'fieldset'):
        if "Years" in element.text:
            years_found = True
            years_div = element

    if years_found:
        dates_div = years_div.find_element(By.TAG_NAME, 'ol')
        has_overflow = show_more(dates_div)
        dates_list = dates_div.find_elements(By.TAG_NAME, 'li')

        dates = []
        for i, date in enumerate(dates_list):
            if has_overflow and i == len(dates_list) - 2:
                break
            date_string = date.text.replace('(', '').replace(')', '').replace(',', '').split(' ')
            dates.append([int(x) for x in date_string])

        minimum = min([x[0] for x in dates])
        return dates, minimum
    else:
        return False, False


def make_search(driver, search_terms):
    output = []
    end_date = datetime.now().year
    start_date = 0
    last = None
    while True:
        url = 'https://www.sciencedirect.com/search?qs={}&date={:04d}-{:04d}'.format(
            search_terms, start_date, end_date
        )
        get_page(driver, url)

        page_id = check_for_results(driver)

        if page_id == 100:

            data_found, smallest = pull_results(driver)
            data_found = [x for x in data_found if start_date <= x[0] <= end_date]
            output = output + data_found
            print('Getting dates for: {:04d}-{:04d}'.format(start_date, end_date))

            if last == 103:
                end_date = start_date - 1
            else:
                end_date = smallest - 1
            start_date = 0

        elif page_id == 103:
            start_date = end_date - 1
        else:
            return output, page_id

        last = page_id


def plot_data(years, values, search_term):
    plt.figure()
    plt.ion()
    plt.show()
    plt.fill_between(years, values)

    plt.title('Popularity of: "{}"'.format(search_term))
    plt.xlabel('Year Published')
    plt.ylabel('Publications')

    plt.draw()
    plt.pause(0.001)


def initialise_logs():
    if not os.path.isdir('Log'):
        os.mkdir('Log')


def add_log(driver):
    new_log = datetime.now().strftime('%Y,%d,%m %H;%M;%S')
    new_dir = os.path.join('Log', new_log)
    html_file = os.path.join(new_dir, 'source_code.html')

    if not os.path.isdir(new_dir):
        os.mkdir(new_dir)
        with open(html_file, 'w') as fh:
            fh.write(driver.page_source)


def main():
    initialise_logs()

    service = Service(executable_path=ChromeDriverManager().install())
    opts = webdriver.ChromeOptions()
    opts.add_argument('--headless')

    with webdriver.Chrome(service=service, options=opts) as driver:
        # Hiding 'Headless' from user-agent
        user_agent = driver.execute_script("return navigator.userAgent;")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent.replace('Headless', '')})

        while True:
            search = str(input('[Hit enter to exit]\nSearch for: '))
            if len(search) == 0:
                exit()

            res, end_page = make_search(driver, search)

            if end_page == 600:
                print("Mystery error occured, html added to '{}'".format(os.path.abspath('Logs')))
                add_log(driver)
            else:
                if len(res) > 0:
                    years = [x[0] for x in res]
                    values = [x[1] for x in res]

                    plot_data(years, values, search)

                    while True:
                        print("[Hit enter to exit]")
                        question = str(input("change y scale ['linear, log']: ")).lower()
                        if len(question) == 0:
                            break
                        if question in ['linear', 'log']:
                            plt.yscale(question)
                            plt.draw()
                            plt.pause(0.001)
                        else:
                            print('Keyword "{}" invalid, must be "linear" or "log"'.format(question))
                else:
                    print("No results!")


if __name__ == '__main__':
    main()

