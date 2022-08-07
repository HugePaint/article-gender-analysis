import re
import gender_guesser.detector as gender

def parse_article(path):
    a_file = open("sample.txt", "r")
    data = a_file.read()
    a_file.close()
    list_of_words = re.findall(r'\w+', data)
    return list_of_words

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


path = "sample.txt"
list_of_words = parse_article(path)
# print(list_of_words)
article_analysis(list_of_words)
