import logging
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd
import openpyxl
import json
import re

from os.path import dirname
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET
from collections import defaultdict
from sklearn.ensemble import IsolationForest
from gensim.models import Word2Vec

import fasttext.util


def init_drain3():

    config = TemplateMinerConfig()
    config.load(f"{dirname(__file__)}/api-discovery.ini")
    config.profiling_enabled = True
    template_miner = TemplateMiner(config=config)
    return template_miner


def extract_query_params(url):
    # 解析 URL，提取查询字符串部分
    parsed_url = urlparse(url)
    query_string = parsed_url.query

    # 解析查询字符串，得到参数字典
    query_params = parse_qs(query_string)

    # parse_qs 返回的字典中，每个键的值都是列表。这里我们转换为单个值，假设每个键只有一个值。
    # 如果一个键实际上有多个值，这里只会保留最后一个值。
    query_params_single_value = {k: v[-1] for k, v in query_params.items()}

    return query_params_single_value


def extract_xml_rpc_request_details(xml_string):
    # 解析 XML 字符串
    root = ET.fromstring(xml_string)

    # 提取方法名
    method_name = root.find('methodName').text

    # 初始化参数列表
    params = []

    # 遍历所有参数并提取其值
    for param in root.find('params').findall('param'):
        # 假设每个参数只有一个值
        value_element = param.find('value').find('*')
        # 根据不同的数据类型进行处理
        if value_element.tag == 'string':
            params.append(value_element.text)
        elif value_element.tag == 'int':
            params.append(int(value_element.text))
        # 根据需要添加更多类型的处理
        else:
            params.append(value_element.text)
    return method_name, params


def data_processing(data, content_type, bound):
    try:
        if content_type == "application/x-www-form-urlencoded":
            data = [d.split("=") for d in data.split("&")]
            data_dict = {}
            for item in data:
                data_dict[item[0]] = item[1]
            return (data_dict)
        elif content_type == "multipart/form-data":
            lines = data.split("\n")
            final_dict = {}
            final_data = None
            for line in lines:
                if bound in line: continue
                if ':' in line:
                    dline = [d.split("=") for d in data.split(";")]
                    for item in dline:
                        final_dict[item[0]] = item[1]
                else:
                    final_data = line
            return (final_dict, final_data)
        elif content_type == "application/json":
            # data_dict = eval(data)
            try:
                if data.strip().startswith("{'img"):
                    return None
            except AttributeError:
                return None
            # 将Python的True/False转换为JSON的true/false，将None转换为null
            # 同时确保所有的字符串值用双引号包围
            data_as_json_string = json.dumps(eval(data.replace('true', 'True').replace('false', 'False')))
            # 现在可以安全地使用json.loads来解析这个字符串
            data_dict = json.loads(data_as_json_string)
            return data_dict
        elif content_type == "text/xml":
            method_name, p = extract_xml_rpc_request_details(data)
            return (method_name, p)
    except Exception as e:
        return {}


# def anomaly_detection(content_type, data):

def extract_key_value(df):
    # template_miner = init_drain3()
    url_dict = defaultdict(list)
    index = 0
    for _, row in df.iterrows():
        # print("index: ", index)
        row = row.values
        method, url, header, data, order = row[1], row[2], row[3], row[4], row[0]
        url_parameter = extract_query_params(url)
        url = url.split("?")[0]
        # r = template_miner.add_log_message(url)
        # print(header)
        try:
            header = json.loads(header.replace("'", '"'))
        except (json.JSONDecodeError, AttributeError):
            header = None
        # print("header:"+str(header))
        # content_type = header["Content-Type"].split(";")
        # content_type = content_type[0]
        if header is None:
            content_type = "application/json"
        else:
            content_type = header.get("Content-Type", "application/json").split(";")[0]
        # print("content_type:" + content_type)
        bound = None
        if len(content_type) >= 2:
            bound = content_type[1]
        data = data_processing(data, content_type, bound)

        flag = True
        if index >= 2442:
            flag = False
        url_dict[url].append((url_parameter, data, order, flag))
        index += 1
    return url_dict


def cluster(url_dict, method):
    res_list = []
    template_miner = init_drain3()
    res = []
    example_traffic = {}
    for url in url_dict.keys():
        result = template_miner.add_log_message(url)
        if result["change_type"] != "none":
            res.append(url_dict[url])
            example_traffic[len(res) - 1] = url_dict[url][0]
        else:
            res[result["cluster_id"] - 1] += url_dict[url]
            if result["cluster_id"] - 1 not in example_traffic:
                example_traffic[result["cluster_id"] - 1] = url_dict[url][0]

    sorted_clusters = sorted(template_miner.drain.clusters, key=lambda it: it.size, reverse=True)

    for i, c in enumerate(sorted_clusters):
        res_list.append({
            'method': method,
            'API': c.get_template(),
            'data_id': example_traffic[i][2]
        })
    return res_list


# 检查异常的key
def anomaly_detection(data_2d):
    k = 0
    for line in data_2d:
        features = []
        for item in line:
            # print("item1:" + str(item))
            item = item[1]  # 提取字典
            # 将字典转换为字符串，然后再进行哈希化
            item = str(item)
            # print("item2:" + item)
            unique_words_count = len(set(item))  # 唯一词的数量
            total_words_count = len(item)  # 总词数
            # print(str(unique_words_count)+"," + str(total_words_count))
            features.append([unique_words_count, total_words_count])
        # 使用孤立森林模型进行异常检测
        model = IsolationForest()
        model.fit(features)
        # 预测异常值
        preds = model.predict(features)
        # 输出被标记为异常的列表
        # for i, item in enumerate(line):
        #     if preds[i] == -1:
        #         print(f"clusterId:{k}--total({len(line)})items--Anomaly detected: index{i}, {item}")
        k = k + 1

    # result_lis[r["cluster_id"]].append([url_parameter, data])


def word2vector(data_2d):
    ft = fasttext.load_model('cc.en.300.bin')
    k = 0
    vectors_list = []
    for line in data_2d:
        vectors = []
        for item in line:
            # print("item1:" + str(item))
            item = item[1]
            # print(f"clusterId:{k},{str(item)}")
            zero_vector = np.zeros(300)
            if item is None:
                vectors.append(zero_vector)
            else:
                # 遍历字典的键和值
                count = 0
                for key, value in item.items():
                    # 获取键的向量表示
                    key_vector = ft.get_word_vector(key)
                    zero_vector = zero_vector + key_vector
                    # 获取值的向量表示
                    value_vector = ft.get_word_vector(str(value))
                    zero_vector += value_vector
                    count = count + 2
                zero_vector = zero_vector / count
                vectors.append(zero_vector)
        # print(f"{k}:{vectors}")
        vectors_list.append(vectors)
        k = k + 1
    return vectors_list


def init_center_c(vectors):
    length = len(vectors)
    c = np.zeros(300)
    for vector in vectors:
        c += vector
    c /= length
    return c


"""
求分位数：即对dist(dist就是所有TEG到球心的距离的list)的概率分布求(1-nu)这个百分比处的距离值。
参见论文deep svdd：超参数ν∈(0,1]是离群值分数的上界，是超球外或超球边界上样本分数的下界。
"""


def get_radius(vectors, c, nu: float = 0.15):
    dist = []
    for vector in vectors:
        euclidean_distance = np.linalg.norm(vector - c)
        # print(f"距离：{euclidean_distance}")
        dist.append(euclidean_distance)
    return np.quantile(dist, 1 - nu)


def get_distance_list(vectors, c):
    distance_list = []
    for vector in vectors:
        distance_list.append(np.linalg.norm(vector - c))
    return distance_list


def get_bias_to_mean_distance(vectors, mean_distance):
    bias_list = []
    for vector in vectors:
        distance = np.linalg.norm(vector - mean_distance)
        bias_list.append(distance / mean_distance)
    return bias_list


def extract_api_list(df):
    # df = pd.read_excel(f'{dirname(__file__)}/humhub_url_crawl_log_modified.xlsx')
    df1 = df[df['method'] == 'Get']
    df2 = df[df['method'] == 'Post']
    df3 = df[df['method'] == 'Delete']
    df4 = df[df['method'] == 'Put']
    df5 = df[df['method'] == 'Patch']


    url_dict1 = extract_key_value(df1)
    url_dict2 = extract_key_value(df2)
    url_dict3 = extract_key_value(df3)
    url_dict4 = extract_key_value(df4)
    url_dict5 = extract_key_value(df5)

    res = []
    res.extend(cluster(url_dict1, 'Get'))
    res.extend(cluster(url_dict2, 'Post'))
    res.extend(cluster(url_dict3, 'Delete'))
    res.extend(cluster(url_dict4, 'Put'))
    res.extend(cluster(url_dict5, 'Patch'))
    return res
