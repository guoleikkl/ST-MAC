# 知识增强

import sys
import re
sys.path.append('/home/zhengy/ScienceDataAnalyze')
from mongo_helper import MongoHelper
import logging
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from glm.glm4ApiEnglishMulti import GLM4ClientEnglishMulti
from glm.glm4ApiEnglish import GLM4ClientEnglish
from MTAEval.SrCotFb import MaPereduMTAEval
log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'sci_pop_score_logfile_{log_filename}.log', encoding='utf-8')
                    ])


def score_analyze(Score_Analyze,score_doc):
    prompt = f"""
        Extract the final numerical score from the following text. The score is typically mentioned in a format like "Final Score: X points" or similar variations. Ensure you strictly extract and return only the numerical value as an integer.
        If the score is presented in a descriptive format (e.g., "The model received a score of X"), identify and extract the numeric value. If multiple scores appear, return the last valid score mentioned.
        Text:
        "
            {score_doc}
        "
        Output format:
        <number>
    """
    result = Score_Analyze.send(prompt,score_doc)
    # 使用正则表达式匹配分数（确保是数值）
    score_match = re.search(r"\d+", str(result))
    return int(score_match.group(0)) if score_match else None


def MAEval(key, index):
    logging.info(f"Starting thread for key {key} and index {index}")
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    collectionName = f"CCNewsPopSCIAgent_{index}"
    collections = db[collectionName]
    newCollectionName = f"CCNews_MAEval_{index}"
    newCollections = db[newCollectionName]
    pop_sci_analyze_collectionName = f"Webnlg_MAEval_Pop_{index}"
    pop_sci_analyze_collections = db[pop_sci_analyze_collectionName]
    ori_sci_analyze_collectionName = f"Webnlg_MAEval_Ori_{index}"
    ori_sci_analyze_collections = db[ori_sci_analyze_collectionName]
    all_documents = list(collections.find())
    print(f"Number of documents: {len(all_documents)}")
    if len(all_documents) == 0:
        return
    batch_size = 1000  # 批量插入的大小
    batch = []  # 用于存储待插入的文档
    pop_sci_analyze_results = []
    ori_sci_analyze_results = []
    LLM = GLM4ClientEnglishMulti(key)
    Score_Analyze = GLM4ClientEnglish(key)
    for i, document in tqdm(enumerate(all_documents)):
        try:
            original_id = document['original_id']
            abstract = document['abstract']
            updateKnowledge = document['updateKnowledge']
            score = int(document['score'])
            popsciDoc = document['popsciDoc']
            # print("原内容：",updateKnowledge)
            # print("难度分：", score)
            # print("优化内容：", popsciDoc)
            # 进行评分
            pop_sci_result = MaPereduMTAEval(LLM,original_id,popsciDoc)
            pop_sci_analyze_results.append(pop_sci_result)
            pop_sci_score_doc = pop_sci_result['final_score']
            pop_sci_score = score_analyze(Score_Analyze,pop_sci_score_doc)

            # 进行评分
            ori_sci_result = MaPereduMTAEval(LLM,original_id,abstract)
            ori_sci_analyze_results.append(ori_sci_result)
            ori_sci_score_doc = ori_sci_result['final_score']
            ori_sci_score = score_analyze(Score_Analyze,ori_sci_score_doc)
            if pop_sci_score is None or ori_sci_score is None:
                continue
            logging.info(f"优化后的科普文章扣分得分:{pop_sci_score}",)
            logging.info(f"优化前的科普文章扣分得分:{ori_sci_score}")
            # if i == 3:
            #     quit()
            new_document = {
                'original_id': original_id,
                'abstract': abstract,
                'updateKnowledge': updateKnowledge,
                'popsciDoc': popsciDoc,
                'pop_sci_score': pop_sci_score,
                'ori_sci_score': ori_sci_score,
            }
            batch.append(new_document)
            logging.info(f"文章{original_id}处理完成，继续下一个.....")
            if len(batch) >= batch_size:
                newCollections.insert_many(batch)
                batch.clear()
            if len(pop_sci_analyze_results) >= batch_size:
                pop_sci_analyze_collections.insert_many(pop_sci_analyze_results)
                pop_sci_analyze_results.clear()
            if len(ori_sci_analyze_results) >= batch_size:
                ori_sci_analyze_collections.insert_many(ori_sci_analyze_results)
                ori_sci_analyze_results.clear()
        except Exception as e:
            logging.error(f"数据集:{collectionName}报错,文章:{i},报错信息:{e}")
    if batch:
        newCollections.insert_many(batch)
        batch.clear()
    if pop_sci_analyze_results:
        pop_sci_analyze_collections.insert_many(pop_sci_analyze_results)
        pop_sci_analyze_results.clear()
    if ori_sci_analyze_results:
        ori_sci_analyze_collections.insert_many(ori_sci_analyze_results)
        ori_sci_analyze_results.clear()
    logging.info(f"Finished thread for key {key} and index {index}")


def main():
    logging.info("start MATEval process")
    configKeys = [
        "cdd935b5f0994d52aec886dc199f9c90.m3mYAjrLUukgQTQX",
        "d938d395474448cc9bdc2be3962a44e1.uWFQhVcTXjIiEi95",
        "8339567d82cd4c3a9b82a3f7092378a4.MaZ1EJrtzRNiGp9l",
        "d7772cb285694cf9b88b0657d91312cc.DIlX2dS6o5WD4jqx",
        "c44b431dd83e44fdbf2d7ac3ef48d582.r3LDc0gNccSOJzlV",
        "1eac68dbbdcc46ae891d3a466fe70f9c.K0ZLN6mlrencTTpF"
    ]
    # popSci(configKeys[0],1)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(MAEval, key, index) for index, key in enumerate(configKeys, start=1)]
        for future in futures:
            future.result()  # 等待所有线程完成
    logging.info("end MATEval process")

if __name__ == '__main__':
    # main()
    MAEval("cdd935b5f0994d52aec886dc199f9c90.m3mYAjrLUukgQTQX", 10)