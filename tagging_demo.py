from pickle import FALSE
import re
import nltk
import tkinter as tk
from tkinter import filedialog
import numpy
import gender_guesser.detector as gender

from itertools import tee, islice, chain

from dataclasses import dataclass, field

# Ref: http://nealcaren.github.io/text-as-data/html/times_gender.html
# Two lists  of words that are used when a man or woman is present, based on Danielle Sucher's https://github.com/DanielleSucher/Jailbreak-the-Patriarchy
male_words=set(['guy','spokesman','chairman',"men's",'men','him',"he's",'his','boy','boyfriend','boyfriends','boys','brother','brothers','dad','dads','dude','father','fathers','fiance','gentleman','gentlemen','god','grandfather','grandpa','grandson','groom','he','himself','husband','husbands','king','male','man','mr','nephew','nephews','priest','prince','son','sons','uncle','uncles','waiter','widower','widowers'])
female_words=set(['heroine','spokeswoman','chairwoman',"women's",'actress','women', 'her','aunt','aunts','bride','daughter','daughters','female','fiancee','girl','girlfriend','girlfriends','girls','goddess','granddaughter','grandma','grandmother','herself','ladies','lady','lady','mom','moms','mother','mothers','mrs','ms','niece','nieces','priestess','princess','queens','she','sister','sisters','waitress','widow','widows','wife','wives','woman'])

@dataclass
class Article:
    text_tagged: list
    segmented_gender_word_count: list
    full_name_dictionary: dict

    id: str = ""
    title: str = ""
    author: str = ""
    country: str = ""
    year: str = ""
    category: str = ""
    text: str = ""
    word_count: int = 0
    male_person: int = 0
    female_person: int = 0
    most_mentioned_male: str = ""
    most_mentioned_female: str = ""

# for name lists of all articles, extract most mentioned male/female

def read_articles_from_gui():
    root = tk.Tk()
    root.withdraw()

    article_list = list()
    # file_path = filedialog.askopenfilenames(title='Select Articles', filetypes=[
    #     ("Text Files", ".txt")
    # ])
    file_path = list(["data/sample2.txt"])
    for entry in file_path:
        with open(entry, 'r', encoding='UTF-8') as file_opened:
            article = Article(list(), list(), dict())
            # TODO: parse more info here
            article.text = file_opened.read()
            article_list.append(article)

    return article_list

def read_article(path):
    a_file = open("data/sample3.txt", "r")
    text = a_file.read()
    a_file.close()
    return text

def tag_article(article):
    list_of_words = re.findall(r'\w+', article.text)
    article.text_tagged = nltk.pos_tag(list_of_words)
    return

def split_and_count(article, how_many_segments):
    list_of_tagged_words = article.text_tagged
    where_to_split = 1 + (len(list_of_tagged_words) // how_many_segments)
    split_point = list()
    split_point.append(0)
    for i in range(1, how_many_segments):
        split_point.append(i * where_to_split)
    split_point.append(len(list_of_tagged_words))
    print(split_point)

    # check the last word of 1/3. if NNP, check first word in then next 1/3
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

    count = list()
    for i in range(0, len(split_point) - 1):
        print("\nCount for %2d/3" % i)
        count.append(count_gender_words(list_of_tagged_words[split_point[i] : split_point[i+1]], article.full_name_dictionary))
        print("male : %3d, female : %3d" % (count[i][0], count[i][1]))
    article.segmented_gender_word_count = count

    article.word_count = len(list_of_tagged_words)

    max_male_count = 0
    for name, gender_and_count in article.full_name_dictionary.items():
        if (gender_and_count[0] == "male"):
            article.male_person += 1
        if (gender_and_count[0] == "male") and (gender_and_count[1] > max_male_count):
            max_male_count = gender_and_count[1]
    article.most_mentioned_male = [name for name, gender_and_count in article.full_name_dictionary.items() 
                                    if (gender_and_count[0] == "male") and (gender_and_count[1] == max_male_count)]

    max_female_count = 0
    for name, gender_and_count in article.full_name_dictionary.items():
        if (gender_and_count[0] == "female"):
            article.female_person += 1
        if (gender_and_count[0] == "female") and (gender_and_count[1] > max_female_count):
            max_female_count = gender_and_count[1]
    article.most_mentioned_female = [name for name, gender_and_count in article.full_name_dictionary.items() 
                                    if (gender_and_count[0] == "female") and (gender_and_count[1] == max_female_count)]
    return

def count_gender_words(list_of_tagged_words, name_dict):
    print(list_of_tagged_words)

    male_word_count = 0
    female_word_count = 0
    last_full_name = None
    last_title = None

    for pair in list_of_tagged_words:
        # TODO: double count for Richard Jefferson (sample3.txt)        
        word = pair[0]
        tag = pair[1]
        word_gender = 'unknown'

        if (last_full_name != None) and (word in last_full_name.split()):
            continue
        else:
            last_full_name = None

        # if title, consider the gender mentioned
        if word in set(["Mr", "Ms", "Mrs", "Lady", "Madam", "Miss", "Sir"]):
            # TODO: increase the counter
            last_title = word
            if word in set(["Mr", "Sir"]):
                male_word_count += 1
                print(word + " is found to be a male title.")
            if word in set(["Ms", "Mrs", "Lady", "Madam", "Miss"]):
                female_word_count += 1
                print(word + " is found to be a female title.")
            continue

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
                name_dict[p][1] = name_dict[p][1] + 1
                if last_title != None:
                    print(last_title + " " + word + " is found as " + p + ", now count for " + str(name_dict[p][1]))
                    last_title = "skipped"
                    break
                word_gender = name_dict[p][0]
                print("Name " + word + " is found as " + p + ", and it is " + word_gender + ", now count for " + str(name_dict[p][1]))
        
        if last_title == "skipped":
            last_title = None
            continue
        last_title = None        

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


def find_full_names(article):
    # TODO: keep both entry of Smith as male and female

    # TODO: track title in the list

    text = article.text

    # if we have title before name, use an underscore to tag between title and name
    # replace "Mr. name" with "Mr_name"
    # abbreviated titles like "Mr." "Mrs." "Ms." are not picked up by ne_chunk. Underscore helps
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


    # if non of these above, enter loop with gender-guesser
    male_title = set(["Sir", "Mr"])
    female_title = set(["Lady", "Madam", "Miss", "Ms", "Mrs"])

    print(person_list)
    name_dict = dict()
    for person in person_list:
        # check full name if it starts with "(title)_", "Madam_", "Miss_", "Mr_", then assign to gender
        # check if there is underscore, which means a title is in the full name
        end_index = person.find("_")
        if end_index == -1:
            # no underscore, use gender-guessor to check gender
            name_dict[person] = [check_gender_for_full_name(person), 0]
            continue    # go to next iteration

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
        
        # if title is not picked up correctly, use gender-guesser
        if name_dict[person][0] == "TBD":
            name_dict[person][0] = check_gender_for_full_name(person)
        

    article.full_name_dictionary = name_dict

    return

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

def analyze(article):
    find_full_names(article)
    tag_article(article)
    split_and_count(article, 3)

    # clean up
    # article.text = ""
    # article.text_tagged = list()

if __name__ == '__main__':
    parsed_article_list = read_articles_from_gui()
    for article in parsed_article_list:
        print("\nStart processing a new article")
        find_full_names(article)
        tag_article(article)
        split_and_count(article, 3)
        print("\nCount:")
        for name, count in article.full_name_dictionary.items():
            print("%20s: %20s" % (name, count))

        # clean up
        article.text = ""
        article.text_tagged = list()

        print(article)





