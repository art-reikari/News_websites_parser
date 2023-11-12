from bs4 import BeautifulSoup
import requests
import datetime
import time
import re
import parser


def gather_section_urls(session, url):
    main_menu_urls = {}
    irrelevant_sections = ['News', 'Travel', 'Life', 'Sports', 'Perspectives']
    homepage_resp = session.get(url)
    homepage_resp_text = homepage_resp.text
    hompage_soup = BeautifulSoup(homepage_resp_text, 'html.parser')
    main_menu = hompage_soup.find('nav', id='main_menu_web')
    menu_items = main_menu.findAll('div', class_='item_menu_left')
    for menu_item in menu_items[1:]:
        item_name = menu_item.find('a')['data-medium'].split('-')[1]
        if item_name in irrelevant_sections:
            continue
        sub_sections_urls = {}
        subsections = menu_item.find('ul').findAll('li')
        for sub_section in subsections:
            sub_section_name = sub_section.find('a')['data-medium'].split('-')[1]
            sub_section_url = sub_section.find('a')['href']
            sub_sections_urls[sub_section_name] = url + sub_section_url
        main_menu_urls[item_name] = sub_sections_urls
        if len(subsections) == 0:
            item_url = menu_item.find('a')['href']
            main_menu_urls[item_name] = url + item_url
    return main_menu_urls


def collect_news_from_sections(session, date, section_urls):
    news_dict = {}
    for section in section_urls:
        print(f'Collect section {section}.')
        subsections = section_urls[section]
        try:
            for subsection in subsections:
                subsection_url = subsections[subsection]
                news_dict = collect_subsection_news(session, subsection, subsection_url, news_dict, date)
        except TypeError:
            subsection_url = subsections
            news_dict = collect_subsection_news(session, section, subsection_url, news_dict, date)

        print(f'Section {section} is successfully collected')
    return news_dict


def collect_subsection_news(session, subsection, subsection_url, news_dict, date):
    print(f'Collect subsection {subsection}.')
    subsection_resp = session.get(subsection_url)
    subsection_soup = BeautifulSoup(subsection_resp.text, 'html.parser')

    news = subsection_soup.findAll('div', class_='item_news')
    filtered_news_urls = []

    for piece in news:
        post_date = piece.find('div', class_='timer_post')
        post_date = datetime.datetime.strptime(post_date.text.split('|')[0].strip(), '%B %d, %Y').date()
        if post_date == date:
            filtered_news_urls.append(piece.find(class_='lead_news_site').find('a')['href'])

    for url in filtered_news_urls:
        news_resp = requests.get(url)
        news_soup = BeautifulSoup(news_resp.text, 'html.parser')
        try:
            news_title = news_soup.find('h1', class_='title_post').text
            try:
                news_lead_row = news_soup.find('span', class_='lead_post_detail row').text
            except AttributeError:
                news_lead_row = news_soup.find('div', class_='lead_news_photo_detail').text
            news_body = ' '.join([piece.text for piece in news_soup.findAll('p', class_='Normal')])
            news_text = f'{news_lead_row} {news_body}'
        except AttributeError:
            news_title = url.split('/')[-1].split('.')[0]
            news_title = ' '.join(re.findall(r'\w*', news_title)).split()
            news_text =\
                ' '.join([piece.text for piece in news_soup.find('div', id='medium_editor').findAll('p')]).split()
        keywords_score = parser.count_keywords(news_text)
        news_dict[news_title] = (news_text, keywords_score)
    print(f'Subsection {subsection} is successfully collected.')
    time.sleep(5)
    return news_dict


def collect_vietnam_express_news(outer_news):
    with requests.Session() as sess:
        today = datetime.datetime.today().date()
        homepage_url = 'https://e.vnexpress.net/'
        sections_urls = gather_section_urls(sess, homepage_url)
        local_news = collect_news_from_sections(sess, today, sections_urls)
        local_news = parser.find_relevant_news(local_news, 5)
        output_news = outer_news | local_news
    return output_news


# if __name__ == '__main__':
#     cleared_news = collect_vietnam_express_news()
#     with open('news_vietnam_express.txt', 'w', encoding='utf-8') as afile:
#         for title in cleared_news.keys():
#             text = cleared_news[title][0]
#             afile.write(f'{title}\n')
#             afile.write(f'{text}\n\n\n')
