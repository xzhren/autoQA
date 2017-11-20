# encoding=utf-8

import numpy as np
import pandas as pd
import time
import datetime
import re
from tqdm import tqdm
import difflib

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

    def get_QAs(self, lesson_dialogue_pd):
        pattern = re.compile("(?<=<blockquote>)[\s\S]*(?=</blockquote>)")
        father_id_list = []
        content_list = []
        qa_diaglog = []
        data_list = lesson_dialogue_pd.values
        for index, line in enumerate(data_list):
            content = line[-2]
            isQues = line[-1]
            id = line[0]
            searchobj = pattern.search(content)
            father_id = -1
            last_content = ''
            if searchobj:
                quotetr = searchobj.group()
                quotetr = quotetr.replace('<p></p>', '')
                for last in range(index-1,-1,-1):
                    last_item = data_list[last]
                    last_content = last_item[-2]
                    last_isQues = last_item[-1]
                    last_id = last_item[0]
                    seq = difflib.SequenceMatcher(None, quotetr, last_content)
                    ratio = seq.ratio()
                    if ratio > 0.8:
                        father_id = last_id
                        break
                quotetr = '<blockquote>' + quotetr + '</blockquote>'
                content = content.replace(quotetr, '')
            
            if not isQues:
                qa_item = []
                qa_item.append(father_id)
                qa_item.append(id)
                qa_item.append(last_content)
                qa_item.append(content)
                qa_diaglog.append(qa_item)
        return qa_diaglog



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

    def get_QAs(self, test_reviews_pd):
        test_reviews = test_reviews_pd.values
        now_commit_id = ''
        last_is_ques = True
        qa_list = []
        for index, line in enumerate(test_reviews):
            commit_id = line[1]
            isQus = line[-2]
            id = line[0]
            content = line[-4]
            if commit_id != now_commit_id:
                now_commit_id = commit_id
            else:
                if (not isQus) and last_is_ques:
                    qa_temp = []
                    qa_temp.append(last_id)
                    qa_temp.append(id)
                    qa_temp.append(last_content)
                    qa_temp.append(content)
                    qa_list.append(qa_temp)
            last_is_ques = isQus
            last_id = id
            last_content = content
        return qa_list
