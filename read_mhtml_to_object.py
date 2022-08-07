from turtle import heading
from bs4 import BeautifulSoup
import tagging_core as analyzer
import prettyprinter as pp
import quopri
import re
import json
import dataclasses
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog

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

root = tk.Tk()
root.withdraw()
folder_selected = filedialog.askdirectory(title='Select folder that contains mhtml files')

file_path_list = list()
for root, dirs, files in os.walk(folder_selected):
    for file in files:
        if file.endswith(".mhtml"):
             file_path_list.append(os.path.join(root, file))

for file_path in file_path_list:
    print("Processing " + file_path)
    json_out_path = os.path.splitext(file_path)[0]+'.json'

    if os.path.exists(json_out_path):
        print(os.path.basename(json_out_path) + " is exist. Skipped.")
        continue

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
            print("Article Object: " + article_object.id + " (" + str(count) + "/" + str(len(article_nodes)) + ")")

        count = 0
        for a in article_list:
            count += 1
            analyzer.analyze(a)
            print("Analyzing " + a.id + " (" + str(count) + "/" + str(len(article_nodes)) + ")")
            # clean up
            a.text = ""
            a.text_tagged = list()

        # Serializing json 
        json_articles = json.dumps(article_list, indent = 4, cls=EnhancedJSONEncoder)
        with open(json_out_path, "w") as outfile:
            outfile.write(json_articles)
            print("Dumped:  " + json_out_path)





