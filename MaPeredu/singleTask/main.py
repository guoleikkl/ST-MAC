# 知识增强

import sys

sys.path.append('/home/zhengy/ScienceDataAnalyze')
from mongo_helper import MongoHelper
import logging
from datetime import datetime
from tqdm import tqdm
from glm.glm4ApiEnglish import GLM4ClientEnglish

log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'seqToseq_pop_score_logfile_{log_filename}.log', encoding='utf-8')
                    ])


def main():
    logging.info('Starting')
    LLM = GLM4ClientEnglish(".eZiqCjYgDbaA9ZdV")
    mongo = MongoHelper()
    client = mongo.client
    collectionName = f"ccnews_SubjectAgent_10"
    db = client['personalization']
    newCollectionName = "CCNewsSingleTask_10"
    newCollections = db[newCollectionName]
    collections = db[collectionName]
    all_documents = list(collections.find())
    all_documents = all_documents[:3000]
    batch_size = 1000  # 批量插入的大小
    batch = []
    logging.info(f'total:{len(all_documents)},newCollectionName:{newCollectionName})')
    for index, document in tqdm(enumerate(all_documents)):
        abstract = document['abstract']
        original_id = document['original_id']
        s_agent_subject = document['s_agent_subject']
        field = s_agent_subject
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
                        You are an expert in {field}. Based on the given text, enrich the content in the following ways:
                        1. Add some background knowledge and embed it into the article.
                        2. When explaining the knowledge points in the article, add some case information.
                        3. For the knowledge points in the article, add some academic descriptions.
                        The output should maintain logical coherence and scientific accuracy, and the output format should be the same as the original text, which is a short passage without special characters.
                        The result should be in English, and directly output the article content.
                        The article to be revised is:{abstract}
                    """
        result = LLM.send(prompt=prompt, content=abstract)
        prompt2 = f"""
            You are a professional writing expert. Please generate a high-quality popular science article that meets the following requirements:
        1.	Scientific Accuracy: The content should be based on scientific consensus, ensuring factual accuracy while avoiding misleading or exaggerated claims. Key points should be supported by reliable data and sources.
        2.	Clarity: Scientific concepts should be explained in a simple and understandable manner, making them accessible to non-expert readers.
        3.	Logical Coherence: The article should have a clear logical structure, ensuring a well-organized progression of scientific explanations without abrupt transitions or gaps.
        4.	Engagement: The content should be engaging, using storytelling, vivid examples, or thought-provoking questions to capture the reader’s interest.
        5.	Readability and Accessibility: The use of technical jargon should be minimized, and necessary terms should be clearly explained so that readers with different knowledge backgrounds can understand the content.
        6.	Structural Integrity: The article should include a well-defined introduction, main body, and conclusion, ensuring a coherent and structured presentation.
        7.	Language Style: The writing should be natural and fluent, avoiding overly rigid or obscure expressions to enhance readability and approachability.
        8.	Potential for Sharing: The article should be written in a way that stimulates readers’ curiosity, encouraging them not only to gain knowledge but also to further explore or share the content.

            The article should be based on: {result}. Please return only the final article.
        """
        result_popsci = LLM.send(prompt=prompt2, content=result)
        result_document = {
            'original_id': original_id,
            'abstract': abstract,
            's_agent_subject': s_agent_subject,
            'updateKnowledge':result,
            'result_popsci':result_popsci
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
    main()
