
class global_path:
    # ====input====
    __raw_data_path__ = "./data/"
    __data_for_classify_path__ = __raw_data_path__ + "dataset/labeled_dataset_without_label_migration_sample.json"
    
    __crawler_search_result_path__ = __raw_data_path__ + "crawler_search_result/"
    # __crawler_search_result_path__ = "./"
    
    __text_path__ = f"{__raw_data_path__}crawler_corpus/text_data.json" # k-means生成
    __all_response__dichotomy_path__ = f"{__raw_data_path__}raw_data/all_response_dichotomy_v1.json"
    __sani_input_path__ = __all_response__dichotomy_path__ # 特殊字符占比生成
    __sani_output_path__ = __raw_data_path__ + "crawler_corpus/text_response_sanitization_v4.json"
    __crawler_tfidf_path__ = __raw_data_path__ + "crawler_corpus/text_response_tfidf_v4.json"

    __line_migration_map_path__ = f"{__raw_data_path__}raw_data/line_migration_map.json"
    
    __agent_labels_path__ = __raw_data_path__ + "agent_outputs/agent_labels"
    __2_response_pattern_result_path__ = __raw_data_path__ + "crawler_corpus/response_pattern.json"
    
    
    __assets_library_path__ = "/__assets_tree/"
    __origin_ip_path__ = __raw_data_path__ + "dataset/labeled_dataset_without_label_migration.json"
    __label_migration_result_path__ = __raw_data_path__ + "label_migration_result/"
    __origin_label_path__ =  __label_migration_result_path__ + "origin_assets_ch.json"
    __openai_label_path__ = __label_migration_result_path__ + "openai_assets_en.json"
    __line_ip_map_path__ = __raw_data_path__ + "raw_data/line_migration_map.json"
    __dictionary_path__ = __raw_data_path__ + "dictionary/"
    
    __label_dict_path__ = __label_migration_result_path__ + "/tmp_label_dict.json"
    
    __dataset_path__ = __raw_data_path__ + "dataset/"
    __model_path__ = "./model/"
    
class utils_path:
    # Path to the dictionary words file
    WORD_DICTIONARY_PATH = './data/util_data/dictionary_words'

    # Path to the blacklist file
    BLACKLIST_PATH = './data/util_data/blacklist.txt'