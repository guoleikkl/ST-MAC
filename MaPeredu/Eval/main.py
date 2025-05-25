import sys

sys.path.append('/home/zhengy/ScienceDataAnalyze')
from mongo_helper import MongoHelper
import logging
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from glm.glm4ApiEnglish import GLM4ClientEnglish
log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'sci_knowledge_logfile_{log_filename}.log',encoding='utf-8')
                    ])
import json

def LLMZheng():
    logging.info('start LLMZheng')
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    pop_score_num = 0
    ori_score_num = 0
    equal_num =0
    total_num = 0
    for index in range(1,5):
        collectionName = f"MaPereduLLMZheng_{index}"
        collections = db[collectionName]
        all_documents = list(collections.find())
        total_num += len(all_documents)
        for i,document in enumerate(tqdm(all_documents)):
            result_score=document['result_score']
            if result_score == 'A':
                pop_score_num+=1
            elif result_score == 'B':
                ori_score_num+=1
            else:
                equal_num+=1
    logging.info(f'answer:pop_score_num:{pop_score_num},ori_score_num:{ori_score_num},equal_num:{equal_num},total_num:{total_num}')
    logging.info(f'pop_radio:{pop_score_num/total_num},ori_radio:{ori_score_num/total_num},equal_radio:{equal_num/total_num}')



    logging.info('end LLMZheng')

def MATEval():
    logging.info('start LLMZheng')
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    pop_score_num = 0
    ori_score_num = 0
    equal_num = 0
    total_num = 0
    for index in range(1, 5):
        collectionName = f"MAEval_{index}"
        collections = db[collectionName]
        all_documents = list(collections.find())
        total_num += len(all_documents)
        for i, document in enumerate(tqdm(all_documents)):
            pop_sci_score = int(document['pop_sci_score'])
            ori_sci_score = int(document['ori_sci_score'])
            if pop_sci_score<ori_sci_score:
                pop_score_num += 1
            elif pop_sci_score>ori_sci_score:
                ori_score_num += 1
            else:
                equal_num += 1
    logging.info(
        f'answer:pop_score_num:{pop_score_num},ori_score_num:{ori_score_num},equal_num:{equal_num},total_num:{total_num}')
    logging.info(
        f'pop_radio:{pop_score_num / total_num},ori_radio:{ori_score_num / total_num},equal_radio:{equal_num / total_num}')

def WebnlgMATEval():
    logging.info('start LLMZheng')
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    pop_score_num = 0
    ori_score_num = 0
    equal_num = 0
    total_num = 0
    collectionName = "CCNews_MATEval_1"
    collections = db[collectionName]
    all_documents = list(collections.find())
    total_num += len(all_documents)
    for i, document in enumerate(tqdm(all_documents)):
        pop_sci_score = int(document['pop_sci_score'])
        ori_sci_score = int(document['ori_sci_score'])
        if pop_sci_score < ori_sci_score:
            pop_score_num += 1
        elif pop_sci_score > ori_sci_score:
            ori_score_num += 1
        else:
            equal_num += 1
    logging.info(
        f'answer:pop_score_num:{pop_score_num},ori_score_num:{ori_score_num},equal_num:{equal_num},total_num:{total_num}')
    logging.info(
        f'pop_radio:{pop_score_num / total_num},ori_radio:{ori_score_num / total_num},equal_radio:{equal_num / total_num}')

def WebNLGLLMZheng():
    logging.info('start LLMZheng')
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    pop_score_num = 0
    ori_score_num = 0
    equal_num =0
    total_num = 0
    for index in range(1,5):
        collectionName = f"WebnlgSingleLLMZheng_{index}"
        collections = db[collectionName]
        all_documents = list(collections.find())
        total_num += len(all_documents)
        for i,document in enumerate(tqdm(all_documents)):
            result_score=document['result_score']
            if result_score == 'A':
                pop_score_num+=1
            elif result_score == 'B':
                ori_score_num+=1
            else:
                equal_num+=1
    logging.info(f'answer:pop_score_num:{pop_score_num},ori_score_num:{ori_score_num},equal_num:{equal_num},total_num:{total_num}')
    logging.info(f'pop_radio:{pop_score_num/total_num},ori_radio:{ori_score_num/total_num},equal_radio:{equal_num/total_num}')



    logging.info('end LLMZheng')
def EventLLMZheng():
    logging.info('start LLMZheng')
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    pop_score_num = 0
    ori_score_num = 0
    equal_num =0
    total_num = 0
    collectionName = "MaPereduSingleLLMZheng_1"
    collections = db[collectionName]
    all_documents = list(collections.find())
    total_num += len(all_documents)
    for i,document in enumerate(tqdm(all_documents)):
        result_score=document['result_score']
        if result_score == 'A':
            pop_score_num+=1
        elif result_score == 'B':
            ori_score_num+=1
        else:
            equal_num+=1
    logging.info(f'answer:pop_score_num:{pop_score_num},ori_score_num:{ori_score_num},equal_num:{equal_num},total_num:{total_num}')
    logging.info(f'pop_radio:{pop_score_num/total_num},ori_radio:{ori_score_num/total_num},equal_radio:{equal_num/total_num}')
    logging.info('end LLMZheng')
def Peredu():
    LLMZheng()
    # MATEval()

def Webnlg():
    WebnlgMATEval()
    # WebNLGLLMZheng()

def Event():
    EventLLMZheng()

def CCNews():
    EventLLMZheng()


def main():
    # Peredu()
    Webnlg()
    # Event()
if __name__ == '__main__':
    main()