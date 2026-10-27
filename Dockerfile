
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY main.py /app/
COPY __assets_tree /app/__assets_tree
COPY __utils /app/__utils
COPY __logs /app/__logs
COPY __data_processing /app/__data_processing
COPY __label_migration /app/__label_migration
COPY requirements.txt /app/

# 创建目标目录并复制数据
RUN mkdir -p /app/data/util_data
COPY ./data/util_data/dictionary_words /app/data/util_data/dictionary_words
COPY ./data/util_data/blacklist.txt /app/data/util_data/blacklist.txt
COPY ./data/dataset/labeled_dataset_without_label_migration_sample.json /app/data/dataset/labeled_dataset_without_label_migration_sample.json


RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt


# 设置默认启动命令
# CMD ["python", "main.py"]
