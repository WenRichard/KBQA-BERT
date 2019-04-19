# KBQA-BERT
## 基于知识图谱的问答系统，BERT做命名实体识别和句子相似度，分为online和outline模式


## Introduction
本项目主要由两个重要的点组成，一是基于BERT的命名实体识别，二是基于BERT的句子相似度计算，本项目将这两个模块进行融合，构建基于BERT的KBQA问答系统，在命名实体识别上分为online predict和outline predict；在句子相似度上，也分为online predict和outline predict，2个模块互不干扰，做到了高内聚低耦合的效果，最后的kbqa相当于融合这2个模块进行outline predict，具体介绍请见[我的知乎专栏](https://zhuanlan.zhihu.com/p/62946533)！

### 环境配置

    Python版本为3.6
    tensorflow版本为1.13
    XAMPP版本为3.3.2
    Navicat Premium12
    
### 目录说明

    bert文件夹是google官方下载的
    Data文件夹存放原始数据和处理好的数据
        construct_dataset.py  生成NER_Data的数据
        construct_dataset_attribute.py  生成Sim_Data的数据
        triple_clean.py  生成三元组数据
        load_dbdata.py  将数据导入mysql db
    ModelParams文件夹需要下载BERT的中文配置文件：chinese_L-12_H-768_A-12
    Output文件夹存放输出的数据
    
    基于BERT的命名实体识别模块
    - lstm_crf_layer.py
    - run_ner.py
    - tf_metrics.py
    - conlleval.py
    - conlleval.pl
    - run_ner.sh
    
    基于BERT的句子相似度计算模块
    - args.py
    - run_similarity.py
    
    KBQA模块
    - terminal_predict.py
    - terminal_ner.sh
    - kbqa_test.py
    
 ### 使用说明
    
    - run_ner.sh
    NER训练和调参
    
    - terminal_ner.sh
    do_predict_online=True  NER线上预测
    do_predict_outline=True  NER线下预测
    
    - args.py
    train = True  预训练模型
    test = True  SIM线上测试
    
    - run_similarity.py
    python run一下就可以啦
    
    - kbqa_test.py
    基于KB的问答测试
  
 ### 实验分析
 训练时间长到发指，嗯，我们实验室搞深度学习老板不给买GPU，实验都是用耐心和毅力堆出来的，在这个没人的地方吐槽下！
 
 --------------------------------------------------------------
**如果觉得我的工作对您有帮助，请不要吝啬右上角的小星星哦！欢迎Fork和Star！也欢迎一起建设这个项目！**    
**有时间就会更新问答相关项目，有兴趣的同学可以follow一下**  
**留言请在Issues或者email xiezhengwen2013@163.com**
    
