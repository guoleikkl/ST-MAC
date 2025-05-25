from datasets import load_dataset

# 假设数据集的文件路径是 'path/to/your/file.parquet'
dataset = load_dataset('parquet', data_files='train-00000-of-00005.parquet')
data = list(dataset['train'])
print(len(data))
# 查看数据集的结构
for index,item in enumerate(data):
    print(item)
    quit()