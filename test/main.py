import sys
sys.path.append('/home/zhengy/ScienceDataAnalyze')
import logging
import json
from datetime import datetime
from glm.glm4Api import GLM4Client
import concurrent.futures

log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'sci_classify_logfile_{log_filename}.log', encoding='utf-8')
                    ])


def process_document(apiKey, document):
    # 每个线程使用不同的 API 密钥创建一个新的客户端实例
    client = GLM4Client(apiKey)
    content = document['内容']
    singleDoc = document['singleDoc']
    multiDoc = document['multiDoc']

    promptA = f"""
    你是一个领域评判专家，你的任务是帮我评判这个文本的学科领域是属于A和B哪个答案。
    A:{singleDoc}
    B:{multiDoc}
    文本:{content}
    直接返回答案的选项A or B，只需要回复一个字母
    """
    resultA = client.send(promptA, content)

    promptB = f"""
    你是一个领域评判专家，你的任务是帮我评判这个文本的领域是属于A和B哪个答案。
    A:{multiDoc}
    B:{singleDoc}
    文本:{content}
    直接返回答案A or B，只需要回复一个字母
    """
    resultB = client.send(promptB, content)

    if resultA != resultB and 'B' in resultA:
        return 'B'
    elif resultB != resultA and 'A' in resultB:
        return 'A'
    else:
        return 'C'
def main():
    config = {
        'one': '99626758d48544d2822315c5e6eaf5ee.fuxIb0w9azCJtUNn',
        'two': 'cead652a24cd4de4aa9ee5ae9d8cd044.hAqjnmj8IWvaCMcx',
        'three': '77d65d1d8ad04cb9899f7d5aa7d7846d.aBMFnpu2G70RuF8G',
        'four': '96cc3810ae9b43098f36b2754152f2a3.hbeFkwcJsWzlisrM',
        'five': 'ea3a6ea7f63a4623b0e933b3321172e0.7Y5teY5JYTdGNigQ'
    }

    numA = 0
    numB = 0
    numC = 0

    # 读取 JSON 文件
    with open('diff_documents_2025_01_26_21_00_59.json', 'r') as f:
        data = json.load(f)

    # 使用线程池进行并行处理
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 为每个文档分配一个 API 密钥并处理
        # 通过循环给每个线程分配不同的 API 密钥
        keys = list(config.values())
        results = list(executor.map(lambda doc: process_document(keys[hash(doc['内容']) % len(keys)], doc), data))

    # 统计结果
    for result in results:
        if result == 'A':
            numA += 1
        elif result == 'B':
            numB += 1
        else:
            numC += 1

    logging.info(f'多agent: {numA}, 单agent: {numB}, 公平: {numC}')
if __name__ == '__main__':
    main()