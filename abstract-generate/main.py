import sys
from operator import index

# sys.path.append('/home/zhengy/ScienceDataAnalyze')
from mongo_helper import MongoHelper
from zhipuai import ZhipuAI
from tqdm import tqdm
import logging
from datetime import datetime
client = ZhipuAI(api_key="da2bd9097e594614a45afa9e01351708.NpJX7suQq0DthjGY")
log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'logfile_{log_filename}.log',encoding='utf-8')
                    ])
mongo = MongoHelper()

def main():
    client = mongo.client
    db = client['personalization']
    collectionNames = ['kepuchina_encyclopedia_of_life','kepuchina_frontier_science_and_technology','kepuchina_military_affairs','kepuchina_science_and_education','kepuchina_science_fiction','stdaily_education','stdaily_news']
    for collectionName in tqdm(collectionNames):
        collections = db[collectionName]
        all_documents = collections.find()
        try:
            # 将所有文档转换为包含'title'和'content'的字典列表
            articles = []
            for index,doc in enumerate(all_documents):
                try:
                    article = {'title': doc['title'], 'content': doc['content']}
                    articles.append(article)
                except Exception as e:
                    logging.error(f"Error:{collectionName},index:{index}",e)
                    continue
            # 调用store_abstracts函数处理文章
            store_abstracts(articles)
        except Exception as e:
            logging.error(f"Error generating abstract for collectionName {collectionName}: {e}")
            continue



def store_abstracts(articles, batch_size=100):

    collection_index = 2
    collection_name = f'abstractSCI{collection_index}'
    batch = []

    for index, article in tqdm(enumerate(articles)):
        try:
            # 生成唯一的SCI ID
            sci_id = f'SCI{index + 1}'

            # 处理文章内容
            title = article['title']
            content = article['content']

            # 如果内容超过4095个字符，进行截断
            if len(content) > 4000:
                content = content[:4000]
            # 调用generation函数生成摘要
            try:
                # 调用generation函数生成摘要
                result = generation(title,content)
            except Exception as e:
                print(f"Error generating abstract for article {sci_id}: {e}")
                continue
            # 创建文档
            document = {
                'sci_id': sci_id,
                'title': title,
                'abstract': result
            }
            batch.append(document)

            # 检查集合中文档数量
            db = mongo.client.get_default_database()
            collection = db[collection_name]
            if collection.count_documents({}) + len(batch) >= 5000:
                collection_index += 1
                collection_name = f'abstractSCI{collection_index}'
                collection = db[collection_name]

            # 批量插入
            if len(batch) >= batch_size:
                mongo.save_to_popsci(collection_name, batch)
                batch.clear()
        except Exception as e:
            logging.error(f"Error generating abstract for article: {article}，{e}")
            continue
    # 插入剩余的文档
    if batch:
        mongo.save_to_popsci(collection_name, batch)


def generation(title,content):
    if (content==''):
        content = title
    if content == '':
        return
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {
                "role": "system",
                "content": "你是一个信息提取专家，你的任务是帮我对科普文章进行内容摘要，先确保科普文章的知识含量，然后对超过500字的文章进行摘要,对较短的文章扩充。直接告诉我答案就行，不要前缀，只要文本，不用*等符号"
            },
            {
                "role": "user",
                "content": content
            }
        ],
        top_p=0.7,
        temperature=0.95,
        max_tokens=4095,
        tools=[{"type": "web_search", "web_search": {"search_result": True}}],
        stream=True
    )
    result = ""
    for trunk in response:
        for choice in trunk.choices:
            content = choice.delta.content.replace('\n', '').strip()
            result += content
    print("摘要内容:",result)
    return result


if __name__ == '__main__':
    main()