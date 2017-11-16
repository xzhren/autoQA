# encoding=utf-8

import numpy as np
import pandas as pd
import time
import datetime
import re
from tqdm import tqdm

class LessonQA:
    
    def __init__(self):
        self.lesson_qa_df = self._load_data()
        self.lessonQA_keys = self._get_keys()
        
    def _load_data(self):
        lesson_qa_df = pd.read_csv("./data/lesson_question_df.csv")
        lesson_qa_df['isQues'] = lesson_qa_df.apply(lambda line: line[1] == line[2], axis=1)
        return lesson_qa_df

    def _get_keys(self):
        lessonQA_keys = self.lesson_qa_df[['course','lesson','owner']].drop_duplicates()
        return lessonQA_keys

    def get_keys(self):
        return self.lessonQA_keys

    def get_key_by_index(self, index):
        return self.lessonQA_keys.iloc[index:index+1]

    def get_key_by_range(self, min, max):
        return self.lessonQA_keys.iloc[min:max+1]

    def get_lessson_by_key(self, lessonQA_key_pd):
        lesson_dialogue_pd = pd.merge(self.lesson_qa_df, lessonQA_key_pd, how="inner")
        return lesson_dialogue_pd.sort_values(by=['createdTime'], ascending=True)

    def pprint_lesson_QA(self, lesson_dialogue_pd):
        str_QA = ''
        
        for line in lesson_dialogue_pd.values:
            str_QA += datetime.datetime.fromtimestamp(
                int(line[-3]//1000)
            ).strftime('%Y-%m-%d %H:%M:%S')
            
            if line[-1]: str_QA += ' Q：'
            else: str_QA += ' A：'
                
            str_QA += line[1]
            str_QA += ' '
            str_QA += line[-2]
            str_QA += '\n'
            
        return str_QA


class CodeQA:
    
    def __init__(self):
        self.reivews_df, self.tests_result_df, self.tests_df = self._load_data()
        self.codeQA_keys = self._get_keys()
        self.testid_commitid_dict = self._get_testid_commitid_dict()
        self.reivews_df['testId'] = self.reivews_df.apply(lambda line: self.testid_commitid_dict[line[1]], axis=1)
        self.reivews_df['isQues'] = self.reivews_df.apply(lambda line: line[2] == line[3], axis=1)
        self.reivews_df = self.reivews_df.sort_values(by=['createdTime'], ascending=True)
        
    def _load_data(self):
        reivews_df = pd.read_csv("./data/reivews_df.csv")
        tests_result_df = pd.read_csv("./data/tests_result_df.csv")
        tests_df = pd.read_csv("./data/tests_df.csv")
        tests_df['owner'] = tests_df['tester']
        return reivews_df, tests_result_df, tests_df

    def _get_keys(self):
        codeQA_keys = self.tests_df[['course','lesson','question','owner']].drop_duplicates()
        return codeQA_keys

    def _get_testid_commitid_dict(self):
        testid_min_time_series = self.tests_df[['id','createdTime','owner']].groupby(['id']).min()
        commitid_min_time_series = self.reivews_df[['commitId','createdTime','owner']].groupby(['commitId']).min()
        merge_series = testid_min_time_series.append(commitid_min_time_series).sort_values(by=['createdTime'], ascending=True)
        merge_series_groups_dict = merge_series.groupby(['owner']).groups

        testid_commitid_dict = {}
        errlist = []
        for owner in tqdm(merge_series_groups_dict.keys()):
            index = merge_series_groups_dict[owner]
            owner_df = merge_series.loc[index]
            
            pattern = re.compile("[a-z0-9]{40}")
            last_items = ''
            for i, (index, value) in enumerate(owner_df.iterrows()):
                if pattern.match(index):
                    if last_is_test:
                        testid_commitid_dict[index] = last_items[1]
                    else:
                        testid_commitid_dict[index] = testid_commitid_dict[last_items[1]]
                        errlist.append(last_items)
                        errlist.append((i, index, value['createdTime'], value['owner']))
                        # print(last_items)
                        # print(i, index, value['createdTime'], value['owner'])
                        # time.sleep(1)
                        
                    last_is_test = False
                else:
                    last_is_test = True
                last_items = i,index,value['createdTime'], value['owner']
        # print(errlist)
        [print(item) for item in errlist]
        return testid_commitid_dict

    def get_keys(self):
        return self.codeQA_keys

    def get_key_by_index(self, index):
        return self.codeQA_keys.iloc[index:index+1]

    def get_key_by_range(self, min, max):
        return self.codeQA_keys.iloc[min:max+1]

    def get_test_info_by_key(self, codeQA_key):
        test_info_pd = pd.merge(self.tests_df, codeQA_key, how="inner")
        return test_info_pd

    def get_test_info_by_testid(self, codeQA_key):
        test_info_pd = pd.merge(self.tests_df, codeQA_key, left_on='id', right_on='testId', how="inner")
        return test_info_pd

    def get_test_result_by_testid(self, test_info_pd):
        test_result_pd = pd.merge(self.tests_result_df, test_info_pd[['id']], left_on='testId', right_on='id', how="inner")
        return test_result_pd

    def get_reviews_by_key(self, codeQA_key):
        test_info_pd = pd.merge(self.tests_df, codeQA_key, how="inner")
        test_reviews_pd = pd.merge(self.reivews_df, test_info_pd[['id']], left_on='testId', right_on='id', how="inner")
        commitid_testid_pd = test_reviews_pd[['commitId','testId']].drop_duplicates()
        commitid_testid_pd['id'] = commitid_testid_pd['testId']
        return test_reviews_pd, commitid_testid_pd

    def pprint_code_QA(self, test_reviews_pd):
        str_QA = ''
        now_commit_id = ''
        for line in test_reviews_pd.values:
            if line[1] != now_commit_id:
                str_QA += '\n' + line[1] + '\n'
                now_commit_id = line[1] 
            str_QA += datetime.datetime.fromtimestamp(
                int(line[-5]//1000)
            ).strftime('%Y-%m-%d %H:%M:%S')
            
            if line[-2]: str_QA += ' Q：'
            else: str_QA += ' A：'
                
            str_QA += line[2]
            str_QA += ' '
            str_QA += line[-4]
            str_QA += '\n'
            
        return str_QA

