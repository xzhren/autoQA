# encoding=utf-8

import pandas as pd
import numpy as np
import importlib
import AnswerUtils
from collections import Counter
from sklearn import preprocessing
import re

from AnswerUtils import CodeQA

codeQA = CodeQA()
code_keys = codeQA.get_keys()

for i in range(len(code_keys)):
    print(i, 100*i/len(code_keys), "%")

    sample_key = codeQA.get_key_by_index(i)
    test_info_pd = codeQA.get_testinfo_by_testid(sample_key)

    # Assert
    # compileErrStack_list = test_info_pd.drop_duplicates(['compileErrStack'])[['compileErrStack']].values
    # assert compileErrStack_list[0][0] != compileErrStack_list[0][0]
    assert len(Counter(test_info_pd.compileErrStack)) == 1
    assert len(Counter(test_info_pd.duration)) == 1
    owner_id = list(test_info_pd.columns).index("owner")
    tester_id = list(test_info_pd.columns).index("tester")
    tmp = test_info_pd.apply(lambda line: line[owner_id] == line[tester_id], axis=1).drop_duplicates()
    assert (len(tmp) == 1) and (tmp[0] == True)

    # Simple errorStack
    pattern = re.compile("\\tat com.tianmaying.*\(.*\)\\n")
    def get_most_value_info(row):
        searchobj = pattern.search(str(row))
        if searchobj:
            return searchobj.group().strip()
        else:
            return ''
    test_info_pd['errorStackSimple'] = test_info_pd.errStack.apply(get_most_value_info)

    # Label Encoder
    lbl = preprocessing.LabelEncoder()
    test_info_pd['titleid'] = lbl.fit_transform(test_info_pd.title)
    test_info_pd['resultid'] = lbl.fit_transform(test_info_pd.result)
    # test_info_pd['statusid'] = lbl.fit_transform(test_info_pd.status)
    test_info_pd['errorStackID'] = lbl.fit_transform(test_info_pd.errorStackSimple)

    # Status_str Encoder
    title_set = set(test_info_pd.titleid)
    status_str_list = []
    for test_id in test_info_pd.testId:
        status_str = ''
        for title_id in title_set:
            tmp = test_info_pd[(test_info_pd.testId == test_id) & (test_info_pd.titleid == title_id)].resultid.values[0]
            status_str += str(tmp)
        status_str_list.append(status_str)
    assert len(status_str_list) == len(test_info_pd)
    test_info_pd['status_str'] = status_str_list

    # errorStack_str Encoder
    title_set = set(test_info_pd.titleid)
    errorStack_str_list = []
    for test_id in test_info_pd.testId:
        errorStack_str = ''
        for title_id in title_set:
            tmp = test_info_pd[(test_info_pd.testId == test_id) & (test_info_pd.titleid == title_id)].errorStackID.values[0]
            assert tmp < 100
            if tmp < 10: errorStack_str += '0' + str(tmp) + '-'
            else: errorStack_str += str(tmp) + '-'
        errorStack_str_list.append(errorStack_str)
    assert len(errorStack_str_list) == len(test_info_pd)
    test_info_pd['errorStack_str'] = errorStack_str_list

    # get Q&A
    test_reviews_pd = codeQA.get_reviews_by_key(sample_key)
    answer_df = codeQA.get_answers_by_reviews(test_reviews_pd)
    question_df = codeQA.get_questions_by_reviews(test_reviews_pd)
    more_status_pd = test_info_pd[['testId', 'errorStack_str', 'status_str']].drop_duplicates()
    prefix = sample_key['course'].values[0]+"+"+sample_key['lesson'].values[0]+"+"+sample_key['question'].values[0]

    questino_status_pd = question_df.merge(more_status_pd, on=['testId'])[['testId','status_str', 'errorStack_str','content']]
    questino_status_pd = questino_status_pd.sort_values(['status_str'])
    questino_status_pd.to_csv("./output/"+prefix+"+question.csv", index=False, encoding="utf-8")

    answer_status_pd = answer_df.merge(more_status_pd, on=['testId'])[['testId','status_str', 'errorStack_str','content']]
    answer_status_pd = answer_status_pd.sort_values(['status_str'])
    answer_status_pd.to_csv("./output/"+prefix+"+answer.csv", index=False, encoding="utf-8")
