#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import re
import time
import jieba
import numpy as np
import pandas as pd
import urllib.request
import urllib.parse
import tensorflow as tf
from Data.load_dbdata import upload_data
from global_config import Logger

from run_similarity import BertSim
# 模块导入 https://blog.csdn.net/xiongchengluo1129/article/details/80453599

loginfo = Logger("recommend_articles.log", "info")
file = "./Data/NER_Data/q_t_a_testing_predict.txt"

bs = BertSim()
bs.set_mode(tf.estimator.ModeKeys.PREDICT)


def dataset_test():
    '''
    用训练问答对中的实体+属性，去知识库中进行问答测试准确率上限
    :return:
    '''
    with open(file) as f:
        total = 0
        recall = 0
        correct = 0

        for line in f:
            question, entity, attribute, answer, ner = line.split("\t")
            ner = ner.replace("#", "").replace("[UNK]", "%")
            # case1: entity and attribute Exact Match
            sql_e1_a1 = "select * from nlpccQA where entity='"+entity+"' and attribute='"+attribute+"' limit 10"
            result_e1_a1 = upload_data(sql_e1_a1)

            # case2: entity Fuzzy Match and attribute Exact Match
            sql_e0_a1 = "select * from nlpccQA where entity like '%" + entity + "%' and attribute='" + attribute + "' limit 10"
            #result_e0_a1 = upload_data(sql_e0_a1, True)

            # case3: entity Exact Match and attribute Fuzzy Match
            sql_e1_a0 = "select * from nlpccQA where entity like '" + entity + "' and attribute='%" + attribute + "%' limit 10"
            #result_e1_a0 = upload_data(sql_e1_a0)

            if len(result_e1_a1) > 0:
                recall += 1
                for l in result_e1_a1:
                    if l[2] == answer:
                        correct += 1
            else:
                result_e0_a1 = upload_data(sql_e0_a1)
                if len(result_e0_a1) > 0:
                    recall += 1
                    for l in result_e0_a1:
                        if l[2] == answer:
                            correct += 1
                else:
                    result_e1_a0 = upload_data(sql_e1_a0)
                    if len(result_e1_a0) > 0:
                        recall += 1
                        for l in result_e1_a0:
                            if l[2] == answer:
                                correct += 1
                    else:
                        loginfo.logger.info(sql_e1_a0)
            if total > 100:
                break
            total += 1
            time.sleep(1)
            loginfo.logger.info("total: {}, recall: {}, correct:{}, accuracy: {}%".format(total, recall, correct, correct * 100.0 / recall))
        #loginfo.logger.info("total: {}, recall: {}, correct:{}, accuracy: {}%".format(total, recall, correct, correct*100.0/recall))


def estimate_answer(candidate, answer):
    '''
    :param candidate:
    :param answer:
    :return:
    '''
    candidate = candidate.strip().lower()
    answer = answer.strip().lower()
    if candidate == answer:
        return True

    if not answer.isdigit() and candidate.isdigit():
        candidate_temp = "{:.5E}".format(int(candidate))
        if candidate_temp == answer:
            return True
        candidate_temp == "{:.4E}".format(int(candidate))
        if candidate_temp == answer:
            return True

    return False


def kb_fuzzy_classify_test():
    '''
    进行问答测试：
    1、 实体检索:输入问题，ner得出实体集合，在数据库中检索与输入实体相关的所有三元组
    2、 属性映射——bert分类/文本相似度
        + 非语义匹配：如果所得三元组的关系(attribute)属性是 输入问题 字符串的子集，将所得三元组的答案(answer)属性与正确答案匹配，correct +1
        + 语义匹配：利用bert计算输入问题(input question)与所得三元组的关系(attribute)属性的相似度，将最相似的三元组的答案作为答案，并与正确
          的答案进行匹配，correct +1
    3、 答案组合
    :return:
    '''
    with open(file, encoding='utf-8') as f:
        total = 0
        recall = 0
        correct = 0
        ambiguity = 0    # 属性匹配正确但是答案不正确

        for line in f:
            try:
                total += 1
                question, entity, attribute, answer, ner = line.split("\t")
                ner = ner.replace("#", "").replace("[UNK]", "%").replace("\n", "")
                # case: entity Fuzzy Match
                # 找出所有包含这些实体的三元组
                sql_e0_a1 = "select * from nlpccQA where entity like '%" + ner + "%' order by length(entity) asc limit 20"
                # sql查出来的是tuple，要转换成list才不会报错
                result_e0_a1 = list(upload_data(sql_e0_a1))

                if len(result_e0_a1) > 0:
                    recall += 1

                    flag_fuzzy = True
                    # 非语义匹配，加快速度
                    # l1[0]: entity
                    # l1[1]: attribute
                    # l1[2]: answer
                    flag_ambiguity = True
                    for l in result_e0_a1:
                        if l[1] in question or l[1].lower() in question or l[1].upper() in question:
                            flag_fuzzy = False

                            if estimate_answer(l[2], answer):
                                correct += 1
                                flag_ambiguity = False
                            else:
                                loginfo.logger.info("\t".join(l))

                    # 非语义匹配成功，继续下一次
                    if not flag_fuzzy:

                        if flag_ambiguity:
                            ambiguity += 1

                        time.sleep(1)
                        loginfo.logger.info("total: {}, recall: {}, correct:{}, accuracy: {}%, ambiguity：{}".format(total, recall, correct, correct * 100.0 / recall, ambiguity))
                        continue

                    # 语义匹配
                    result_df = pd.DataFrame(result_e0_a1, columns=['entity', 'attribute', 'value'])
                    # loginfo.logger.info(result_df.head(100))

                    attribute_candicate_sim = [(k, bs.predict(question, k)[0][1]) for k in result_df['attribute'].tolist()]
                    attribute_candicate_sort = sorted(attribute_candicate_sim, key=lambda candicate: candicate[1], reverse=True)
                    loginfo.logger.info("\n".join([str(k)+" "+str(v) for (k, v) in attribute_candicate_sort]))

                    answer_candicate_df = result_df[result_df["attribute"] == attribute_candicate_sort[0][0]]
                    for row in answer_candicate_df.index:
                        if estimate_answer(answer_candicate_df.loc[row, "value"], answer):
                            correct += 1
                        else:
                            loginfo.logger.info("\t".join(answer_candicate_df.loc[row].tolist()))
                time.sleep(1)
                loginfo.logger.info("total: {}, recall: {}, correct:{}, accuracy: {}%, ambiguity：{}".format(total, recall, correct, correct * 100.0 / recall, ambiguity))
            except Exception as e:
                loginfo.logger.info("the question id % d occur error %s" % (total, repr(e)))


if __name__ == '__main__':
    kb_fuzzy_classify_test()