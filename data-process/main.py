import sys
sys.path.append('/home/zhengy/ScienceDataAnalyze')
from mongo_helper import MongoHelper
import logging
from datetime import datetime
from tqdm import tqdm
import json
import re

log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'logfile_{log_filename}.log',encoding='utf-8')
                    ])


def contains_chinese(text):
    """检查字符串中是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))



def main():
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    logging.info('train.source, train.target start process data ...')
    train_triple = 0
    val_triple = 0
    test_triple = 0
    error_num = 0
    with open('train.source', 'w', encoding='utf-8') as source:
        with open('train.target', 'w', encoding='utf-8') as target:
            for i in tqdm(range(1,4),total=3):
                collectionName = f'pereduKGCnToEnglish_v2_part_{i}'
                logging.info(f'start process {collectionName}')
                collections = db[collectionName]
                all_documents = list(collections.find())
                for index,document in tqdm(enumerate(all_documents)):
                    kg_content  = document['kgContent']
                    kg_target = document['abstract']
                                        # 如果包含中文字符，则跳过
                    if contains_chinese(kg_content) or contains_chinese(kg_target):
                        error_num = error_num + 1
                        continue
                    format_json = json.loads(kg_content)
                    # 这里得到一个所有的三元组，现在要的到一个字符串
                    kgGraph = ''
                    for item in format_json:
                        head = item['head']
                        rel = item['rel']
                        tail = item['tail']
                        if head == '' or rel == '' or tail == '':
                            continue
                        else:
                            train_triple = train_triple + 1
                            kgGraph = kgGraph+ f'<S>{head}<P>{rel}<O>{tail}'
                    if kgGraph and kg_target:
                        source.write(kgGraph + '\n')  # 每个result一行
                        target.write(kg_target + '\n')
    logging.info('train.source, train.target end process data ...')
    logging.info('val.source, train.target start process data ...')
    with open('dev.source', 'w', encoding='utf-8') as source_val:
        with open('dev.target', 'w', encoding='utf-8') as target_val:
            with open('test.source', 'w', encoding='utf-8') as source_test:
                with open('test.target', 'w', encoding='utf-8') as target_test:
                    for i in tqdm(range(4, 6),total=2):
                        collectionName = f'pereduKGCnToEnglish_v2_part_{i}'
                        logging.info(f'start process {collectionName}')
                        collections = db[collectionName]
                        all_documents = list(collections.find())
                        for index, document in tqdm(enumerate(all_documents)):
                            kg_content = document['kgContent']
                            kg_target = document['abstract']
                                                # 如果包含中文字符，则跳过
                            if contains_chinese(kg_content) or contains_chinese(kg_target):
                                error_num = error_num + 1
                                continue
                            format_json = json.loads(kg_content)
                            # 这里得到一个所有的三元组，现在要的到一个字符串
                            kgGraph = ''
                            cur_triple = 0
                            for item in format_json:
                                cur_triple = cur_triple + 1
                                head = item['head']
                                rel = item['rel']
                                tail = item['tail']
                                if head == '' or rel == '' or tail == '':
                                    continue
                                else:
                                    kgGraph = kgGraph + f'<S>{head}<P>{rel}<O>{tail}'
                            if index%2==0:
                                val_triple = val_triple + cur_triple
                                if kgGraph and kg_target:
                                    source_val.write(kgGraph + '\n')  # 每个result一行
                                    target_val.write(kg_target + '\n')
                            else:
                                test_triple = test_triple + cur_triple
                                if kgGraph and kg_target:
                                    source_test.write(kgGraph + '\n')  # 每个result一行
                                    target_test.write(kg_target + '\n')
    logging.info('val.source, train.target end process data ...')
    logging.info(f'train_triple:{train_triple}, val_triple:{val_triple},test_triple:{test_triple},error_num:{error_num}')
if __name__ == '__main__':
    # test = "Festival<P>be affected by / be included in / be marked by<O>United Nations Educational, Scientific and Cultural Organization (UNESCO)<S>The Spring Festival<P>列入: be included in or on<O>List of Intangible Cultural Heritage of"
    # print(contains_chinese(test))
    main()