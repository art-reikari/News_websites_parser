from bs4 import BeautifulSoup
import requests
import datetime
import time
import parser


def collect_page(session, news_dict, soup, date):
    # print(len(soup.findAll('div', class_='view-content row')))
    news_container = soup.findAll('div', class_='view-content row')[1]
    news_cards = news_container.findAll('div', class_='card-body')
    news_urls = []
    for news_card in news_cards:
        post_timestamp = news_card.find('div', class_='card-time').find('time')['data-created-timestamp']
        post_date = datetime.datetime.fromtimestamp(int(post_timestamp)).date()
        if post_date == date:
            news_urls.append(fr"https://www.straitstimes.com/{news_card.find('a')['href']}")
        else:
            break
    last_news_timestamp = news_cards[-1].find('div', class_='card-time').find('time')['data-created-timestamp']
    last_news_post_date = datetime.datetime.fromtimestamp(int(last_news_timestamp)).date()

    for news_url in news_urls:
        time.sleep(5)
        news_resp = session.get(news_url)
        news_soup = BeautifulSoup(news_resp.text, 'html.parser')
        news_title = news_soup.find('h1', class_='headline node-title').text.strip()
        print(news_title)
        news_body = ' '.join([piece.text.strip() for piece in news_soup.findAll('p')])
        score = parser.count_keywords(news_body)
        news_dict[news_title] = (news_body, score)
    if last_news_post_date == date:
        time.sleep(5)
        next_page_url = r'https://www.straitstimes.com' + soup.find('a', class_='page-link')['href']
        # print(next_page_url)
        next_page_resp = session.get(next_page_url)
        next_page_soup = BeautifulSoup(next_page_resp.text, 'html.parser')
        return news_dict, next_page_soup
    else:
        return news_dict, None


def collect_section(session, news_dict, url, date):
    session.headers = {'accept-encoding': 'gzip'}
    # print(url)
    section_resp = session.get(url)
    page_soup = BeautifulSoup(section_resp.text, 'html.parser')
    section_title = page_soup.find('div',
                                   class_='col-sm-6 col-md-8 col-lg-8 articles-latest-term-by-url '
                                   'block block-st-layouts block-block-latest-by-term-from-url').find('h2').text.strip()
    print(f'Gathering section {section_title}')
    page = 1
    try:
        while True:
            print(f'Gathering page {page}')
            news, page_soup = collect_page(session, news_dict, page_soup, date)
            page += 1
    except AttributeError:
        print('No more news from today')
    return news_dict


def collect_straits_times_news(outer_news):
    urls = ['https://www.straitstimes.com/asia/se-asia', 'https://www.straitstimes.com/asia/east-asia',
            'https://www.straitstimes.com/business/economy', 'https://www.straitstimes.com/business/invest',
            'https://www.straitstimes.com/business/banking', 'https://www.straitstimes.com/business/companies-markets',
            'https://www.straitstimes.com/business/property']
    today = datetime.datetime.today().date()
    local_news = {}
    with requests.session() as session:
        for url in urls:
            local_news = collect_section(session, local_news, url, today)
    local_news = parser.find_relevant_news(local_news, 5)
    output_news = outer_news | local_news
    return output_news


if __name__ == '__main__':
    parsed_news = {}
    parsed_news = collect_straits_times_news(parsed_news)
    with open('the_straits_times.txt', 'w', encoding='utf-8') as afile:
        for title, body in parsed_news.items():
            afile.write(f'{title}\n')
            afile.write(f'{body}\n\n\n')
