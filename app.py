import streamlit as st
import json
import pandas as pd
from random import randrange
import base64

st.set_option('deprecation.showfileUploaderEncoding', False)

"""
# Speed Updating

This app is used to pair people together for speed updating. It should be used
with this [Guided Track survey](https://www.guidedtrack.com/programs/14467/edit).

"""

st.sidebar.markdown("""
## Survey Instructions

Copy this [Guided Track survey](https://www.guidedtrack.com/programs/14467/edit).
* Click on the link above
* (You will need to setup a Guided Track account if you don't have one.)
* Click 'Copy' to copy the survey
* Click on 'Publish' at the top
* Share the link with the participants
* Wait for everyone to fill in the survey
* Click on 'Data' at the top
* Click 'Download data'
* Upload this csv file to this app 
""")

def get_data():
    file_buffer = st.file_uploader("Upload file", type=['csv'])

    show_file = st.empty()
    if not file_buffer:
        show_file.info("Please upload a file of type: " + ", ".join(["csv"]))
        return

    if file_buffer is not None:
        dataframe = pd.read_csv(file_buffer)
        return dataframe


def get_questions(dataframe):
    """

    :param dataframe: pandas dataframe of survey results
    :return: List[String] of question texts
    """
    return json.loads(dataframe["questions"][0])


def get_people(dataframe):
    """

    :param dataframe: pandas dataframe of survey results
    :return: List[List[String, int...]]
    """
    ppl = []
    for i in range(len(dataframe)):
        answers = json.loads(dataframe["answers"][i])
        ppl.append([dataframe["name"][i]] + answers)
    return ppl


# Returns squared difference in answer values for question q_index and persons p1 and p2
def chat_score(chat):
    p1, p2, q_index = chat
    p1_ans = p1[q_index]
    p2_ans = p2[q_index]
    if (p1_ans == -100) or (p2_ans == -100):
        return -100  # large negative for questions people don't want to talk about
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
        if arrangement_score(current) < arrangement_score(new):  # find better arrangement
            change = arrangement_score(new) - arrangement_score(current)
            print('     ' + str(arrangement_score(current)))
            current = new
            print('     +', change)
    return current


def arrange(people, num_iterations=100):
    i = 0
    overall_best_score = 0
    overall_best_arrangement = []
    while i < num_iterations:

        output = local_search(people, steps=50)
        output_score = arrangement_score(output)
        print(str(i) + ': final overall score: ' + str(output_score))

        if output_score > overall_best_score:
            overall_best_score = output_score
            overall_best_arrangement = output

        i = i + 1

    return overall_best_arrangement


def arrangement2df(arrangement):
    data = []

    for pair in arrangement:
        data.append([pair[0][0], pair[1][0], q_text[pair[2]]])

    return pd.DataFrame(data, columns=["Person 1", "Person 2", "Question"])


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="updateing_pairs.csv">Download csv file</a>'


# ======== Main ========

df = get_data()

if df is not None:
    q_text = get_questions(df)
    people = get_people(df)

    st.write(f"{len(q_text)} questions")
    st.write(f"{len(people)} people")

    show_qs = st.checkbox('Show questions', value=False)
    if show_qs:
        st.write(q_text)

    arrangement = arrange(people, num_iterations=100)

    st.write(f"Final score: {arrangement_score(arrangement)}")

    pairs_df = arrangement2df(arrangement)

    pairs_df = pairs_df.sort_values(by="Person 1")
    pairs_df = pairs_df.reset_index(drop=True)


    pairs_df.to_pickle("example.pkl")

    st.table(pairs_df)

    st.markdown(get_table_download_link(pairs_df), unsafe_allow_html=True)
else:
    eg_df = pd.read_pickle("example.pkl")

    st.markdown("## Example output")
    st.table(eg_df)

    st.markdown(get_table_download_link(eg_df), unsafe_allow_html=True)


"""
This app was created by [JJ](https://jhepburn.io/)

Based on work from [Julia Galef](https://juliagalef.com/) with help from Nick Anyos and James Fodor.
"""
