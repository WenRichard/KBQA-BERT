# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 20:16
# @Author  : Alan
# @Email   : xiezhengwen2013@163.com
# @File    : triple_clean.py
# @Software: PyCharm


import pandas as pd


'''
构造NER训练集，实体序列标注，训练BERT+BiLSTM+CRF
'''

question_str = "<question"
triple_str = "<triple"
answer_str = "<answer"
start_str = "============="


triple_list = []
seq_q_list = []    #["中","华","人","民"]
seq_tag_list = []  #[0,0,1,1]
for data_type in ["training", "testing"]:
    file = "./NLPCC2016KBQA/nlpcc-iccpol-2016.kbqa." + data_type + "-data"
    with open(file, 'r',encoding='utf-8') as f:
        q_str = ""
        t_str = ""
        a_str = ""
        for line in f:
            if question_str in line:
                q_str = line.strip()
            if triple_str in line:
                t_str = line.strip()
            if start_str in line:  #new question answer triple
                entities = t_str.split("|||")[0].split(">")[1].strip()
                q_str = q_str.split(">")[1].replace(" ","").strip()
                if ''.join(entities.split(' ')) in q_str:
                    clean_triple = t_str.split(">")[1].replace('\t','').replace(" ","").strip().split("|||")
                    triple_list.append(clean_triple)
                else:
                    print(entities)
                    print(q_str)
                    print('------------------------')

df = pd.DataFrame(triple_list, columns=["entity", "attribute", "answer"])
print(df)
print(df.info())
df.to_csv("./DB_Data/clean_triple.csv", encoding='utf-8', index=False)