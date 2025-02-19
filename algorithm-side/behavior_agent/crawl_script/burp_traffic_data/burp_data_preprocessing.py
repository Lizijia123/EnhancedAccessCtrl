

import xml.etree.ElementTree as ET
import csv
import json
from config.basic import CURR_APP_NAME
from urllib.parse import  quote_plus, unquote_plus

def urlencoded_to_json(urlencoded_data):
    # 解析 URL 编码的数据，同时保留原始编码
    parsed_data = {}
    for pair in urlencoded_data.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            key = unquote_plus(key)
            value = unquote_plus(value)
            if key in parsed_data:
                if isinstance(parsed_data[key], list):
                    parsed_data[key].append(value)
                else:
                    parsed_data[key] = [parsed_data[key], value]
            else:
                parsed_data[key] = value
        else:
            # 处理没有值的键
            key = unquote_plus(pair)
            parsed_data[key] = ""
    # 将处理后的数据转换为 JSON 字符串
    json_data = json.dumps(parsed_data)
    return json_data


def json_to_urlencoded(json_data):
    # 将 JSON 字符串转换为字典
    data_dict = json.loads(json_data)
    urlencoded_pairs = []
    for key, value in data_dict.items():
        if isinstance(value, list):
            for sub_value in value:
                # 使用 quote_plus 函数进行编码，同时处理空格和特殊字符
                urlencoded_pairs.append(f"{quote_plus(key)}={quote_plus(sub_value)}")
        else:
            urlencoded_pairs.append(f"{quote_plus(key)}={quote_plus(value)}")
    urlencoded_data = "&".join(urlencoded_pairs)
    return urlencoded_data

def parse_request_headers(header_string):
    headers = {}
    lines = header_string.split("\n")
    for line in lines:
        if line.strip():
            if ": " in line:
                parts = line.split(": ", 1)
                headers[parts[0]] = parts[1]
    return headers


def xml_to_csv(xml_file, csv_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['method', 'url', 'header', 'data', 'traffic_type', 'type'])

        for item in root.findall('item'):
            method = item.find('method').text
            url = item.find('url').text
            request = item.find('request').text
            header = parse_request_headers(request)
            data = None
            if method == 'POST':
                # TODO 根据content-type，解析body
                data = request.split('\n')[-1]

            status = item.find('status').text
            writer.writerow([method, url, header, data, status])

xml_to_csv(f'{CURR_APP_NAME}_burp_traffic_data.xml', f'{CURR_APP_NAME}_burp_log.csv')
#
#
# import json
# from urllib.parse import quote, unquote, urlencode
#
# # 示例数据
# original_urlencoded_data = "_csrf=ufn63XkmbKvwslWO-1ZRjiFHrL-N2ER3zCXWWvJ-eHvVwaq6ExNY2J7nAcWCZwTfZDD41cKtHiWGdpgIxRYpFA%3D%3D&AdvancedSettingsSpace%5BhideMembersSidebar%5D=0&AdvancedSettingsSpace%5BindexUrl%5D=&AdvancedSettingsSpace%5BindexGuestUrl%5D="
#
# # 转换为 JSON
# json_data = urlencoded_to_json(original_urlencoded_data)
# print("JSON data:", json_data)
#
# # 再转换回 URL 编码
# new_urlencoded_data = json_to_urlencoded(json_data)
# print("New URL encoded data:", new_urlencoded_data)
# print("Original URL encoded data:", original_urlencoded_data)
