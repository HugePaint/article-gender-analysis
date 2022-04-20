from pickle import FALSE
import re
import nltk
import tkinter as tk
from tkinter import filedialog
import numpy
import gender_guesser.detector as gender


from itertools import tee, islice, chain

def read_articles_from_gui():
    root = tk.Tk()
    root.withdraw()

    content_list = list()
    file_path = filedialog.askopenfilenames(title='Select Articles', filetypes=[
        ("Text Files", ".txt")
    ])
    for entry in file_path:
        with open(entry, 'r', encoding='UTF-8') as file_opened:
            text = file_opened.read()
            content_list.append(text)

    return content_list

def create_name_dict(content_list):
    # key: name; value: list([gender, count])
    name_dict = dict()
    for text in content_list:
        for person in get_human_names(text):
            name_dict[person] = ["unknown", 0]
    
    return name_dict

def read_article(path):
    a_file = open("sample.txt", "r")
    text = a_file.read()
    a_file.close()
    return text

def parse_article(str):
    list_of_words = re.findall(r'\w+', str)
    return list_of_words

def article_analysis(list_of_lists, name_dict):
    name_count = 0
    male_count = 0
    female_count = 0
    andy_count = 0

    d = gender.Detector()
    skip = 0
    copy_for_next = list(list_of_lists)
    copy_for_next.append([None])
    for pair, next in zip(list_of_lists, copy_for_next):
        if skip == 1:
            skip = 0
            continue

        name = pair[0]
        tag = pair[1]

        if tag != "NNP": continue
        # skip the name "The" in Korea
        if name == "The": continue
        if len(name) <= 1: continue

        for p in name_dict.keys():
            if name in p:
                print("Name " + name + " is found in person list as " + p)
                result = d.get_gender(name)
                value = name_dict[p]
                value[0] = result
                value[1] = value[1] + 1
                name_dict[p] = value

                if result == "male" or result == "mostly_male":
                    name_count += 1
                    male_count += 1
                    print(name + " is found to be male.")
                elif result == "female" or result == "mostly_female":
                    name_count += 1
                    female_count += 1
                    print(name + " is found to be female.")
                elif result == "andy":
                    name_count += 1
                    andy_count += 1
                    print(name + " is found to be androgynous.")
                if (next[1] == "NNP"):
                    skip = 1
                    
    print("There are " + str(name_count) + " names identified in the article.")
    print("There are " + str(male_count) + " male names in total.")
    print("There are " + str(female_count) + " female names in total.")
    print("There are " + str(andy_count) + " androgynous names in total.")
    return (name_count, male_count, female_count, andy_count)

def get_human_names(text):
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    person_list = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 0: #avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            #check duplicates
            if not any(name in p for p in person_list):
                for p in person_list:
                    if p in name:
                        person_list.remove(p)
                        person_list.append(name[:-1])
                        break
                else:
                    person_list.append(name[:-1])
            name = ''
        person = []

    return (person_list)

full_content_list = read_articles_from_gui()
name_dict = create_name_dict(full_content_list)
for article in full_content_list:
    list_of_words = parse_article(article)
    tagged_words = nltk.pos_tag(list_of_words)
    result_list = article_analysis(tagged_words, name_dict)

print("\nCount:")
for name, count in name_dict.items():
    print("%20s: %20s" % (name, count))

# path = "sample.txt"
# text = read_article(path)
# list_of_words = parse_article(text)
# tagged_words = nltk.pos_tag(list_of_words)
# person_list = get_human_names(text)
# # print(tagged_words)
# print(get_human_names(text))
# name_dict = article_analysis(tagged_words, person_list)





