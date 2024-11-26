
class global_path:
    
    __raw_data_path__ = "/data_hdd/tzh24/zgc4/1_zgc_iot_iden/raw_data/"
    __data_for_classify_path__ = __raw_data_path__ + "device_assets_ori.json"
    
    __crawler_search_result_path__ = __raw_data_path__ + "crawler_search_result/"
    
    __text_path__ = f"{__raw_data_path__}crawler_corpus/text_data.json"
    __sani_path__ = __raw_data_path__ + "crawler_corpus/text_response_sanitization_v4.json"
    __crawler_tfidf_path__ = __raw_data_path__ + "crawler_corpus/text_response_tfidf_v4.json"
    __agent_labels_path__ = __raw_data_path__ + "agent_outputs/agent_labels.json"
    
    
    
    __assets_library_path__ = "/data_hdd/tzh24/zgc4/1_zgc_iot_iden/__assets_tree/"
    __origin_ip_path__ = __raw_data_path__ + "iot_assets_ip.json"
    __label_migration_result_path__ = __raw_data_path__ + "label_migration_result/"
    __origin_label_path__ =  __label_migration_result_path__ + "/origin_assets_ch.json"
    __openai_label_path__ = __label_migration_result_path__ + "/openai_assets_en.json"
    __line_ip_map_path__ = __raw_data_path__ + "/line_migration_map.json"
    __dictionary_path__ = __raw_data_path__ + "dictionary/"
    
    __label_dict_path__ = __label_migration_result_path__ + "/tmp_label_dict.json"
    
    __dataset_path__ = __raw_data_path__ + "dataset/"
    
class utils_path:
    # Path to the dictionary words file
    WORD_DICTIONARY_PATH = '/data_hdd/tzh24/zgc4/1_zgc_iot_iden/_4_DER/dictionary_words'

    # Path to the blacklist file
    BLACKLIST_PATH = '/data_hdd/tzh24/zgc4/1_zgc_iot_iden/raw_data/黑名单.txt'