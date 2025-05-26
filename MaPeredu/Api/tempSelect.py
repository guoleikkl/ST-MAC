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

def story(content,score,LLM):
    prompt = f"""
    You are a professional writer who excels at writing popular science articles to spread knowledge. Your task is to modify the style of the input article into a story - driven style, and increase the difficulty of the article according to the difficulty score for style transfer. The story - driven style is characterized by starting with an interesting or captivating story, quickly drawing readers into the situation, and then gradually leading to the core scientific topic.
    The article structure is as follows:
    1. Part 1: An Engaging Story Introduction
        - Use a small story, historical event, or life - like scene related to the topic to attract readers.
        - Pose questions or contradictions that arouse curiosity, such as "Why does ice float on water?" or "What makes humans so fascinated by black holes?"
    2. Part 2: Interpretation of Scientific Concepts
        - Connect the story or scenario to the core scientific topic, raise questions, and explain them in plain language.
        - Use analogies, metaphors, or examples from daily life to help readers understand complex concepts.
    3. Part 3: Expansion and Conclusion
        - Expand on the impact or background of the story, such as the significance of scientific discoveries, the practical applications of technology, etc.
        - End with a thought - provoking statement or a cliffhanger to guide readers to explore further.
    
    The article after the style transfer should be an English short essay, without obvious expressions such as "Part 1" and "Part 2".Just directly output the resulting article. 
    Article to be style - transferred: {content}, Difficulty score: {score} 
    """
    result = LLM.send(prompt,content)
    return result

def question(content,score,LLM):
    prompt = f"""
        You are a professional writer, proficient in writing popular - science articles that spread knowledge. Your task is to modify the style of the input article into a question - and - answer exploratory style. Additionally, you need to increase the difficulty of the article according to the difficulty score. The question - and - answer exploratory style is characterized by revolving around a series of key questions and gradually answering the possible doubts of readers.
        The article structure is as follows:

        1. Part 1: Raising Core Questions
            - Start with common yet thought - provoking questions, such as "Why is the sky blue?" or "Will artificial intelligence really replace humans?"
            - Briefly point out the importance or relevance of these questions to guide readers to keep reading.

        2. Part 2: Gradually Answering Questions
            - Break down the core questions into multiple sub - questions, with each paragraph corresponding to the answer to one question.
            - Begin from basic knowledge, progress step by step, and gradually unfold in - depth scientific principles or technical mechanisms.
            - Use clear logic to guide readers and enhance persuasiveness through illustrations, data, or cases.

        3. Part 3: Summary and Open - ended Discussion
            - Summarize the answers to the questions, distill the core knowledge points, and enable readers to review the article content.
            - Introduce unresolved issues or directions worthy of further research to stimulate readers' curiosity and desire for exploration.

        The article after the style transfer should be an English short essay, without obvious expressions such as "Part 1" and "Part 2". Just directly output the resulting article. 
        Article to be style - transferred: {content}, Difficulty score: {score}
        """
    result = LLM.send(prompt,content)
    return result


def layer(content,score,LLM):
    prompt = f"""
        You are a professional writer skilled at crafting popular science articles that disseminate knowledge. Your task is to modify the style of the input article into a hierarchical - progressive style and increase the article's difficulty according to the difficulty score. The characteristics of the hierarchical - progressive style are as follows: It progresses layer by layer from background introduction to detailed analysis and then to practical application, with a clear content structure.
            The article structure is as follows:
            1. Part 1: Background Introduction
                - Briefly introduce the background of the topic at the beginning, such as the development history of science and technology, existing problems, or research significance.
                - Use data or facts to enhance the credibility of the background content and quickly establish a topic framework for readers.

            2. Part 2: In - depth Analysis of Core Concepts
                - Focus on the key concepts or theories of the topic and explain them in detail from simple to complex.
                - Use analogies or step - by - step methods to help readers understand technical details or scientific principles.
                - Insert relevant case studies or experimental results to enhance the scientific nature and趣味性 of the article.

            3. Part 3: Practical Application and Outlook
                - Describe the practical application scenarios of the core concepts or technologies, such as their specific manifestations in daily life or their influence within the industry.
                - Discuss future development directions, unresolved problems, or potential impacts, guiding readers to think about the significance of science and technology to society.

            The article after the style transfer should be an English short essay, without obvious expressions such as "Part 1" and "Part 2".Just directly output the resulting article. 
            Article to be style - transferred: {content}, Difficulty score: {score}
        """
    result = LLM.send(prompt,content)
    return result


def popSci(key,index):
    logging.info(f"Starting thread for key {key} and index {index}")
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    collectionName = f"MaPereduPopScoreAgent_V3_{index}"
    collections = db[collectionName]
    newCollectionName = f"MaPereduPopSCIAgent_{index}"
    newCollections = db[newCollectionName]
    all_documents = list(collections.find())
    print(f"Number of documents: {len(all_documents)}")
    if len(all_documents) == 0:
        return
    batch_size = 1000  # 批量插入的大小
    batch = []  # 用于存储待插入的文档
    LLM = GLM4ClientEnglish(key)
    start = 0
    if index != 5:
        start = 5000
    for i,document in tqdm(enumerate(all_documents,start=start)):
        try:
            updateKnowledge = document['updateKnowledge']
            abstract = document['abstract']
            original_id = document['original_id']
            score = int(document['score'])
            popsciDoc = ''
            if score >= 1 and score <= 3:
                # 1-3
                popsciDoc = story(updateKnowledge,score-1,LLM)
            elif score >= 4 and score <= 7:
                # 1-4
                popsciDoc = question(updateKnowledge,score-3,LLM)
            elif score >= 8 and score <= 10:
                # 1-3
                popsciDoc = layer(updateKnowledge,score-7,LLM)
            if popsciDoc == '':
                continue
            # print("原内容：",updateKnowledge)
            # print("难度分：", score)
            # print("优化内容：", popsciDoc)
            new_document = {
                'original_id':original_id,
                'abstract':abstract,
                'updateKnowledge':updateKnowledge,
                'score':score,
                'popsciDoc':popsciDoc
            }
            batch.append(new_document)
            logging.info(f"文章{original_id}处理完成，继续下一个.....")
            if len(batch) >= batch_size:
                # newCollections.insert_many(batch)
                batch.clear()
            # if i ==5:
            #     quit()
        except Exception as e:
            logging.error(f"数据集:{collectionName}报错,文章:{i},报错信息:{e}")
    if batch:
        newCollections.insert_many(batch)
        batch.clear()
    logging.info(f"Finished thread for key {key} and index {index}")


def main():
    logging.info("start tempSelect process")
    configKeys = [
        ".Ak0mVn7Zrm1LLgiO",
        ".m3mYAjrLUukgQTQX",
        ".5n7AkiLxzf51t5tZ",
        ".Kah3xHd0AmOH2PYH",
        ".kur8pG8bk0282v1o",
        ".SxJFrFnwsR0EDWYj"
    ]
    # popSci(configKeys[0],1)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(popSci, key, index) for index, key in enumerate(configKeys, start=1)]
        for future in futures:
            future.result()  # 等待所有线程完成
    logging.info("end tempSelect process")


if __name__ == '__main__':
    # main()
    popSci("49a1ea5cbfd14ba8b57a200e9d1387da.Ak0mVn7Zrm1LLgiO",5)
