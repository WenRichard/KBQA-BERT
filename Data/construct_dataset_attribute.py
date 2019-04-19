# coding:utf-8
import sys
import os
import random
import pandas as pd


'''
构造属性关联训练集，分类问题，训练BERT分类模型
1 
'''
# [training, testing]
data_type = "training"
file = "nlpcc-iccpol-2016.kbqa."+data_type+"-data"
target = "./NER_Data/q_t_a_df_"+data_type+".csv"

attribute_classify_sample = []

# count the number of attribute
testing_df = pd.read_csv(target, encoding='utf-8')
testing_df['attribute'] = testing_df['t_str'].apply(lambda x: x.split('|||')[1].strip())
attribute_list = testing_df['attribute'].tolist()
print(len(set(attribute_list)))
print(testing_df.head())


# construct sample
for row in testing_df.index:
    question, pos_att = testing_df.loc[row][['q_str', 'attribute']]
    question = question.strip()
    pos_att = pos_att.strip()
    # random.shuffle(attribute_list)    the complex is big
    # neg_att_list = attribute_list[0:5]
    neg_att_list = random.sample(attribute_list, 5)
    attribute_classify_sample.append([question, pos_att, '1'])
    neg_att_sample = [[question, neg_att, '0'] for neg_att in neg_att_list if neg_att != pos_att]
    attribute_classify_sample.extend(neg_att_sample)

seq_result = [str(lineno) + '\t' + '\t'.join(line) for (lineno, line) in enumerate(attribute_classify_sample)]

if data_type == 'testing':
    with open("./Sim_Data/"+data_type+".txt", "w", encoding='utf-8') as f:
        f.write("\n".join(seq_result))
else:
    val_seq_result = seq_result[0:12000]
    with open("./Sim_Data/"+"val"+".txt", "w", encoding='utf-8') as f:
        f.write("\n".join(val_seq_result))

    training_seq_result = seq_result[12000:]
    with open("./Sim_Data/"+data_type+".txt", "w", encoding='utf-8') as f:
        f.write("\n".join(training_seq_result))
