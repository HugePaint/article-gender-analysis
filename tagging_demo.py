import re
import nltk
import numpy
import gender_guesser.detector as gender

def read_article(path):
    a_file = open("sample.txt", "r")
    text = a_file.read()
    a_file.close()
    return text

def parse_article(text):
    list_of_words = re.findall(r'\w+', text)
    return list_of_words

def tag_article(list_of_words):
    tagged_words = nltk.pos_tag(list_of_words)
    return tagged_words

def article_analysis(list_of_lists):
    name_count = 0
    male_count = 0
    female_count = 0
    andy_count = 0

    d = gender.Detector()
    for word in list_of_lists:
        # skip the name "The" in Korea
        if word == "The": continue

        result = d.get_gender(word)
        if result == "male" or result == "mostly_male":
            name_count += 1
            male_count += 1
            print(word + " is found to be male.")
        elif result == "female" or result == "mostly_female":
            name_count += 1
            female_count += 1
            print(word + " is found to be female.")
        elif result == "andy":
            name_count += 1
            andy_count += 1
            print(word + " is found to be androgynous.")

    print("There are " + str(name_count) + " names in the article.")
    print("There are " + str(male_count) + " male names in total.")
    print("There are " + str(female_count) + " female names in total.")
    print("There are " + str(andy_count) + " androgynous names in total.")
    return

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
        if len(person) > 1: #avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    return (person_list)

path = "sample.txt"
text = read_article(path)
list_of_words = parse_article(text)
tagged_words = tag_article(list_of_words)
print(tagged_words)
print(get_human_names(text))
# article_analysis(list_of_words)


