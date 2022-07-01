from bs4 import BeautifulSoup
from tagging_demo import Article
import quopri

file_path = r"data\Australia_Corp_2003.mhtml"
with open(file_path, 'r') as fp:
    new_soup = BeautifulSoup(quopri.decodestring(fp.read()), 'lxml')
    article_set = new_soup.find_all("div", class_="article")

    for a in article_set:
        article_object = Article(list(), list(), dict())
        article_object.id = a['id']

        heading_node = a.find("b", string="HD").parent.next_sibling.string

        word_count_str = a.find("b", string="WC").parent.next_sibling.string
        article_object.word_count = [int(s) for s in word_count_str.split() if s.isdigit()][0]

        print(article_object)


    print(article_set)

