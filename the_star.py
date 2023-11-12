from bs4 import BeautifulSoup
import requests
import time
import parser
import re


def gather_news_from_page(session, page_url, news_dict):
    page_resp = session.get(page_url)
    page_soup = BeautifulSoup(page_resp.text, 'html.parser')
    news_tags = page_soup.find('ul', class_='timeline').findAll('h2', class_='f18')
    for news_tag in news_tags:
        time.sleep(5)
        news_url = news_tag.find('a')['href']
        news_resp = session.get(news_url)
        news_soup = BeautifulSoup(news_resp.text, 'html.parser')
        news_title = news_soup.find('div', class_='headline story-pg').find('h1').text.strip()
        print(news_title)
        news_body = ' '.join([piece.text for piece in news_soup.find('div', id='story-body').findAll('p')]).strip()
        keywords_score = parser.count_keywords(news_body)
        news_dict[news_title] = (news_body, keywords_score)
    pager = page_soup.find('ul', class_='pager')
    next_page_number = int(pager.find('li', class_='pager-nav active').find('a').text) + 1
    next_page_url = pager.find('a', string=re.compile(fr'\s*{next_page_number}\s*'))['href']
    return news_dict, next_page_url


def gather_sections(session, section_url, news_dict):
    print(f'Gather section {re.search("tag.*", section_url).group().split("=")[1]}')
    for _ in range(1, 5)[:1]:
        print(f'Gather page {_}')
        news_dict, section_url = gather_news_from_page(session, section_url, news_dict)
    return news_dict


def collect_the_star_news(outer_news):
    urls = ['https://www.thestar.com.my/news/latest?tag=Business',
            'https://www.thestar.com.my/news/latest?tag=Aseanplus',
            'https://www.thestar.com.my/news/latest?tag=Tech',
            'https://www.thestar.com.my/news/latest?tag=Nation']
    local_news = {}
    with requests.session() as sess:
        for url in urls[:1]:
            local_news = gather_sections(sess, url, local_news)
    local_news = parser.find_relevant_news(local_news, 10)
    output_news = outer_news | local_news
    return output_news


# if __name__ == '__main__':
#     cleared_news = {}
#     cleared_news = collect_the_star_news(cleared_news)
#     with open('star_news.txt', 'w', encoding='utf-8') as afile:
#         for title, body in cleared_news.items():
#             afile.write(f'{title}\n')
#             afile.write(f'{body}\n\n\n')
