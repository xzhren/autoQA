## 数据描述

1、tests.json 测试

用户每次提交作业都会产生一次测试，tests中的每一条记录表示一次测试，字段如下

"id" : 测试id,
"compileErrStack" : 编译错误信息，如果没有编译错误，则为空,
"question" : 每个lesson会有多道题目，question为题目的名称,
"tester" : 作业的提交者,
"lesson" : lesson的名称,
"createdTime" : 提交作业的时间,
"course" : course的名称,
"status" : 测试结果

2、test-codes 测试代码

每次测试对应的代码，test-codes文件夹下的每一个文件夹对应一次测试，文件名为测试的id

3、test-results.json 测试结果

测试结果的信息，每次测试会对应多个测试用例，test-results中每一条记录对应一个测试用例的结果，字段如下：

"id" : 测试结果id,
"result" : 测试的结果,
"duration" : 测试花费的时间,
"testId" : 对应的测试id,
"title" : 测试用例的名称,
"errStack" : 测试的堆栈信息,
"errMessage" : 给学生显示的提示信息

4、lesson-questions.json 课程答疑

lesson-questions为针对课程的答疑信息，表示了某个学生在某个lesson下的聊天记录。

"id" : 课程答疑id,
"owner" : 学生的用户名,
"creator" : 记录的创建者，如果创建者与owner一致，表示是学生的提问，如果不一致，表示是老师的回答,
"course" : course的名称,
"lesson" : lesson的名称,
"createdTime" : 记录的创建时间,
"content" : 记录的内容

5、reivews.json 代码答疑

review记录了学生针对代码的答疑信息，学生可以针对提交作业的某一行提出问题，老师可以在任意一行给出作业批阅提示

"id" : 代码答疑id,
"owner" : 学生用户名,
"creator" : 记录的创建者，如果创建者与owner一致，表示是学生的提问，如果不一致，表示是老师的回答,
"course" : course的名称,
"lesson" : lesson的名称,
"createdTime" : 记录的创建时间,
"path" : 代码文件的路径,
"lineNum" : 代码行数,
"content" : 答疑的内容,
"commitId" : git里的commitid, 暂时没什么用，忽略它

## 自动问答的初步思路

1、以测试结果为核心，将数据进行关联：

- 测试结果--答疑
- 测试结果--review
- 测试结果--测试--对应的代码

细节：

- 找到某个lesson-questions/review创建时间前后的两个测试，对比其测试结果：
  - 如果某个测试用例由不通过变成通过，表示该答疑与该测试结果相关联，且该答疑帮助学生通过了某个测试用例
  - 如果某个测试用例由通过变成不通过，表示该答疑与该测试结果相关联，这种情况可能是改了一处代码，还需要修改其他代码

2、给老师的回答进行评分

评价标准：

- 老师回答后，用户通过几次提交才通过，提交次数越少，评分越高

3、对回答进行筛选以及合并

- 将一些没有意义的回答去掉，例如谢谢之类的
- 课程答疑与代码答疑需要综合一起考虑，例如答疑区提出的问题，老师有时候会直接回答看代码答疑
- 老师经常会回答类似的问题，我们根据针对的问题和回答的相似度，对多个回答合并成一个问题的答案


