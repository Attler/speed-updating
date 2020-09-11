import csv
import math
from random import randrange, shuffle
import copy

input_file = 'Speed Updating Questions.csv'


# Reads input of .csv file of list of persons and their answers to the form questions
# def read_form(input):
#     with open(input, encoding="utf8") as csvfile:
#         people = []
#         reader = csv.reader(csvfile)
#         for row in reader:
#             people.append(row)
#         q_text = people[1][1:]
#         people = people[1:]
#         for index, person in enumerate(people):
#             people[index] = person[1:]
#         return people


# Returns squared difference in answer values for question q_index and persons p1 and p2
def chat_score(chat):
    p1, p2, q_index = chat
    p1_ans = p1[q_index]
    p2_ans = p2[q_index]
    if (p1_ans == None) or (p2_ans == None):
        return (-100)  # large negative for questions people don't want to talk about
    return (abs(p1_ans - p2_ans)) ** 2


# Returns overall match score of full arrangment of persons
def arrangement_score(arrangement):
    return sum(map(chat_score, arrangement))


def init_arrangement(people):
    n_people = len(people)
    n_ques = len(people[0]) - 2
    arrangement = []
    # shuffle(people)
    for i in range(0, n_people, 2):  # assuming even number of people
        p1 = people[i]
        p2 = people[i + 1]
        q_index = randrange(n_ques) + 1  # random question index
        chat = (p1, p2, q_index)
        # print('pair:',people[i][0],'&',people[i+1][0])
        if len(chat) == 3:
            arrangement.append(chat)
    return arrangement


def random_step(arrangement):
    trial_arrangement = arrangement.copy()  # create new list so original isn't modified
    n1 = randrange(len(trial_arrangement))  # swap random pair
    n2 = randrange(len(trial_arrangement))
    s1 = trial_arrangement[n1][0]
    s2 = trial_arrangement[n2][0]
    trial_arrangement[n1] = (s2, trial_arrangement[n1][1], trial_arrangement[n1][2])
    trial_arrangement[n2] = (s1, trial_arrangement[n2][1], trial_arrangement[n2][2])
    # print('\nRandomstep')
    # for pair in arrangement:
    #    print('pair:',pair[0][0],'&',pair[1][0])
    # print('score',arrangement_score(arrangement))
    return trial_arrangement


def local_search(people, steps):
    init_arr = init_arrangement(people)
    current = init_arr
    for i in range(steps):
        new = random_step(current)
        if (arrangement_score(current) < arrangement_score(new)):  # find better arrangement
            change = arrangement_score(new) - arrangement_score(current)
            print('     ' + str(arrangement_score(current)))
            current = new
            print('     +', change)
    return current


##---------------------------------------------##

answer_translation = {'Strongly Agree': 3,
                      'Agree': 2,
                      'Somewhat Agree': 1,
                      'Unsure': 0,
                      'Somewhat Disagree': -1,
                      'Disagree': -2,
                      'Strongly Disagree': -3,
                      '': None,
                      'I don\'t want to talk about this question': None}

##---------------------------------------------##
i = 0
num_iterations = 100
overall_best_score = 0
overall_best_arrangement = []
while i < num_iterations:

    # load data from csv
    with open(input_file, encoding="utf8") as csvfile:
        people = []
        reader = csv.reader(csvfile)
        for row in reader:
            people.append(row)
        q_text = people[0][1:]

        people = people[1:]
        for index, person in enumerate(people):
            people[index] = person[1:]

    print(people[0])

    # store data in numerical form
    for person in people:
        for index, answer in enumerate(person):
            if index == 0:  # ignore first column
                continue
            person[index] = answer_translation[answer]  # get answer value

    print(people[0])

    output = local_search(people, steps=50)
    output_score = arrangement_score(output)
    print(str(i) + ': final overall score: ' + str(output_score))

    # for pair in output:
    #    question_index = pair[2]
    #    print('pair:',pair[0][0],'&',pair[1][0])
    #    print('question:',q_text[question_index])
    #    print(pair[0][question_index])
    #    print(pair[1][question_index])

    if (output_score > overall_best_score):
        overall_best_score = output_score
        overall_best_arrangement = output

    i = i + 1

print('Finished!')
print('best score:', overall_best_score)
for pair in overall_best_arrangement:
    question_index = pair[2]
    print('pair:', pair[0][0], '&', pair[1][0])
    print('question:', q_text[question_index])
    print(pair[0][question_index], 'vs', pair[1][question_index])



