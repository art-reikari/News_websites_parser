from bs4 import BeautifulSoup
import requests
import datetime
import time
import parser


def collect_page(session, soup, news_dict, date, cont):
    page_container = soup.find('div', class_='container category-container anchor')
    news_urls = []
    try:
        primary_news = page_container.find('div', class_='post-card__primary-story post-card__alternate-story')
        primary_news_post_date = datetime.datetime.strptime(primary_news.find('time')['datetime'].split('T')[0],
                                                            '%Y-%m-%d').date()
        if primary_news_post_date == datetime.datetime.today().date():
            pass
        elif primary_news_post_date != date:
            return news_dict, None, False
        else:
            news_urls.append(primary_news.find('h3').find('a')['href'])
    except AttributeError:
        pass
    for piece in page_container.findAll('div', class_='post-card__more-secondary-story'):
        post_date = datetime.datetime.strptime(piece.find('time')['datetime'].split('T')[0], '%Y-%m-%d').date()
        if post_date == datetime.datetime.today().date():
            continue
        elif post_date != date:
            cont = False
        else:
            news_urls.append(piece.find('h3').find('a')['href'])
    for news_url in news_urls:
        time.sleep(5)
        news_resp = session.get(news_url)
        news_soup = BeautifulSoup(news_resp.text, 'html.parser')
        news_title = news_soup.find('h1', class_='post-single__title').text.strip()
        print(news_title)
        news_body = news_soup.find('div', class_='post-single__content entry-content').findAll('p')
        news_body = ' '.join([piece.text.strip() for piece in news_body])
        score = parser.count_keywords(news_body)
        news_dict[news_title] = (news_body, score)
    time.sleep(5)
    next_page_url = soup.find('div', class_='pagination').find('a')['href']
    next_page_resp = session.get(next_page_url)
    next_page_soup = BeautifulSoup(next_page_resp.text, 'html.parser')
    return news_dict, next_page_soup, cont


def collect_section(session, url, news_dict, date):
    page_resp = session.get(url)
    page_soup = BeautifulSoup(page_resp.text, 'html.parser')
    section_title = page_soup.find('div', class_='masthead-banner__header-content--title').text.strip()
    print(f'Gathering section {section_title}')
    cont = True
    page_num = 1
    while cont:
        print(f'Page {page_num}')
        news_dict, page_soup, cont = collect_page(session, page_soup, news_dict, date, cont)
        page_num += 1
    return news_dict


def collect_rappler_news(outer_news):
    sections_urls = ['https://www.rappler.com/nation/', 'https://www.rappler.com/world/asia-pacific/',
                     'https://www.rappler.com/business/']
    key_date = (datetime.datetime.today() - datetime.timedelta(1)).date()
    local_news = {}
    with requests.session() as session:
        for section_url in sections_urls:
            local_news = collect_section(session, section_url, local_news, key_date)
        local_news = parser.find_relevant_news(local_news, 5)
        output_news = outer_news | local_news
        return output_news


# if __name__ == '__main__':
#     parsed_news = {}
#     parsed_news = collect_rappler_news(parsed_news)
#     with open('rappler.txt', 'w', encoding='utf-8') as afile:
#         for title, body in parsed_news.items():
#             afile.write(f'{title}\n')
#             afile.write(f'{body}\n\n\n')
