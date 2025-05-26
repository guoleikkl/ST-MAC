# 知识增强

import sys

sys.path.append('/home/zhengy/ScienceDataAnalyze')
from mongo_helper import MongoHelper
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from tqdm import tqdm
from glm.glm4ApiEnglish import GLM4ClientEnglish
log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'seqToseq_pop_score_logfile_{log_filename}.log',encoding='utf-8')
                    ])



def main(config):
    logging.info('Starting')
    key = config['key']
    # collectionName = config['collectionName']
    # newCollectionName = config['newCollectionName']
    LLM = GLM4ClientEnglish(key)
    mongo = MongoHelper()
    client = mongo.client
    collectionName = f"pereduAbstractEnglish_part_1"
    db = client['personalization']
    newCollectionName = "PereduSeqToSeq_V3_1"
    newCollections = db[newCollectionName]
    logging.info(f'{newCollectionName}，key：{key}')
    collections = db[collectionName]
    all_documents = list(collections.find())
    all_documents = all_documents[:3000]
    batch_size = 1000  # 批量插入的大小
    batch = []
    logging.info(f'start total:{len(all_documents)}), collectionName:{collectionName}, newCollectionName:{newCollectionName}')
    for index,document in tqdm(enumerate(all_documents)):
        abstract = document['abstract']
        original_id = document['original_id']
        # prompt = f"""
        #     You are a professional writing expert. Please generate a high-quality popular science article that meets the following requirements:
        # 1.	Scientific Accuracy: The content should be based on scientific consensus, ensuring factual accuracy while avoiding misleading or exaggerated claims. Key points should be supported by reliable data and sources.
        # 2.	Clarity: Scientific concepts should be explained in a simple and understandable manner, making them accessible to non-expert readers.
        # 3.	Logical Coherence: The article should have a clear logical structure, ensuring a well-organized progression of scientific explanations without abrupt transitions or gaps.
        # 4.	Engagement: The content should be engaging, using storytelling, vivid examples, or thought-provoking questions to capture the reader’s interest.
        # 5.	Readability and Accessibility: The use of technical jargon should be minimized, and necessary terms should be clearly explained so that readers with different knowledge backgrounds can understand the content.
        # 6.	Structural Integrity: The article should include a well-defined introduction, main body, and conclusion, ensuring a coherent and structured presentation.
        # 7.	Language Style: The writing should be natural and fluent, avoiding overly rigid or obscure expressions to enhance readability and approachability.
        # 8.	Potential for Sharing: The article should be written in a way that stimulates readers’ curiosity, encouraging them not only to gain knowledge but also to further explore or share the content.
        #
        #     The article should be based on: {abstract}. Please return only the final article.
        # """
        prompt = f"""
                    You are a professional writing expert. Please generate a high-quality popular science article.
                    The article should be based on: {abstract}. Please return only the final article.
                """
        result = LLM.send(prompt=prompt, content=abstract)
        result_document = {
            'original_id':original_id,
            'abstract':abstract,
            'seqToseqDoc':result,
        }
        batch.append(result_document)
        logging.info(f"文章{original_id}处理完成，继续下一个.....")
        if len(batch) >= batch_size:
            newCollections.insert_many(batch)
            batch.clear()
    if batch:
        newCollections.insert_many(batch)
        batch.clear()
    logging.info('Finished')



if __name__ == '__main__':
    # Peredu

    configKeys=[{
        'key': '.Zp0dMBtoJjXfwH4l',
        'collectionName': 'pereduAbstractEnglish_part_1',
        'newCollectionName': 'PereduSeqToSeq_V3_1',
    },{
        'key':'.OGeSUfwZOMCKY2OO',
        'collectionName':'webnlg_1',
        'newCollectionName':'WebnlgSeqToSeq_V2_1',
    },{
        'key':'.hS1kTjGCjkzoKrCw',
        'collectionName':'event_1',
        'newCollectionName':'EventSeqToSeq_V2_1',
    },{
        'key':'.pNEJFkoNyEWNvAQT',
        'collectionName':'ccnews_10',
        'newCollectionName':'CCNewsSeqToSeq_V2_10',
    }]
    main(configKeys[0])
    # with ThreadPoolExecutor(max_workers=3) as executor:
    #     futures = [executor.submit(main, config) for config in configKeys]
    #     for future in futures:
    #         future.result()  # 等待所有线程完成
    logging.info("end PopScience process")
    # # Webnlg
    # main("2d3ee13653fb42e5962e95ed8b25a3c7.OGeSUfwZOMCKY2OO")
    # # Event
    # main("52e3cfe8211740078aa70b01378b5e30.hS1kTjGCjkzoKrCw")
    # # CCNews
    # main("020fd2b115624095bebfa23d1a2e2e69.pNEJFkoNyEWNvAQT")


