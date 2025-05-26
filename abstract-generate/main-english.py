import sys
from operator import index

sys.path.append('/home/zhengy/ScienceDataAnalyze')
from mongo_helper import MongoHelper
from glm.glm4ApiEnglish import GLM4ClientEnglish
from tqdm import tqdm
import logging
from datetime import datetime
log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'english_logfile_{log_filename}.log',encoding='utf-8')
                    ])
mongo = MongoHelper()

def main():
    mongo = MongoHelper()
    client = mongo.client
    API_KEY = "."
    glm4_client = GLM4ClientEnglish(API_KEY)
    db = client['personalization']
    prompt = "你是一个翻译、信息抽取专家，你的任务是帮我对科普文章内容翻译，先确保科普文章的知识含量，然后对超过200字的文章进行摘要然后翻译。直接告诉我答案就行，不要前缀，只要文本，不用*等符号，保留英文的空格标点"
    kgCollectionName = "pereduAbstractEnglish"
    kgCollection = db[kgCollectionName]
    batch_size = 500  # 批量插入的大小
    batch = []  # 用于存储待插入的文档
    for i in tqdm(range(1, 8)):
        collectionName = f"abstractSCI{i}"
        collections = db[collectionName]
        all_documents = collections.find()
        for index, doc in tqdm(enumerate(all_documents)):
            trans_abstract2English = process_document(doc, glm4_client, prompt)
            if trans_abstract2English is not None:
                new_document = {
                    'original_id': doc['_id'],  # 保存原始文档的ID
                    'title': doc.get('title', 'No Title'),  # 假设文档有'title'字段
                    'abstract': trans_abstract2English
                }
                batch.append(new_document)
                logging.info(f"文章{doc['_id']}处理完成，继续下一个.....")
            # 批量插入
            if len(batch) >= batch_size:
                kgCollection.insert_many(batch)
                batch.clear()
        # 插入剩余的文档
        if batch:
            kgCollection.insert_many(batch)
            batch.clear()


def process_document(doc, glm4_client, prompt):
    try:
        abstract = doc['abstract']
        result = glm4_client.send(prompt, abstract)
        return result
    except Exception as e:
        logging.error(f"文章{doc['_id']}文章生成错误……,{e}")
        return None




if __name__ == '__main__':
    logging.info("english abstract has started")
    main()
    logging.info("english abstract has finished")
