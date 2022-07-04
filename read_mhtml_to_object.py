from turtle import heading
from bs4 import BeautifulSoup
import tagging_demo as analyzer
import prettyprinter as pp
import quopri
import re
import json
import dataclasses

class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            if isinstance(o, np.integer):
                return int(o)
            if isinstance(o, np.floating):
                return float(o)
            if isinstance(o, np.ndarray):
                return o.tolist()
            return super().default(o)

# pp.install_extras()

file_path = r"data\Australia_Corp_2003.mhtml"
with open(file_path, 'r') as fp:
    new_soup = BeautifulSoup(quopri.decodestring(fp.read()), 'lxml')
    article_nodes = new_soup.find_all("div", class_="article", id=re.compile(r'article-[.]*'))

    count = 0
    article_list = list()
    for a in article_nodes:
        count += 1
        article_object = analyzer.Article(list(), list(), dict())
        article_object.id = a['id']

        heading_str = a.find("b", string="HD").parent.next_sibling.string
        article_object.title = heading_str

        word_count_str = a.find("b", string="WC").parent.next_sibling.string
        article_object.word_count = [int(s) for s in word_count_str.split() if s.isdigit()][0]

        publish_date_str = a.find("b", string="PD").parent.next_sibling.string
        article_object.year = publish_date_str[-4:]

        try:
            LP_node = a.find("b", string="LP").parent.parent.next_sibling
            for child in LP_node.children:
                article_object.text += child.text + " "
        except:
            print(article_object.id + ": No LP section")
        
        try:
            TD_node = a.find("b", string="TD").parent.parent.next_sibling
            for child in TD_node.children:
                article_object.text += child.text + " "
        except:
            print(article_object.id + ": No TD section")
        
        article_object.text = article_object.text.replace('\n', '')

        article_list.append(article_object)

        # pp.pprint(article_object, indent=1)
        print(article_object.id + "/t(" + str(count) + "/" + str(len(article_nodes)) + ")")

    for a in article_list:
        analyzer.analyze(a)
        print(a.id)
        # clean up
        a.text = ""
        a.text_tagged = list()

    # Serializing json 
    json_articles = json.dumps(article_list, indent = 4, cls=EnhancedJSONEncoder)
    with open("data\Australia_Corp_2003.json", "w") as outfile:
        outfile.write(json_articles)


    print(article_nodes)

