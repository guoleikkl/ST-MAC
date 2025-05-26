# 知识增强

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
import re


# 知识增强

def knowledge(key,index):
    logging.info(f"Starting thread for key {key} and index {index}")
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    collectionName = f"ccnews_SubjectAgent_{index}"
    newCollectionName = f"CCNewsKnowledgeAgent_{index}"
    newCollections = db[newCollectionName]
    collections = db[collectionName]
    all_documents = list(collections.find())
    batch_size = 1000  # 批量插入的大小
    batch = []  # 用于存储待插入的文档
    LLM = GLM4ClientEnglish(key)
    try:
        for i,document in tqdm(enumerate(all_documents)):
            content = document['abstract']
            original_id = document['original_id']
            field = document['m_agent_subject']
            m_agent_subject = document['m_agent_subject']
            s_agent_subject = document['s_agent_subject']
            prompt = f"""
                You are an expert in {field}. Based on the given text, enrich the content in the following ways:
                1. Add some background knowledge and embed it into the article.
                2. When explaining the knowledge points in the article, add some case information.
                3. For the knowledge points in the article, add some academic descriptions.
                The output should maintain logical coherence and scientific accuracy, and the output format should be the same as the original text, which is a short passage without special characters.
                The result should be in English, and directly output the article content.
                The article to be revised is:{content}
            """
            result = LLM.send(prompt=prompt,content=content)
            # print("原文:",content)
            # print("增强后:",result)
            new_document = {
                'original_id':original_id,
                'abstract':content,
                'updateKnowledge':result,
                'm_agent_subject':m_agent_subject,
                's_agent_subject':s_agent_subject,
            }
            batch.append(new_document)
            logging.info(f"文章{original_id}处理完成，继续下一个.....")
            # 批量插入
            if len(batch) >= batch_size:
                newCollections.insert_many(batch)
                batch.clear()
            # if index == 5:
            #     quit()
    except Exception as e:
        logging.error(f"数据集:{collectionName}报错,报错信息:{e}")
    if batch:
        newCollections.insert_many(batch)
        batch.clear()
    logging.info(f"Finished thread for key {key} and index {index}")


def main():
    logging.info("start knowledge procee")
    configKeys = [
        ".",
        ".",
        ".",
        ".",
        ".",
        "."
    ]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(knowledge, configKeys[index%5], index) for index in range(1,2)]
        for future in futures:
            future.result()  # 等待所有线程完成
    logging.info("end knowledge procee")


if __name__ == '__main__':
    # main()
    knowledge("d23b2232b0c04bca9a79f9e992363426.opPdoaPSOOrDCFV5",10)
