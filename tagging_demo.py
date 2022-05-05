from pickle import FALSE
import re
import nltk
import tkinter as tk
from tkinter import filedialog
import numpy
import gender_guesser.detector as gender

from itertools import tee, islice, chain
# Ref: http://nealcaren.github.io/text-as-data/html/times_gender.html
# Two lists  of words that are used when a man or woman is present, based on Danielle Sucher's https://github.com/DanielleSucher/Jailbreak-the-Patriarchy
male_words=set(['guy','spokesman','chairman',"men's",'men','him',"he's",'his','boy','boyfriend','boyfriends','boys','brother','brothers','dad','dads','dude','father','fathers','fiance','gentleman','gentlemen','god','grandfather','grandpa','grandson','groom','he','himself','husband','husbands','king','male','man','mr','nephew','nephews','priest','prince','son','sons','uncle','uncles','waiter','widower','widowers'])
female_words=set(['heroine','spokeswoman','chairwoman',"women's",'actress','women',"she's",'her','aunt','aunts','bride','daughter','daughters','female','fiancee','girl','girlfriend','girlfriends','girls','goddess','granddaughter','grandma','grandmother','herself','ladies','lady','lady','mom','moms','mother','mothers','mrs','ms','niece','nieces','priestess','princess','queens','she','sister','sisters','waitress','widow','widows','wife','wives','woman'])
male_words_with_name = set(male_words)
female_words_with_name = set(female_words)


def read_articles_from_gui():
    root = tk.Tk()
    root.withdraw()

    content_list = list()
    # file_path = filedialog.askopenfilenames(title='Select Articles', filetypes=[
    #     ("Text Files", ".txt")
    # ])
    file_path = list(["sample2.txt"])
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

def clean_list_for_name_extraction(list_of_tagged_words):
    # deal with Mr as NNP, so a full name is expected as [firstname, lastname]
    cleaned_list = list(list_of_tagged_words)
    for pair in list_of_tagged_words:
        if pair[0].lower() in male_words:
            print(pair)
            cleaned_list.remove(pair)
        if pair[0].lower() in female_words:
            print(pair)
            cleaned_list.remove(pair)
    print(cleaned_list)
    return cleaned_list

def article_analysis(list_of_tagged_words, name_dict):
    name_count = 0
    male_count = 0
    female_count = 0
    andy_count = 0

    # check gender
    d = gender.Detector()
    skip = 0
    cleaned_list = clean_list_for_name_extraction(list_of_tagged_words)
    copy_for_next = list(cleaned_list)
    copy_for_next.append([None])

    # separate article here to 1/3, then count
    for pair, next in zip(cleaned_list, copy_for_next):
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
                    male_words_with_name.add(name.lower())
                    print(name + " is found to be male.")
                elif result == "female" or result == "mostly_female":
                    name_count += 1
                    female_count += 1
                    female_words_with_name.add(name.lower())
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

    print
    print(male_words_with_name)
    print(male_words_with_name)

    one_third_count = 1 + (len(list_of_tagged_words) // 3)
    one_third_result = list([[0, 0],
                             [0, 0],
                             [0, 0]])
    for i in range(0, one_third_count):
        pair = list_of_tagged_words[i]
        word = pair[0].lower()
        if word in male_words_with_name:
            print(word + " is count for male in 1/3.")
            one_third_result[0][0] = one_third_result[0][0] + 1
        if word in female_words_with_name:
            print(word + " is count for female in 1/3.")
            one_third_result[0][1] = one_third_result[0][1] + 1
    for i in range(one_third_count, 2 * one_third_count):
        pair = list_of_tagged_words[i]
        word = pair[0].lower()
        if word in male_words_with_name:
            print(word + " is count for male in 2/3.")
            one_third_result[1][0] = one_third_result[1][0] + 1
        if word in female_words_with_name:
            print(word + " is count for female in 2/3.")
            one_third_result[1][1] = one_third_result[1][1] + 1
    for i in range(2 * one_third_count, len(list_of_tagged_words)):
        pair = list_of_tagged_words[i]
        word = pair[0].lower()
        if word in male_words_with_name:
            print(word + " is count for male in 3/3.")
            one_third_result[2][0] = one_third_result[2][0] + 1
        if word in female_words_with_name:
            print(word + " is count for female in 3/3.")
            one_third_result[2][1] = one_third_result[2][1] + 1

    return one_third_result

def get_human_names(text):
    # TODO: consider "Lady", "Madam", "Miss", "Sir" etc.
    #       assign the gender here if we have pronoun
    #       only abbreviations like "Mr." "Mrs." "Ms." have problem 

    # replace "Mr. name" with "Mr_name" for chunker to pickup mr and mrs
    title_abbreviations = set(["Mr", "Ms", "Mrs"])
    for abbr in title_abbreviations:
        text = re.sub(str(abbr+".\s"), str(abbr+"_"), text)
    
    titles = set(["Lady", "Madam", "Miss", "Sir"])
    for t in titles:
        text = re.sub(str(t+"\s"), str(t+"_"), text)


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


    # check full name if it starts with "Lady", "Madam", "Miss", "Sir", then assign to gender
    # check if the first word is start with "Mr_" "Mrs_" "Ms_", then assign gender
    # if non of these above, enter loop with gender-guesser
    male_title = set(["Sir", "Mr"])
    female_title = set(["Lady", "Madam", "Miss", "Ms", "Mrs"])

    name_dict = dict()
    for person in person_list:
        # check if there is underscore, which means a title is in the full name
        end_index = person.find("_")
        if end_index == -1:
            # no underscore, go check next name
            name_dict[person] = [check_gender_for_full_name(person), 0]
            print(person)
            print(name_dict[person])
            continue

        start_index = person.find(" ")
        # if there is space in title, we only need the last word before underscore
        if start_index == -1 or start_index > end_index:
            start_index = 0
        
        # example: "Cat Madam_Elijah Wood", and "Cat Madam_" is extracted
        # in this case we only need Madam
        title = person[start_index : end_index]
        while title.find(" ") > -1:
            title = title[title.find(" ")+1:]
        
        print(title)

        person = person[end_index+1:]
        name_dict[person] = ["TBD", 0]
        if title in male_title:
            name_dict[person][0] = "male"
        if title in female_title:
            name_dict[person][0] = "female"
        # if non of these above, enter loop with gender-guesser
        if name_dict[person][0] == "TBD":
            name_dict[person][0] = check_gender_for_full_name(person)
        print(person)
        print(name_dict[person])
            
    # delete titles from the list
    # run this by 1/3, count occurences of names 

    return (person_list)

def check_gender_for_full_name(full_name):
    first_name = full_name
    if full_name.find(" ") > -1:
        first_name = full_name[ : full_name.find(" ")]
    result = gender.Detector().get_gender(first_name)
    
    if result == "male" or result == "mostly_male":
        return("male")
    elif result == "female" or result == "mostly_female":
        return("female")
    elif result == "andy":
        return("andy")
    else:
        return("unknown")

full_content_list = read_articles_from_gui()
name_dict = create_name_dict(full_content_list)
for article in full_content_list:
    list_of_words = parse_article(article)
    tagged_words = nltk.pos_tag(list_of_words)
    result_list = article_analysis(tagged_words, name_dict)
    print(result_list)

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





