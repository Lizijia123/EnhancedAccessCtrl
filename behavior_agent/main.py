
"""
从爬虫记录中提取API（API发现或者基于用户配置）信息，以及可取参数集合并记录
"""
import api_discovery as ad
import crawl_log_preprocessing as clp
import param_set_collection as psc

if __name__ == '__main__':
    api_log = clp.extract_api_log()
    api_list = ad.api_discovery(api_log, user_config_path=None)
    ad.gen_api_doc(api_list)

    psc.collect_param_set(api_log, api_list)
    psc.collect_user_tokens()
