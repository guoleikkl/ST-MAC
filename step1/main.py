import sys

sys.path.append('/home/zhengy/ScienceDataAnalyze')
from mongo_helper import MongoHelper
import logging
from datetime import datetime
from tqdm import tqdm
import json
from classifyGLM import MClassifyGLM,SClassifyGLM
from concurrent.futures import ThreadPoolExecutor, as_completed

'''
    领域确定-多专家
'''

log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'webnlg_classify_logfile_{log_filename}.log',encoding='utf-8')
                    ])

CLASS_CONFIG=[{
    'class':'Earth Science',
    'key':'.',
},{
    'class':'Physics and Astrophysics',
    'key':'.',
},{
    'class':'mathematics',
    'key':'.',
},{
    'class':'Agriculture and Forestry Science',
    'key':'.',
},{
    'class':'Materials Science',
    'key':'.',
},{
    'class':'Computer Science',
    'key':'.',
},{
    'class':'Environmental Science and Ecology',
    'key':'.',
},{
    'class':'chemistry',
    'key':'.',
},{
    'class':'Engineering Technology',
    'key':'.',
},{
    'class':'biology',
    'key':'.',
},{
    'class':'Medicine',
    'key':'.',
},{
    'class':'Sociology',
    'key':'.',
},{
    'class':'Psychology',
    'key':'',
},{
    'class':'pedagogy',
    'key':'',
},{
    'class':'Economics',
    'key':'',
},{
    'class':'Management',
    'key':'',
},{
    'class':'philosophy',
    'key':'',
},{
    'class':'history',
    'key':'',
},{
    'class':'Literature',
    'key':'',
},{
    'class':'Art',
    'key':'',
}]


# 创建评判系统
def generateSubjectAgent():
    subject_clients = []
    for subject in CLASS_CONFIG:
        client_classify = MClassifyGLM(subject['key'], subject['class'])
        subject_clients.append(client_classify)
    return subject_clients

def client_judge(clients, doc):
    results = []

    def classify_with_client(client):
        result = client.classify_subject(doc)
        if result is not None:
            return {'subject': client.subject, 'score': result}
        return None

    # 使用ThreadPoolExecutor进行多线程处理
    with ThreadPoolExecutor(max_workers=len(clients)) as executor:
        # 提交所有任务
        futures = {executor.submit(classify_with_client, client): client for client in clients}
        
        # 收集所有完成的任务结果
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)
    return results


def getMaxSubject(items):
    orderList = []
    for item in items:
        subject = item['subject']
        score = item['score']
        json_score = json.loads(score)
        if json_score['is_sub']=="1":
            try:
                orderList.append({'subject':subject,'score':float(json_score['probability'])})
            except Exception as e:
                logging.error(f"错误信息:{e},格式化失败:{json_score['probability']}")
                continue
    if len(orderList) == 0:  # 如果 orderList 为空，返回一个默认值或处理逻辑
        logging.warning("No valid subjects found")
        return "No subjects found"  # 或者其他合适的返回值

    max_score = max(item['score'] for item in orderList)
    highest_subjects = [item['subject'] for item in orderList if float(item['score']) == max_score]
    # print(max_score,highest_subjects)
    highest_subjects_str = ' and '.join(highest_subjects)
    # print(f"Highest Score: {max_score}, Subjects: {highest_subjects_str}")
    return highest_subjects_str


def judge():
    prompt = '你是一个知识渊博的专家，你现在正在参与一个讨论会。你的任务是根据其他专家提供的信息来判定文章属于哪个领域。如果其他专家提出的领域是符合这个文章的内容，则返回Ture，且给出领域名字，如果此文章不属于提供信息中的领域，则返回False，并给出理由。'


# 领域确定

def subjectAssert(sAgent_KEY,index=1):
    single_client_classify = SClassifyGLM(sAgent_KEY)
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    collectionName = f"ccnews_{index}"
    newCollectionName = f"ccnews_SubjectAgent_{index}"
    newCollections = db[newCollectionName]
    logging.info(f"Starting thread and {collectionName} to {newCollectionName}")
    collections = db[collectionName]
    all_documents = list(collections.find())
    clients = generateSubjectAgent()
    batch_size = 1000  # 批量插入的大小
    batch = []  # 用于存储待插入的文档
    for document in tqdm(all_documents):
        try:
            content = document['abstract']
            original_id = document['_id']
            scores = client_judge(clients,content)
            logging.info(f'{original_id}:{scores}')
            subject = getMaxSubject(scores)
            single_subject = single_client_classify.classify_subject(content)
            new_document = {
                'original_id':original_id,
                'abstract':content,
                'm_agent_subject':subject,
                's_agent_subject':single_subject
            }
            # print(new_document)
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


def main():
    logging.info("start subject procee")
    sAgent_KEY = "ad9caddd3c4b487d8f46eb0a0a9f3188.uBhUgvmO8iy333hp"
    with ThreadPoolExecutor(max_workers = 5) as executor:
        futures = [executor.submit(subjectAssert,sAgent_KEY,index) for index in range(1,2)]
        # subjectAssert(sAgent_KEY, 1)
        for future in futures:
            future.result()  # 等待所有线程完成
    logging.info("end subject procee")

if __name__ == '__main__':
    main()
    # scores =[{'subject': 'biology', 'score': '{"is_sub": "1", "probability": "0.8"}'}, {'subject': 'Engineering Technology', 'score': '{"is_sub": "1", "probability": "0.95"}'}, {'subject': 'Computer Science', 'score': '{"is_sub": "1", "probability": "0.9"}'}, {'subject': 'philosophy', 'score': '{"is_sub": "1", "probability": "0.8"}'}, {'subject': 'Psychology', 'score': '{"is_sub": "1", "probability": "0.95"}'}, {'subject': 'chemistry', 'score': '{"is_sub": "0", "probability": "0.5"}'}, {'subject': 'Medicine', 'score': '{"is_sub": "1", "probability": "0.8"}'}, {'subject': 'Materials Science', 'score': '{"is_sub": "0", "probability": "0.5"}'}, {'subject': 'Earth Science', 'score': '{"is_sub": "0", "probability": "0.5"}'}, {'subject': 'Management', 'score': '{"is_sub": "1", "probability": "0.95"}'}, {'subject': 'Sociology', 'score': '{"is_sub": "1", "probability": "0.95"}'}, {'subject': 'pedagogy', 'score': '{"is_sub": "1", "probability": "0.95"}'}, {'subject': 'Agriculture and Forestry Science', 'score': '{"is_sub": "0", "probability": "0.75"}'}, {'subject': 'mathematics', 'score': '{"is_sub": "0", "probability": "0.5"}'}, {'subject': 'Environmental Science and Ecology', 'score': '{"is_sub": "0", "probability": "0.7"}'}, {'subject': 'Physics and Astrophysics', 'score': '{"is_sub": "0", "probability": "0.5"}'}, {'subject': 'Economics', 'score': '{"is_sub": "1", "probability": "0.95"}'}, {'subject': 'Literature', 'score': '{"is_sub": "0", "probability": "0.8"}'}, {'subject': 'history', 'score': '{"is_sub": "1", "probability": "0.9"}'}, {'subject': 'Art', 'score': '{"is_sub": "1", "probability": "0.95"}'}]
    # getMaxSubject(scores)
    # for indx in range(1,4):
    #     print(f"index:{indx}")

