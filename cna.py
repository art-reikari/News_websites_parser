from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from bs4 import BeautifulSoup
import requests
import datetime
import re
import time
import parser


def gather_news_block(news_elements, news_dict, today):
    for element in news_elements:
        timestamp_html = \
            element.find_element(By.CLASS_NAME, 'list-object__datetime-duration').get_attribute('innerHTML')
        timestamp = re.search(r'\d+', timestamp_html).group()
        post_date = datetime.datetime.fromtimestamp(float(timestamp)).date()
        if post_date == today:
            heading = element.find_element(By.CLASS_NAME, 'list-object__heading-link').text
            if 'Video' in heading:
                continue
            print(f'Collecting news "{heading}"')
            link_to_news = element.find_element(By.CLASS_NAME, 'list-object__heading-link').get_attribute('href')
            news_resp = requests.get(link_to_news).text
            news_soup = BeautifulSoup(news_resp, 'html.parser')
            news_body = ' '.join([piece.text.strip() for piece in news_soup.findAll('p')])
            score = parser.count_keywords(news_body)
            news_dict[heading] = (news_body, score)
            time.sleep(5)
        else:
            return news_dict, 'No more news from today'
    return news_dict


def gather_primary_news(driver, news_dict, today):
    try:
        first_col = driver.find_element(By.CLASS_NAME,
                                        'top-stories-primary-section__items--col-one')
        first_col_news_elements = first_col.find_elements(By.CLASS_NAME, 'card-object__body')
        first_col_news_elements.extend(first_col.find_elements(By.CLASS_NAME, 'media-object__body'))
        second_col = driver.find_element(By.CLASS_NAME, 'top-stories-primary-section__items--col-two')
        second_col_news_elements = second_col.find_elements(By.CLASS_NAME, 'card-object__body')
    except NoSuchElementException:
        first_col = driver.find_element(By.CLASS_NAME,
                                        'd-middle-9s-3p-ads__items--col-one')
        first_col_news_elements = first_col.find_elements(By.CLASS_NAME, 'media-object__body')
        second_col = driver.find_element(By.CLASS_NAME, 'd-middle-9s-3p-ads__items--col-two')
        second_col_news_elements = second_col.find_elements(By.CLASS_NAME, 'media-object__body')
    for col in (first_col_news_elements, second_col_news_elements):
        try:
            news_dict = gather_news_block(col, news_dict, today)
            assert isinstance(news_dict, dict)
        except AssertionError:
            print(news_dict[1])
            news_dict = news_dict[0]
    return news_dict


def gather_more_news(driver, news_dict, today):
    more_block = driver.find_element(By.CLASS_NAME, 'infinte-dynamic-scroll')
    grid = more_block.find_element(By.CLASS_NAME, 'grid-cards-four-column')
    grid_news_pieces = grid.find_elements(By.CLASS_NAME, 'card-object__body')
    next_grid_num = 1
    while True:
        try:
            news_dict = gather_news_block(grid_news_pieces, news_dict, today)
            assert isinstance(news_dict, dict)
            try:
                driver.find_element(By.CLASS_NAME, 'button--view-more-stories').click()
            except ElementClickInterceptedException:
                element = driver.find_element(By.CLASS_NAME, 'button--view-more-stories')
                driver.execute_script("arguments[0].click();", element)
            grid = more_block.find_elements(By.CLASS_NAME, 'grid-cards-four-column')[next_grid_num]
            grid_news_pieces = grid.find_elements(By.CLASS_NAME, 'card-object__body')
            next_grid_num += 1
        except AssertionError:
            print(news_dict[1])
            news_dict = news_dict[0]
            break
    return news_dict


def collect_cna_news(outer_news):
    local_news = {}
    today = datetime.datetime.today().date()
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=chrome_options)
    for section in ('singapore', 'asia', 'business'):
        print(f'Connecting to section {section.capitalize()}')
        driver.get(fr'https://www.channelnewsasia.com/{section}')
        print(f'Successfully connected to section {section.capitalize()}')
        local_news = gather_primary_news(driver, local_news, today)
        local_news = gather_more_news(driver, local_news, today)
    local_news = parser.find_relevant_news(local_news, 5)
    output_news = outer_news | local_news

    return output_news


# if __name__ == '__main__':
#     news_dict = {}
#     news_dict = collect_cna_news(news_dict)
#     with open('test_cna.txt', 'w', encoding='utf-8') as afile:
#         for title, body in news_dict.items():
#             afile.write(f'{title}\n')
#             afile.write(f'{body}\n\n')
