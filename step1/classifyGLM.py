import sys

from glm.glm4ApiEnglish import GLM4ClientEnglish

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
                        logging.FileHandler(f'sci_classify_logfile_{log_filename}.log',encoding='utf-8')
                    ])

class MClassifyGLM():
    def format_to_json(self,result):
        try:
            # 去掉前缀 'json:' 和反引号
            result = result.strip('`')
            if result.startswith('json'):
                result = result[len('json'):]

            # 将单引号替换为双引号
            result = re.sub(r"'", '"', result)

            # 将字符串转换为JSON对象
            json_data = json.loads(result)

            # 格式化JSON对象为字符串
            formatted_json = json.dumps(json_data, ensure_ascii=False)

            return formatted_json
        except Exception as e:
            logging.error(f"Error decoding JSON: {e},处理后的结果：{result}")
            return None
    def __init__(self,API_KEY,subject):
        self.API_KEY = API_KEY
        self.client = GLM4ClientEnglish(API_KEY)
        self.subject = subject
    def classify_subject(self,content):
        is_sub = "{'is_sub':'1','probability':'value'}"
        is_not_sub = "{'is_sub':'0','probability':'value'}"
        try:
            prompt = f"You are a knowledgeable expert in the field of {self.subject}. Please help me determine whether this article belongs to your professional field and what the probability is. The answer format is a JSON.The result of 'probability' must be of a numeric type. If it is, the reply should be:{is_sub}; if not:{is_not_sub} . The content of the article is as follows: {content}"
            response = self.client.send(prompt,content)
            formatted_json = self.format_to_json(response)
            return formatted_json
        except Exception as e:
            raise Exception(e)

class SClassifyGLM():
    def format_to_json(self,result):
        try:
            # 去掉前缀 'json:' 和反引号
            result = result.strip('`')
            if result.startswith('json'):
                result = result[len('json'):]

            # 将单引号替换为双引号
            result = re.sub(r"'", '"', result)

            # 将字符串转换为JSON对象
            json_data = json.loads(result)

            # 格式化JSON对象为字符串
            formatted_json = json.dumps(json_data, ensure_ascii=False)

            return formatted_json
        except Exception as e:
            logging.error(f"Error decoding JSON: {e},生成错误的结果:{result}")
            return None
    def __init__(self,API_KEY):
        self.API_KEY = API_KEY
        self.client = GLM4ClientEnglish(API_KEY)
    def classify_subject(self,content):
        try:
            prompt =  f"You are an expert in the field of popular science. I will provide you with an article, and you need to tell me which of the following fields this article belongs to: Earth Science, Physics and Astrophysics, mathematics, Agriculture and Forestry Science, Materials Science, Computer Science, Environmental Science and Ecology, chemistry, Engineering Technology, biology, Medicine, Sociology, Psychology, pedagogy, Economics, Management, philosophy, history, Literature, Art.Just give me the answer of the classification. The content of the article is:{content}"
            response = self.client.send(prompt,content)
            return response
        except Exception as e:
            raise Exception(e)



if __name__ == '__main__':
    classify = MClassifyGLM()

