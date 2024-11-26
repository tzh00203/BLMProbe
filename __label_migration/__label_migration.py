# -*- coding: utf-8 -*-
import sys
sys.path.append("/data_hdd/tzh24/zgc4/1_zgc_iot_iden/")

from multiprocessing import Process
from pprint import pprint
import json, random
from __logs.__log import log_init
from __utils.__path_util import global_path
from __utils.__save_file_util import save_dict_to_json
from __utils.__sort_util import sort_dict
from __label_migration_utils import label_name_unify

url_num = 5
NATURAL_LANG_DEFINE = 0.9
in_num_vendor_name_list = ["H3C", "h264dvr", "NetDvrV3"]


def load_openai_assets():
   
    openai_label_path = global_path.__agent_labels_path__
    openai_labels_dict = json.loads(open(openai_label_path, "r", encoding="utf-8").read())

    openai_assets_dict = {"vendor": {}, "type": {}, "product": {}}
    for index_ in openai_labels_dict:
        labels_list = openai_labels_dict[index_]
        for label_ in labels_list:
            print(label_[1])
            label_tmp = eval(label_[1])
            openai_assets_dict["vendor"][label_tmp["vendor"]] = ""
            openai_assets_dict["type"][label_tmp["type"]] = ""
            openai_assets_dict["product"][label_tmp["product"]] = ""

    save_dict_to_json(global_path.__openai_label_path__, openai_assets_dict)


def label_migration():
    origin_ch_en_path = global_path.__origin_label_path__
    origin_ch_en_dict = json.loads(open(origin_ch_en_path, "r", encoding="utf-8").read())
    vendor_list, type_list = origin_ch_en_dict["vendor"], origin_ch_en_dict["type"]
    openai_ch_en_dict = json.loads(open(global_path.__openai_label_path__, "r", encoding="utf-8").read())
    vendor_list_openai, type_list_openai = openai_ch_en_dict["vendor"], openai_ch_en_dict["type"]

    origin_ip_path = global_path.__origin_ip_path__
    origin_ip_dict = eval(open(origin_ip_path, "r", encoding="utf-8").read())

    origin_ip_dict_new = {}
    for ip in origin_ip_dict:
        print(ip)
        assets_tmp = str(origin_ip_dict[ip]['assets'][0])
        assets_tmp_dict_ = eval(assets_tmp)

        assets_tmp_dict_new = assets_tmp_dict_
        vendor_ = assets_tmp_dict_["vendor"]
        type_ = assets_tmp_dict_["type"]
        vendor_new = vendor_list[vendor_] if vendor_list[vendor_] != "" else vendor_
        type_new = type_list[type_] if type_list[type_] != "" else type_
        assets_tmp_dict_new["vendor"], assets_tmp_dict_new["type"] = vendor_new, type_new

        origin_ip_dict_new[ip] = origin_ip_dict[ip]
        origin_ip_dict_new[ip]["assets"] = [assets_tmp_dict_new]

    origin_ip_new_path = global_path.__label_migration_result_path__ + "tmp_iot_assets_ip_new.json"
    save_dict_to_json(origin_ip_new_path, origin_ip_dict_new)

    openai_labels_dict = eval(open(global_path.__agent_labels_path__, "r", encoding="utf-8").read())
    line_map_dict = eval(open(global_path.__line_ip_map_path__, "r", encoding="utf-8").read())

    cnt_= 0
    cnt_ip_ori = 0 
    
    label_dict_, label_num_ = {}, 0
    verify_extension_ip_dict = {}
    for line_index in openai_labels_dict:
        openai_labels_dict_tmp = openai_labels_dict[line_index]

        ip_tmp, index_num_tmp, src_tmp = line_map_dict[line_index][0], line_map_dict[line_index][1], line_map_dict[line_index][2]
        if src_tmp == "ori" and index_num_tmp == 0:
            # cnt_ip_ori += 1
            print("*** ", origin_ip_dict_new[ip_tmp]["assets"][0], openai_labels_dict_tmp['vendor'], openai_labels_dict_tmp['type'], openai_labels_dict_tmp['product'])
            if origin_ip_dict_new[ip_tmp]["assets"][0]["vendor"] == openai_labels_dict_tmp["vendor"]:
                cnt_ip_ori += 1
            if origin_ip_dict_new[ip_tmp]["assets"][0]["vendor"] == openai_labels_dict_tmp["vendor"] and \
                    label_name_unify(origin_ip_dict_new[ip_tmp]["assets"][0]["product"], openai_labels_dict_tmp["product"]):
                cnt_ += 1
                print(ip_tmp, cnt_, openai_labels_dict_tmp["product"])
                origin_ip_dict_new[ip_tmp]["assets"].append(
                    {
                        "vendor": openai_labels_dict_tmp['vendor'],
                        "type":  openai_labels_dict_tmp['type'],
                        "product": openai_labels_dict_tmp['product'],
                    }
                )
                
                print(origin_ip_dict_new[ip_tmp]["assets"])
                verify_extension_ip_dict[ip_tmp] = origin_ip_dict_new[ip_tmp]
                
                # origin_ip_dict_new[ip_tmp]["assets"][0]["product"] = origin_ip_dict_new[ip_tmp]["assets"][1]["product"][0]
        if str(origin_ip_dict_new[ip_tmp]["assets"][0]) not in label_dict_:
            label_dict_[str(origin_ip_dict_new[ip_tmp]["assets"][0])] = str(label_num_)
            label_num_ += 1
    
    save_dict_to_json(global_path.__label_dict_path__, label_dict_)    
    gen_dataset(origin_ip_dict_new, label_dict_)
    

def gen_dataset(origin_ip_dict_new, label_dict):
    from __data_processing.__data_sanitization import sanitization_string
    from __data_processing.__data_TFIDF_util import tfidf_calc
    from __label_migration_utils import shuffle_with_seed, split_string_by_word_count, get_binary
    from __utils.__unicode_util import unicode_calc_proportion, hex_calc_proportion
    tfidf_corpus, tfidf_corpus_id, tfidf_words_dict_ip = [], [], {}
    id_res = 0
    tfidf_words_index = []
    clas_data_list = []
    keywords_dict = {}
    context_list = []
    f1, f2 = 0, 0
    for ip_ in origin_ip_dict_new:
        ip_response_str = ""
        tfidf_corpus_tmp = []
        clas_list = []
        unnatural_list = []
        for index_, response_ori in enumerate(origin_ip_dict_new[ip_]["response_data"]):
            if response_ori == "":
                continue
            # if origin_ip_dict_new[ip_]["src"][index_] == "extend":
            #     continue
            uu_pro = unicode_calc_proportion(response_ori) + hex_calc_proportion(response_ori)
            unnatural_flag = False
            
            # binary or text
            if uu_pro > NATURAL_LANG_DEFINE:
                f1 += 1
                response_ = get_binary(response_ori) + " " +sanitization_string(response_ori)
                print(response_)
                unnatural_flag = True           
            else:
                response_ = sanitization_string(response_ori)
                f2 += 1

            response_tt = response_.replace("\t", " ")
            protocol_tt = origin_ip_dict_new[ip_]["protocol"][index_]
            src_tt = origin_ip_dict_new[ip_]["src"][index_]
            
            if len(response_tt.strip().split()) > 30:
                response_tt_list = split_string_by_word_count(response_tt)
                response_tt_list = [res_t + " " + protocol_tt for res_t in response_tt_list]
                unnatural_tt_list = [unnatural_flag for _ in range(len(response_tt_list))]
                clas_list.extend(response_tt_list) 
                unnatural_list.extend(unnatural_tt_list)
            else:
                clas_list.append(response_tt + " " + protocol_tt)
                unnatural_list.append(unnatural_flag)
            tfidf_corpus.append(response_tt)
            tfidf_corpus_id.append(id_res)
            tfidf_words_index.append(ip_)
            id_res += 1
            print(id_res, "=====")
            ip_response_str += (response_ + " ")
            
        context_tmp = " ".join(ip_response_str.strip().split())
        assets_tmp = origin_ip_dict_new[ip_]["assets"][0]
        # if context_tmp + str(assets_tmp) in context_list:
        #     continue
    
        context_list.append(context_tmp + str(assets_tmp)) 
        keywords_dict[ip_] = {}
        keywords_dict[ip_]["context"] = context_tmp
        keywords_dict[ip_]["keywords"] = []
        keywords_dict[ip_]["assets"] = assets_tmp
        keywords_dict[ip_]["clas_list"] = clas_list
        keywords_dict[ip_]["unnatural_list"] = unnatural_list
        tfidf_words_dict_ip[ip_] = []
        
    tfidf_words_dict = tfidf_calc(tfidf_corpus, tfidf_corpus_id)
    
    for x in tfidf_words_dict:
        print(tfidf_words_dict[x])
        
        keywords_dict[tfidf_words_index[x]]["keywords"].extend(tfidf_words_dict[x])
        each_ip_keywords = list(set(keywords_dict[tfidf_words_index[x]]["keywords"]))
        keywords_dict[tfidf_words_index[x]]["keywords"] = each_ip_keywords
        
        tfidf_words_dict_ip[tfidf_words_index[x]].append(tfidf_words_dict[x])

    # save_dict_to_json("/data_hdd/tzh24/zgc4/1_zgc_iot_iden/__related_work/tmp_fingerprints_tfidf.json", tfidf_words_dict_ip)
    
    
    cnt_print = 1
    same_clas_lst = {}
    cnt_label_ = 0
    for ip_ in keywords_dict:
        print(cnt_print, ip_)
        cnt_print += 1
        if keywords_dict[ip_]["context"] == "":
            continue
        
        labels_list_ = list(label_dict.keys())
        if str(origin_ip_dict_new[ip_]["assets"][0]) not in labels_list_:
            cnt_label_ += 1
            label_dict[str(origin_ip_dict_new[ip_]["assets"][0])] = len(list(label_dict.keys()))
            
        label_str = str(origin_ip_dict_new[ip_]["assets"][0])
        str_list_tt = keywords_dict[ip_]["clas_list"]
        un_flag_list_tt = keywords_dict[ip_]["unnatural_list"]
        for str_tt_index in range(len(str_list_tt)):
            str_tt = str_list_tt[str_tt_index]
            un_flag = un_flag_list_tt[str_tt_index]
            if " ".join(str_tt.strip().split()) == "" or len(str_tt.strip().split()) < 3:
                continue
            if un_flag == False:
                str_tt = "textual language: " + str_tt
                
            else:
                continue
                str_tt = "binary data: " + str_tt

            if str_tt not in same_clas_lst:
            # same_clas_lst = { str1 : {assets1 : num }  }
                same_clas_lst[str_tt] = {}
            if str(label_dict[label_str]) not in same_clas_lst[str_tt]:
                same_clas_lst[str_tt][str(label_dict[label_str])] = 1
            else:
                same_clas_lst[str_tt][str(label_dict[label_str])] += 1
            # clas_data_list.append(str_tt + "\t" + str(label_dict[label_str]))
                
    multi_num = 0
    # print(same_clas_lst)
    for str_ttt in same_clas_lst:
        if len(same_clas_lst[str_ttt]) > 1:
            same_clas_lst[str_ttt] = dict(sorted(same_clas_lst[str_ttt].items(), key=lambda item: item[1], reverse=True))
            print(multi_num, same_clas_lst[str_ttt])
            multi_num += 1
        label_t, num_t = list(same_clas_lst[str_ttt].keys())[0], same_clas_lst[str_ttt][list(same_clas_lst[str_ttt].keys())[0]]
        for _ in range(num_t):
            clas_data_list.append(str_ttt + "\t" + str(label_t)) 
    # mrc_data_list = shuffle_with_seed(mrc_data_list)
    clas_data_list = shuffle_with_seed(clas_data_list)

    with open(global_path.__dataset_path__ + "/train.txt", "w") as ff:
        ff.write("\n".join(clas_data_list[:int(len(clas_data_list)/10*8)]))
    with open(global_path.__dataset_path__ + "/test.txt", "w") as ff:
        ff.write("\n".join(clas_data_list[int(len(clas_data_list)/10*8):int(len(clas_data_list)/10*9)]))
    with open(global_path.__dataset_path__ + "/valid.txt", "w") as ff:
        ff.write("\n".join(clas_data_list[int(len(clas_data_list)/10*9):]))
    
    print(f1, f2, cnt_label_)


# def dataset_1114():
#     origin_ch_en_path = global_path.__label_migration_result_path__ + "/origin_assets_ch.json"
#     origin_ch_en_dict = json.loads(open(origin_ch_en_path, "r", encoding="utf-8").read())
#     vendor_list, type_list = origin_ch_en_dict["vendor"], origin_ch_en_dict["type"]
  
#     origin_ip_path = global_path.__raw_data_path__ + "iot_assets_ip.json"
#     origin_ip_dict = eval(open(origin_ip_path, "r", encoding="utf-8").read())

#     origin_ip_dict_new = {}
#     for ip in origin_ip_dict:
#         print(ip)
#         assets_tmp = str(origin_ip_dict[ip]['assets'][0])
#         assets_tmp_dict_ = eval(assets_tmp)

#         assets_tmp_dict_new = assets_tmp_dict_
#         vendor_ = assets_tmp_dict_["vendor"]
#         type_ = assets_tmp_dict_["type"]
#         vendor_new = vendor_list[vendor_] if vendor_list[vendor_] != "" else vendor_
#         type_new = type_list[type_] if type_list[type_] != "" else type_
#         assets_tmp_dict_new["vendor"], assets_tmp_dict_new["type"] = vendor_new, type_new

#         origin_ip_dict_new[ip] = origin_ip_dict[ip]
#         origin_ip_dict_new[ip]["assets"] = [assets_tmp_dict_new]
        
#     label_dict_ = open(global_path.__label_migration_result_path__ + "/tmp_label_dict.json", "r").read()
#     label_dict_ = json.loads(label_dict_)
#     gen_mrc_dataset(origin_ip_dict_new, label_dict_)
    
          
if __name__ == "__main__":
    # dataset_1114()
    label_migration()
