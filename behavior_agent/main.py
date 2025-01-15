
"""
从爬虫记录中提取API（API发现或者基于用户配置）信息，以及可取参数集合并记录
"""
import api_extracting as ad
import crawl_log_preprocessing as clp
import param_set_collection as psc

if __name__ == '__main__':
    api_log = clp.extract_api_log_to_csv()
    api_log.to_csv('api_log.csv', index=False)
    api_list = ad.api_discovery(api_log, user_config_path=None)
    for api in api_list:
        print(api.to_dict())
    ad.gen_api_doc(api_list)

    psc.collect_param_set(api_log, api_list)
    # psc.collect_user_tokens()
