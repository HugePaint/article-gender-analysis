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
female_words=set(['heroine','spokeswoman','chairwoman',"women's",'actress','women', 'her','aunt','aunts','bride','daughter','daughters','female','fiancee','girl','girlfriend','girlfriends','girls','goddess','granddaughter','grandma','grandmother','herself','ladies','lady','lady','mom','moms','mother','mothers','mrs','ms','niece','nieces','priestess','princess','queens','she','sister','sisters','waitress','widow','widows','wife','wives','woman'])


def read_articles_from_gui():
    root = tk.Tk()
    root.withdraw()

    content_list = list()
    # file_path = filedialog.askopenfilenames(title='Select Articles', filetypes=[
    #     ("Text Files", ".txt")
    # ])
    file_path = list(["sample3.txt"])
    for entry in file_path:
        with open(entry, 'r', encoding='UTF-8') as file_opened:
            text = file_opened.read()
            content_list.append(text)

    return content_list

def read_article(path):
    a_file = open("sample2.txt", "r")
    text = a_file.read()
    a_file.close()
    return text

def parse_article(str):
    list_of_words = re.findall(r'\w+', str)
    return list_of_words

def article_analysis(list_of_tagged_words, name_dict, how_many_segments):
    where_to_split = 1 + (len(list_of_tagged_words) // how_many_segments)
    split_point = list()
    split_point.append(0)
    for i in range(1, how_many_segments):
        split_point.append(i * where_to_split)
    split_point.append(len(list_of_tagged_words))
    print(split_point)

    # TODO: check the last word of 1/3. if NNP, check first word in then next 1/3
    # if the 1/3 starts with NNP, send that word to prior 1/3, and check again.
    for i in range(1, len(split_point) - 1):
        current_split = split_point[i] - 1
        last_pair_in_this_seg = list_of_tagged_words[current_split]
        tag = last_pair_in_this_seg[1]
        if tag == "NNP":
            first_pair_in_next_seg = list_of_tagged_words[current_split]
            while (first_pair_in_next_seg[1] == "NNP"):
                current_split += 1
                first_pair_in_next_seg = list_of_tagged_words[current_split]
            split_point[i] = current_split

    print(split_point)
    
    # TODO: No. of male person, No. of female person
    # most mentioned male full name, most mentioned female full name
    # No. words in the text

    count = list()
    for i in range(0, len(split_point) - 1):
        print("\nCount for %2d/3" % i)
        count.append(count_gender_words(list_of_tagged_words[split_point[i] : split_point[i+1]], name_dict))
        print("male : %3d, female : %3d" % (count[i][0], count[i][1]))

    return count

def count_gender_words(list_of_tagged_words, name_dict):
    print(list_of_tagged_words)

    male_word_count = 0
    female_word_count = 0
    last_full_name = None

    for pair in list_of_tagged_words:        
        word = pair[0]
        tag = pair[1]
        word_gender = 'unknown'

        # if title, consider the gender mentioned
        if word in set(["Mr", "Ms", "Mrs", "Lady", "Madam", "Miss", "Sir"]):
            # TODO: increase the counter
            continue

        # TODO: double count for Richard Jefferson
        if (last_full_name != None) and (word in last_full_name.split()):
            continue
        else:
            last_full_name = None

        # check if current word is in name list
        for p in name_dict.keys():
            # not NNP, not a name
            if tag != 'NNP':
                continue
            
            # Mary Jones-Smith, John Jones, Peter Smith
            # create list(["Mary", "Jones-Smith"]) use space as separator
            # do exact match of word to list element
            if word in p.split():
                last_full_name = p
                word_gender = name_dict[p][0]
                name_dict[p][1] = name_dict[p][1] + 1
                print("Name " + word + " is found as " + p + ", and it is " + word_gender + ", now count for " + str(name_dict[p][1]))

        # then check with regular gender dictionary
        word = pair[0].lower()
        if word in male_words:
            word_gender = "male"
            print(word + " is found to be male.")
        if word in female_words:
            word_gender = "female"
            print(word + " is found to be female.")

        # count increment
        if word_gender == "male":
            male_word_count += 1
        if word_gender == "female":
            female_word_count += 1
            
    
    return (male_word_count, female_word_count)


def get_human_names(text):
    # consider "Lady", "Madam", "Miss", "Sir" etc.
    # assign the gender here if we have pronoun
    # only abbreviations like "Mr." "Mrs." "Ms." have problem 

    original_text = text

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
            name = name[:-1]
            # TODO: check duplicates
            if not any(name in p for p in person_list):
                for p in person_list:
                    if p in name:
                        person_list.remove(p)
                        person_list.append(name)
                        break
                else:
                    person_list.append(name)
            name = ''
        person = []


    # check full name if it starts with "(title)_", "Madam_", "Miss_", "Mr_", then assign to gender
    # if non of these above, enter loop with gender-guesser
    male_title = set(["Sir", "Mr"])
    female_title = set(["Lady", "Madam", "Miss", "Ms", "Mrs"])


    print(person_list)
    name_dict = dict()
    for person in person_list:
        # check if there is underscore, which means a title is in the full name
        end_index = person.find("_")
        if end_index == -1:
            # no underscore, go check next name
            name_dict[person] = [check_gender_for_full_name(person), 0]
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

        person = person[end_index+1:]
        name_dict[person] = ["TBD", 0]
        if title in male_title:
            name_dict[person][0] = "male"
        if title in female_title:
            name_dict[person][0] = "female"
        # if non of these above, enter loop with gender-guesser
        if name_dict[person][0] == "TBD":
            name_dict[person][0] = check_gender_for_full_name(person)
        
    # remove titles
    # title_all = set(["Mr.", "Ms.", "Mrs.", "Lady", "Madam", "Miss", "Sir"])
    # for t in title_all:
    #     original_text = re.sub(t+" ", "", original_text)

    # run this by 1/3, count occurences of names 

    return (name_dict, original_text)

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
for article in full_content_list:
    print("\nStart processing a new article")
    name_dict_and_cleaned_article = get_human_names(article)
    name_dict = name_dict_and_cleaned_article[0]
    list_of_words = parse_article(name_dict_and_cleaned_article[1])
    tagged_words = nltk.pos_tag(list_of_words)
    result_list = article_analysis(tagged_words, name_dict, 3)
    print("\nCount:")
    for name, count in name_dict.items():
        print("%20s: %20s" % (name, count))





