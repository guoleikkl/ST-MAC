# 知识增强

import sys
sys.path.append('/home/zhengy/ScienceDataAnalyze')
import json
import re

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


# 文章评定

def parse_evaluation_result(result_text):
    """
    解析大模型返回的评估结果，提取 isValid 值
    :param result_text: str, 大模型返回的文本结果
    :return: int, 1 代表符合科普标准，0 代表不符合
    """
    try:
        # 方式1：使用 JSON 解析（适用于标准 JSON 格式）
        result_json = json.loads(result_text.replace("'", "\""))  # 替换单引号为双引号
        return int(result_json.get("isValid", 0))  # 获取 isValid 值，默认为 0

    except json.JSONDecodeError:
        # 方式2：使用正则表达式提取（适用于非标准格式）
        match = re.search(r"isValid:\s*['\"]?(\d)['\"]?", result_text)
        if match:
            return int(match.group(1))  # 提取到的数值转换为整数

    # 如果无法解析，返回默认值 0
    return 0

def evaluate_articles(mongo,key,index,dataRange,collections):
    # logging.info(f"Starting thread for key {key} and index {index}")
    newCollectionName = f"CCNewsArticleEval_10"
    logging.info(f"Starting thread for key {key} and index {index},newCollectionName:{newCollectionName}")
    client = mongo.client
    db = client['personalization']
    newCollections = db[newCollectionName]
    start =dataRange[0]
    end = dataRange[1]
    new_all_documents = list(collections.find())
    all_documents = new_all_documents[start:end]
    batch_size = 500  # 批量插入的大小
    batch = []  # 用于存储待插入的文档
    LLM = GLM4ClientEnglish(key)
    try:
        for i,document in tqdm(enumerate(all_documents)):
            content = document['abstract']
            original_id = document['original_id']
            abstract = document['abstract']
            popsciDoc = document['popsciDoc']
            score = document['score']
            temp = """
            {isValid: '1' or '0',// 1 means the article meets the standards for science popularization, 0 means it does not meet them
            'reason':'Explanation of the reason'}
            """
            prompt = f"""
                You are the expert responsible for the quality assessment of the article. Your task is to evaluate the current science popularization article based on the following three aspects:
                1. User Knowledge Level:Ensure the article’s content maintains a knowledge density suitable for science popularization. Evaluate factors such as vocabulary difficulty, article complexity, and frequency of technical terms. Verify if these aspects align with the standard for science communication.
                2. Knowledge Graph Generated Content: The input science popularization article must match the core content conveyed in the knowledge graph generated article. Please evaluate whether the content aligns with the original knowledge graph’s content. The deviation between the article and the knowledge graph should be evaluated for any significant divergence
                3. Language and Artistic Style Please evaluate whether the science popularization article is logically coherent, whether appropriate examples or metaphors have been used to help the user understand, and ensure that the artistic expression of the content does not affect its scientific rigor. Artistic expression should enhance readability and understanding without compromising the scientific integrity of the article.
                Based on the above three aspects, the overall judgment is made to determine whether the article meets the standards for science popularization:
                If the article meets all standards, return '1', indicating it passes the evaluation If the article fails to meet one or more standards, return ”0” and provide a detailed explanation of the reasons.
                Please provide the assessment result in the following format:{temp}
                Science popularization article content: {popsciDoc}, Knowledge graph
                generated content: {abstract}
            """
            result = LLM.send(prompt=prompt,content=content)
            # print("原文:",content)
            print("提出结果:",parse_evaluation_result(result))
            isValid = parse_evaluation_result(result)
            if not isValid:
                continue
            new_document = {
                'original_id':original_id,
                'abstract':content,
                'updateKnowledge':result,
                'popsciDoc':popsciDoc,
                'isValid':isValid,
                'score':score
            }
            batch.append(new_document)
            logging.info(f"文章{original_id}处理完成，继续下一个.....")
            # 批量插入
            if len(batch) >= batch_size:
                newCollections.insert_many(batch)
                batch.clear()
                quit()
    except Exception as e:
        logging.error(f"数据集:{newCollectionName}报错,报错信息:{e}")
    if batch:
        newCollections.insert_many(batch)
        batch.clear()
    logging.info(f"Finished thread for key {key} and index {index}")


def main():
    logging.info("start knowledge procee")
    configKeys = [
        ".VXDpEtjzB3AB4FWT",
        ".I8HnhXDYDa8V0eoN",
        ".3CtrzN9ih92tvtTL",
        ".ZDk8Jz9ZrP7xYAgY",
        ".IgS5Qh81Z2VwivEl",
        ".ilj2YdT91uXAVJGx"
    ]
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    collectionName = "CCNewsPopSCIAgent_10"
    collections = db[collectionName]
    dataSplit=[(0,1000),(1000,2000),(2000,3000),(3000,4000),(4000,5000)]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(evaluate_articles,mongo,configKeys[index%len(configKeys)],index,dataRange,collections) for index,dataRange in enumerate(dataSplit,start=0)]
        for future in futures:
            future.result()  # 等待所有线程完成
    logging.info("end knowledge procee")


if __name__ == '__main__':
    main()
