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


def main():
    mongo = MongoHelper()
    client = mongo.client
    db = client['personalization']
    logging.info('train.source, train.target start process data ...')
    train_triple = 0
    val_triple = 0
    test_triple = 0
