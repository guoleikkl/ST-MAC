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
log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'LLM_Zheng_Eval_logfile_{log_filename}.log', encoding='utf-8')
                    ])
ROLE = 'assistant'

def answerAnalyze(client,result):
    prompt = f"""
    Extract the final verdict from the following evaluation result. The final decision should be strictly formatted as "[[A]]", "[[B]]", or "[[C]]". 
    Ensure that you **only return the decision** without additional text. If multiple possible answers appear, select the last valid decision mentioned.
    Text:
    "{result}"
    Output format:
    <A/B/C>
    """
    # 发送请求到 LLM 并获取结果
    response = client.send(prompt,result)
    # 使用正则表达式提取最终评估结果
    match = re.search(r"\[\[(A|B|C)\]\]", response)

    return match.group(1) if match else None

# A是科普文章，B是正常文章
def selectAnswer(client,ori_document,pop_document):
    prompt = """
    Please act as an impartial judge and evaluate the quality of the two popular science articles provided below. 
    Your task is to determine which article better aligns with the principles of high-quality popular science writing.

    ### Definition of High-Quality Popular Science Writing:
    A well-written popular science article should meet the following criteria:

    1. **Scientific Accuracy**: The information should be factually correct, aligned with scientific consensus, and free from misleading or exaggerated claims. Reliable sources and data should support key assertions.
    2. **Clarity**: Complex scientific concepts should be explained in a simple, easy-to-understand manner.
    3. **Logical Coherence**: The flow of scientific explanations should be structured logically, ensuring smooth transitions between ideas and avoiding abrupt jumps that might confuse the reader.
    4. **Engagement**: The writing should capture the reader’s interest through storytelling, relatable examples, or thought-provoking questions.
    5. **Accessibility**: The article should minimize heavy technical jargon or clearly explain necessary terms, ensuring comprehension by a general audience.
    6. **Structure**: The article should have a well-organized structure with a clear introduction, main body, and conclusion that guides the reader through the topic smoothly.
    7. **Tone & Approachability**: The language should be friendly and conversational, making scientific knowledge enjoyable and approachable.
    8. **Impact & Shareability**: The article should have a compelling narrative, making it not only informative but also engaging enough to encourage readers to share or explore further.

    Your evaluation should take all these factors into account while also considering the **relevance, depth, and creativity** of the articles.

    ### Evaluation Instructions:
    - Compare both articles holistically and provide a short explanation of your reasoning.
    - Avoid positional biases and ensure that the order in which the articles were presented does not influence your decision.
    - Do not allow the length of the articles to impact your evaluation.
    - Be as **objective and scientific** as possible in your assessment.

    After providing your explanation, **strictly output your final decision in the following format**:
    - **"[[A]]"** → If **Article A is better**
    - **"[[B]]"** → If **Article B is better**
    - **"[[C]]"** → If **both articles are of equal quality (a tie)**
    """
    messages_agent1 = [{"role": "system", "content": prompt}]
    user_prompt=f"""
    Which article better fits the definition of high-quality popular science writing?
    [The Start of Article A]
    {pop_document}
    
    [The End of Article A]

    [The Start of Article B]
    {ori_document}
    [The End of Article B]
    """
    d = {"role": "user", "content": user_prompt}
    messages_agent1.append(d)
    result = client.send(messages_agent1)
    return result


def MAEval(key, index):

    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    collectionName = f"CCNewsArticleEval_{index}"
    collections = db[collectionName]
    newCollectionName = f"CCNewsLLMZheng_{index}"
    logging.info(f"Starting thread for key {key} and index {index},newCollectionName: {newCollectionName}")
    newCollections = db[newCollectionName]
    all_documents = list(collections.find())
    print(f"Number of documents: {len(all_documents)}")
    if len(all_documents) == 0:
        return
    batch_size = 1000  # 批量插入的大小
    batch = []  # 用于存储待插入的文档
    LLM = GLM4ClientEnglishMulti(key)
    answerAnalyzeLLM = GLM4ClientEnglish(key)
    for i, document in tqdm(enumerate(all_documents)):
        try:
            original_id = document['original_id']
            abstract = document['abstract']
            updateKnowledge = document['updateKnowledge']
            score = int(document['score'])
            popsciDoc = document['popsciDoc']
            # 进行评分
            # resultA中 A是pop，B是ori
            result_A = selectAnswer(LLM,abstract,popsciDoc)
            # resultA中 A是ori，B是pop

            result_analyze_A = answerAnalyze(answerAnalyzeLLM,result_A)
            result_B = selectAnswer(LLM, popsciDoc, abstract)
            result_analyze_B = answerAnalyze(answerAnalyzeLLM, result_B)
            if result_analyze_A is None or result_analyze_B is None:
                continue
            logging.info(f"这篇文章的第一次判断,A是优化，B是原文:{result_analyze_A}")
            logging.info(f"这篇文章的第二次判断,A是原文，B是优化:{result_analyze_B}")
            result_score = 'C'
            if result_analyze_A == 'A' and result_analyze_B == 'B':
                result_score = 'A'
            elif result_analyze_A == 'B' and result_analyze_B == 'A':
                result_score = 'B'
            else:
                result_score = 'C'
            logging.info(f"最终结果:A表示科普，B表示原文，C表示公平:{result_score}")
            # if i == 10:
            #     quit()
            new_document = {
                'original_id': original_id,
                'abstract': abstract,
                'updateKnowledge': updateKnowledge,
                'popsciDoc': popsciDoc,
                'score': score,
                'result_score':result_score
            }
            batch.append(new_document)
            logging.info(f"文章{original_id}处理完成，继续下一个.....")
            if len(batch) >= batch_size:
                newCollections.insert_many(batch)
                batch.clear()
        except Exception as e:
            logging.error(f"数据集:{collectionName}报错,文章:{i},报错信息:{e}")
    if batch:
        newCollections.insert_many(batch)
        batch.clear()
    logging.info(f"Finished thread for key {key} and index {index}")


def main():
    logging.info("start MATEval process")
    configKeys = [
        "d7772cb285694cf9b88b0657d91312cc.DIlX2dS6o5WD4jqx",
        "d7772cb285694cf9b88b0657d91312cc.DIlX2dS6o5WD4jqx",
        "a5a7c5eec10449d99757d670ad40a3fd.LCWP2CZDaPyrRNWc",
        "e8920a9608f746cbb7b8a7469f90cce0.UKz0VKO3ad4zOljc",
        "a040efdb480b48dabcda27f85d565c8e.u5erlnsZykOX3xQZ",
        "77686a1d56b748aeb608f0aaddb02487.aJhAsBIaCZycfo5Y"
    ]
    # popSci(configKeys[0],1)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(MAEval, key, index) for index, key in enumerate(configKeys, start=1)]
        for future in futures:
            future.result()  # 等待所有线程完成
    logging.info("end MATEval process")


if __name__ == '__main__':
    # main()
    MAEval("bedda43ae36c4c518169b089fabe5d43.XEDy3lMjjSsagCh5", 10)