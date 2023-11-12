import re
import itertools

import cna
import straits_times
import vietnam_express
import the_star
import rappler


def count_keywords(text):
    keywords = [r'Chin\w*', r'Japan\w*', r'Korea\w*', r'Malaysia\w*', r'Singapor\w*', r'Vietnam\w*', 'Brunei',
                r'Lao\w*', r'Cambodia\w*', 'Myanmar', 'Philippines', 'Filipino', r'Indonesia\w*', r'[E,e]conom\w*',
                '[T,t]rade', '[I,i]nternational', r'[C,c]urrenc\w*', '[E,e]xchange', r'[E,e]xport\w*', r'[I,i]mport\w*',
                r'[I,i]nterest\w*', '[I,i]nflation', r'[D,d]evaluat\w*', '[C,c]risis', '[C,c]rises', r'[B,b]ank\w*',
                r'[N,n]egotiat\w*', r'[H,h]ub\w*', r'[G,g]lobal\w*', r'[M,m]anufactur\w*', r'[M,m]arket\w*',
                r'[L,l]abor\w*', r'[C,c]ompan\w*', '[P,p]roduction', r'[F,f]irm\w*', r'[E,e]nterpris\w*',
                r'[F,f]actor\w*', r'[F,f]inanc\w*']
    score = 0
    for keyword in keywords:
        score += len(re.findall(keyword, text))

    return score


def find_relevant_news(news_dict, news_count):
    news_dict = dict(sorted(news_dict.items(), key=lambda item: item[1][1], reverse=True))
    news_dict = dict(itertools.islice(news_dict.items(), news_count))
    return news_dict


def save_news(news_texts):
    with open('news.txt', 'w', encoding="utf-8") as afile:
        for news_title, news_body in news_texts.items():
            afile.write(f'{news_title.strip()}')
            afile.write(f'\n{news_body[0]}\n\n\n')


if __name__ == '__main__':
    news = {}
    print('Collecting Vietnam Express\n')
    news = vietnam_express.collect_vietnam_express_news(news)
    print('\nVietnam Express is successfully collected\n')
    print('Collecting The Star\n')
    news = the_star.collect_the_star_news(news)
    print('\nThe Star is successfully collected\n')
    print('Collecting Rappler\n')
    news = rappler.collect_rappler_news(news)
    print('\nRappler is successfully collected\n')
    print('Collecting The Straits Times\n')
    news = straits_times.collect_straits_times_news(news)
    print('\nThe Straits Times is successfully collected\n')
    print('Collecting CNA\n')
    news = cna.collect_cna_news(news)
    print('\nCNA is successfully collected\n')
    save_news(news)
    print('All news are successfully saved to news.txt')
