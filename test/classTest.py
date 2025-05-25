from mongo_helper import MongoHelper
from tqdm import tqdm
import logging
import json
from datetime import datetime
log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'sci_classify_logfile_{log_filename}.log',encoding='utf-8')
                    ])


def main():
    dictData = {}
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    sameAllNum = 0
    sameInNum = 0
    diffNum = 0
    total = 0
    diff_documents = []  # 用于保存 diff 文档
    single_counts = {}  # 用于统计 singleDoc 的种类和数量

    for index in tqdm(range(1, 3)):
        collectionName = f"pereduSubjectAgent_{index}"
        collections = db[collectionName]
        all_documents = list(collections.find())
        for document in tqdm(all_documents):
            total += 1
            singleDoc = document['s_agent_subject']
            multiDoc = document['m_agent_subject']

            # 统计 singleDoc 的种类和数量
            if singleDoc in single_counts:
                single_counts[singleDoc] += 1
            else:
                single_counts[singleDoc] = 1
            # dictData
            # if singleDoc is None or multiDoc is None:
            #     continue
            # if singleDoc == multiDoc:
            #     sameAllNum = sameAllNum + 1
            # elif singleDoc in multiDoc:
            #     sameInNum = sameInNum + 1
            # else:
            #     diff_documents.append({
            #         "内容": document.get('abstract', ''),
            #         "singleDoc": singleDoc,
            #         "multiDoc": multiDoc
            #     })
            #     diffNum =diffNum+ 1
    # with open(f'diff_documents_{log_filename}.json', 'w', encoding='utf-8') as f:
    #     json.dump(diff_documents, f, ensure_ascii=False, indent=4)
    # with open(f'diff_documents_{log_filename}.json', 'w', encoding='utf-8') as f:
    #     json.dump(diff_documents, f, ensure_ascii=False, indent=4)
    print("sameAllNum:", sameAllNum, "sameInNum:", sameInNum, "diffNum:", diffNum, "total:", total)
    print("singleDoc counts:", single_counts)  # 输出 singleDoc 的种类和数量







if __name__ == '__main__':
    main()