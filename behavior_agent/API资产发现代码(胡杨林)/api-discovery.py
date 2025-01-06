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
from collections import defaultdict
import random

from os.path import dirname
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET
from collections import defaultdict
from sklearn.ensemble import IsolationForest
#from gensim.models import Word2Vec

import fasttext.util


def init_drain3():
    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

    config = TemplateMinerConfig()
    config.load(f"{dirname(__file__)}/my_drain3_test.ini")
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
        data_as_json_string = json.dumps(eval(data))
        # 现在可以安全地使用json.loads来解析这个字符串
        data_dict = json.loads(data_as_json_string)
        return data_dict
    elif content_type == "text/xml":
        method_name, p = extract_xml_rpc_request_details(data)
        return (method_name, p)


# def anomaly_detection(content_type, data):


def extract_key_value(df):

    # template_miner = init_drain3()
    url_dict = defaultdict(list)
    index = 0
    for _, row in df.iterrows():
        # print("index: ", index)
        row = row.values

        # method, url, header, data = row[1], row[2], row[3], row[4]
        method, url, header, data = row[0], row[1], row[2], row[3]

        url_parameter = extract_query_params(url)
        url = url.split("?")[0]
        # r = template_miner.add_log_message(url)
        # print(header)

        flag = True
        if index >= 2442:
            flag = False
        # url_dict[url].append((url_parameter, data, index, flag, header))
        url_dict[url].append((method, url_parameter, header, data, index, flag))
        index += 1
    return url_dict


def cluster(url_dict):
    template_miner = init_drain3()
    cluster_info = {}
    res = {}  # 初始化res为字典
    for url, traffic_list in url_dict.items():
        for traffic in traffic_list:
            result = template_miner.add_log_message(url)
            cluster_id = result["cluster_id"]
            template_mined = result["template_mined"]

            # 将 cluster_id、template_mined 和 url 存入字典中
            if cluster_id not in cluster_info:
                cluster_info[cluster_id] = (template_mined, [])
            cluster_info[cluster_id][1].append(url)

            # 存储每个cluster_id对应的流量数据
            if cluster_id not in res:
                res[cluster_id] = []  # 使用cluster_id作为键

            # 解构traffic
            method, url_parameter, header, data, index, flag = traffic
            res[cluster_id].append((index, flag, method, url, url_parameter, header, data))

    # 打印前缀树的每个集群
    sorted_clusters = sorted(template_miner.drain.clusters, key=lambda it: it.size, reverse=True)
    for c in sorted_clusters:
        print(c)

    # 输出 cluster_id、template_mined 和对应的流量数据
    for cluster_id, (template_mined, urls) in cluster_info.items():
        print()
        print(f"ID={cluster_id}模板（{template_mined}）包含的流量数据如下:")
        for traffic_data in res[cluster_id]:
            index, flag, method, url, url_parameter, header, data = traffic_data
            print(
                # f"Index: {index}, Flag: {flag}, Method: {method}, URL: {url}, URL Parameters: {url_parameter}, Header: {header}, Data: {data}")
                f"流量索引号: {index}, Method: {method}, URL: {url} Header: {header}, Data: {data}")

    print()
    print("----------------------------------------------")


'''
def cluster(url_dict):
    template_miner = init_drain3()
    cluster_info = {}
    res = []
    for url in url_dict.keys():
        result = template_miner.add_log_message(url)
        cluster_id = result["cluster_id"]
        template_mined = result["template_mined"]

        # 将 cluster_id、template_mined 和 url 存入字典中
        if cluster_id not in cluster_info:
            cluster_info[cluster_id] = (template_mined, [url])
        else:
            cluster_info[cluster_id][1].append(url)

        # print(f"'url':{url} ,'cluster_id':{cluster_id} ,'template':{template_mined}")
        if result["change_type"] != "none":
            res.append(url_dict[url])
        else:
            res[result["cluster_id"] - 1] += url_dict[url]
    # print("前缀树:")
    # template_miner.drain.print_tree()

    sorted_clusters = sorted(template_miner.drain.clusters, key=lambda it: it.size, reverse=True)
    for c in sorted_clusters:
        print(c)

    # 输出 cluster_id、template_mined 和对应的 url
    for cluster_id, (template_mined, urls) in cluster_info.items():
        # print(f"ID={cluster_id}    : Template={template_mined}    : URLs={urls}")
        print(f"ID={cluster_id}模板包含的流量数据如下:{urls}")

    return res
'''

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
    print(np.array(vectors_list[0]).shape)  # (453, 300) 该簇的流量数目 * 句向量维数（300）
    print(np.array(vectors_list[1]).shape)  # (156, 300) 该簇的流量数目 * 句向量维数（300）
    # result_lis[r["cluster_id"]].append([url_parameter, data])
    return vectors_list


def init_center_c(vectors):
    length = len(vectors)
    print(f"数据集长度：{length}")
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


def main():
    # df = pd.read_excel('DataGeneration_old_old\\normal_data_property.xlsx')
    # df = pd.read_excel('DataGeneration_old_old\\normal_data_ab_nd_new_new.xlsx')
    df = pd.read_excel('DataGeneration_old_old\\collegeERP-0.01-new-new.xlsx')

    df1 = df[df['method'] == 'GET']
    df2 = df[df['method'] == 'POST']
    df3 = df[df['method'] == 'DELETE']
    df4 = df[df['method'] == 'PUT']

    url_dict1 = extract_key_value(df1)
    url_dict2 = extract_key_value(df2)
    url_dict3 = extract_key_value(df3)
    url_dict4 = extract_key_value(df4)

    print("Get数据: ")
    res1 = cluster(url_dict1)
    print("Post数据: ")
    res2 = cluster(url_dict2)
    print("Delete数据: ")
    res3 = cluster(url_dict3)
    print("Put数据: ")
    res4 = cluster(url_dict4)

    print("---------------不同Method流量总览---------------")
    print("Get数据条数：", df1.shape[0])
    print("Post数据条数：", df2.shape[0])
    print("Delete数据条数：", df3.shape[0])
    print("Put数据条数：", df4.shape[0])
    print("总数据条数：", df.shape[0])


    # for index, line in enumerate(res):
    #     normal_count = 0
    #     abnormal_count = 0
    #     for item in line:
    #         # index = item[2]
    #         flag = item[3]
    #         if flag:
    #             normal_count += 1
    #         else:
    #             abnormal_count += 1
    #     print(f"第{index + 1}个簇：正常数据{normal_count}条，异常数据{abnormal_count}条")
    #     # print(f"第{index + 1}个簇对应的的列表：{line}")
    #
    # # anomaly_detection(res)
    #
    # # 向量化
    # vectors_list = word2vector(res)
    #
    # # 构建超球体，将大部分的数据包含在球体之中，其他的则为离群点
    # for index, vectors in enumerate(vectors_list):
    #     print("第"+str(index+1)+"个簇：")
    #     c = init_center_c(vectors)
    #     # 设置打印选项，使数组打印时不换行
    #     np.set_printoptions(threshold=np.inf, linewidth=np.inf)
    #     print(f"超球体球心：{c}")
    #     r = get_radius(vectors, c)
    #     print(f"超球体半径：{r}")
    #     distance_list = get_distance_list(vectors, c)
    #     print(distance_list)
    #     max_distance = max(distance_list)
    #     min_distance = min(distance_list)
    #     print("最大距离:", max_distance)
    #     print("最小距离:", min_distance)
    #     mean_distance = sum(distance_list) / len(distance_list)
    #     print(f"平均距离：{mean_distance}")
    #     print(f"异常距离判定比率：{max_distance / mean_distance}")

    # normal_count = 0
    # abnormal_count = 0
    # for vector in test_vectors:
    #     # print(vector)
    #     euclidean_distance = np.linalg.norm(vector - c)
    #     if euclidean_distance <= r:
    #         # print("正常")
    #         normal_count += 1
    #     else:
    #         # print("异常")
    #         abnormal_count += 1
    # print(f"正常数据条数: {normal_count}")
    # print(f"异常数据条数: {abnormal_count}")


if __name__ == "__main__":
    main()
