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
                        logging.FileHandler(f'sci_pop_score_logfile_{log_filename}.log',encoding='utf-8')
                    ])


# 计算得分

def popSci(key,index):
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    collectionName = f"CCNewsKnowledgeAgent_{index}"
    newCollectionName = f"CCNewsPopScoreAgent_{index}"
    logging.info(f"Starting thread for key {key} and index {index},collectionName {collectionName}")
    newCollections = db[newCollectionName]
    collections = db[collectionName]
    all_documents = list(collections.find())
    print(f"Number of documents: {len(all_documents)}")
    if len(all_documents) == 0:
        return
    batch_size = 1000  # 批量插入的大小
    batch = []  # 用于存储待插入的文档
    LLM = GLM4ClientEnglish(key)
    for i,document in tqdm(enumerate(all_documents)):
        try:
            score = -1
            updateKnowledge = document['updateKnowledge']
            abstract = document['abstract']
            original_id = document['original_id']
            m_agent_subject = document['m_agent_subject']
            s_agent_subject = document['s_agent_subject']
            prompt = f"""
                You are an expert in popular science content analysis, responsible for evaluating the complexity of the following article. Please rate the complexity according to the following dimensions:
                Language simplicity: Does the article use simple and easy - to - understand language? Does it avoid excessive technical terms?
                Sentence structure: Is the sentence structure complex? What is the ratio of long sentences to short sentences? And how complex are the sentences?Use of technical terms: Does the article use a large number of technical terms? Are these terms explained in detail?
                Paragraph structure and content organization: Does the article adopt a narrative structure, a problem - driven approach, or a logical progression? If it clearly uses a narrative approach, the final score should be between 1 - 3; if it clearly uses a problem - driven approach, the final score should be between 4 - 7; if it clearly uses a logical progression, the final score should be between 8 - 10. 1 represents the simplest and 10 represents the most complex.
                Please directly tell me the score from 1 to 10, no need to state the reasons. The content of the article is: {updateKnowledge}
            """
            result = LLM.send(prompt=prompt,content=updateKnowledge)
            if '1' in result and '0' not in result:
                score = 1
            elif '2' in result:
                score = 2
            elif '3' in result:
                score = 3
            elif '4' in result:
                score = 4
            elif '5' in result:
                score = 5
            elif '6' in result:
                score = 6
            elif '7' in result:
                score = 7
            elif '8' in result:
                score = 8
            elif '9' in result:
                score = 9
            elif '10' in result:
                score = 10
            # print("原文:",updateKnowledge)
            # print("增强后:",score)
            new_document = {
                'original_id':original_id,
                'abstract':abstract,
                'updateKnowledge':updateKnowledge,
                'score':score,
                'm_agent_subject':m_agent_subject,
                's_agent_subject':s_agent_subject,
            }
            batch.append(new_document)
            logging.info(f"文章{original_id}处理完成，继续下一个.....")
            # 批量插入
            if len(batch) >= batch_size:
                newCollections.insert_many(batch)
                batch.clear()
        except Exception as e:
            logging.error(f"数据集:{collectionName}报错,报错信息:{e}")
    if batch:
        newCollections.insert_many(batch)
        batch.clear()
    logging.info(f"Finished thread for key {key} and index {index}")

def main():
    logging.info("start PopScience process")
    configKeys = [
        "5d402c5e8df649b9acbe23058d261336.5n7AkiLxzf51t5tZ",
        "fa76761f31244f27be16c74be8c2745c.ObUwPInG4GzFIXxj",
        "e8daca08a0934cefb96fb72a34f7d702.Q3ACeQFNjO4P1qyb",
        "baccba9864b042f28474b37630ccaafb.5jh9PkmG5NGGkp50",
        "7d0e84ce617d4f8ca7bd72412f673c08.lQblXeRzfP99msFn",
        "21c4d4d31dbd49e58268e8d4b231ee8c.3alNfkHGLG2sNmtv"
    ]
    # popSci(configKeys[0],1)
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(popSci, configKeys[index%5], index) for index in range(10,11)]
        for future in futures:
            future.result()  # 等待所有线程完成
    logging.info("end PopScience process")


if __name__ == '__main__':
    # configKeys = [
    #     "5d402c5e8df649b9acbe23058d261336.5n7AkiLxzf51t5tZ",
    #     "99626758d48544d2822315c5e6eaf5ee.fuxIb0w9azCJtUNn",
    #     "799c6e24c32e4c7db26fe92442ba6c75.WePbYZMOmPc6kB0i",
    #     "cead652a24cd4de4aa9ee5ae9d8cd044.hAqjnmj8IWvaCMcx",
    #     "5c40f74a3eb341de90ca95a66ce55740.1kEZZD616pNCIUc5",
    #     "96cc3810ae9b43098f36b2754152f2a3.hbeFkwcJsWzlisrM"
    # ]
    # popSci(configKeys[0],1)
    main()