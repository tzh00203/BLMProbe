from pprint import pprint

import requests
import json
import tiktoken
import re

in_num_vendor_name_list = ["h3c", "h264dvr", "netdvrv3"]

import random


def gen_train_test_dev(mrc_data_list):
    """
    mrc_tmp = {
                "ip": ip_,
                "context": "", "keywords": [],
                "end_position": [],
                "entity_label": "",
                "impossible": True,
                "qas_id": "",
                "query": "",
                "span_position": [],
                "start_position": []
            }
    """
    train_, test_, dev_ = [], [], []
    for data_list_tmp in [ 
                          [train_, mrc_data_list[:int(len(mrc_data_list)/4*3)]], 
                          [test_, mrc_data_list[int(len(mrc_data_list)/4*3):int(len(mrc_data_list)/8*7)]], 
                          [dev_, mrc_data_list[int(len(mrc_data_list)/8*7):]]
                          ]:
        dd, ll = data_list_tmp[0], data_list_tmp[1]
        index_ = 0
        for ll_ in ll:
            for mrc_tmp in ll_:
                mrc_tmp["qas_id"] = str(index_) + "." + mrc_tmp["qas_id"].split(".")[-1]
                dd.append(mrc_tmp)
            index_ += 1
    return train_, test_, dev_


def get_binary(str_):
    
    # str_ = repr(str_).replace("\\", "\\\\")
    # binary_parts = [ "".join(substr_) for substr_ in re.findall(r'(\\\\x[0-9a-fA-F]{2})(\\\\x[0-9a-fA-F]{2})(\\\\x[0-9a-fA-F]{2})(\\\\x[0-9a-fA-F]{2})(\\\\x[0-9a-fA-F]{2})', str_)] 
    # return " ".join(binary_parts)
    ss = (repr(str_))
    ss = ss.replace("\\\\", "\\")
    # print(ss)
    # print(len(ss))
    binary_parts =  re.finditer(r'(\\x[0-9a-fA-F]{2})', ss)

    binary_part_list = []
    binary_index_list = []
    groups = []
    groups_binary = []
    for match in binary_parts:
        # print(match)
        # print(repr(match))
        binary_part = match.group()
        index_start = match.start()
        index_end = match.end() - 1
        binary_index_list.append(index_start)
        binary_part_list.append(binary_part)
        # print(binary_part, index_start)
        
    # print(binary_index_list, binary_part_list)
    # with open("./caogaozhi.output", "w", encoding="utf-8") as f:
    #     a = "\\x00\\x00\\x00\\x00\\x00 \\x00\\x00\\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00firmware ce2940 mikrotik"
    #     a = a.replace("\\", "\\\\")
    #     print(a)
    #     f.write(a)

    start_flag = False
    for num_index in binary_index_list:
        found_group = False
        if not start_flag:
            groups.append([num_index])
            groups_binary.append([binary_part_list[binary_index_list.index(num_index)]])
            start_flag = True
            continue
        if abs(num_index - groups[-1][-1]) == 4 :
            groups[-1].append(num_index)
            groups_binary[-1].append(binary_part_list[binary_index_list.index(num_index)])
            found_group = True
        
        if not found_group:
            groups.append([num_index])
            groups_binary.append([binary_part_list[binary_index_list.index(num_index)]])
    # print(groups)
    binary_parts_result = [ "".join(group_binary) for group_binary in groups_binary ]
    # print(binary_parts_result)
    result_string = ""
    for sss in binary_parts_result:
        if len(sss) <= 5:
            continue
        result_string += sss + " "
    return result_string.strip()

# print(get_binary("@\u0014Pg\fМ \u0001\u0000\u0000\u0000\u0000dСx\u0001ИЫ\u0000\u0000\u0000\u0000"))
    
def shuffle_with_seed(original_list, seed=32):
    # 复制原列表以避免修改原列表
    shuffled_list = original_list[:]
    
    # 设置随机种子
    random.seed(seed)
    
    # 打乱列表
    random.shuffle(shuffled_list)
    
    return shuffled_list


def label_name_unify(ori_name, openai_name):
    ori_name, openai_name = ori_name.lower(), openai_name.lower()
    if openai_name in ori_name or openai_name == "null":
        return False
    elif ori_name in openai_name:
        return True

    for num_vendor in in_num_vendor_name_list:
        ori_name = ori_name.replace(num_vendor, "")
        openai_name = openai_name.replace(num_vendor, "")

    num_in_ori = bool(re.search(r'\d', ori_name))
    num_in_openai = bool(re.search(r'\d', openai_name))
    if num_in_ori == False and num_in_openai == True:
        return True
    if num_in_ori == True and num_in_openai == True:
        return False
    if num_in_ori == True and num_in_openai == False:
        return False
    return False


def mark_label_in_context(str_, keywords_list):
    """
    mrc_tmp = {
                "ip": ip_,
                "context": "", "keywords": [],
                "end_position": [],
                "entity_label": "",
                "impossible": True,
                "qas_id": "",
                "query": "",
                "span_position": [],
                "start_position": []
            }
    """
    print(keywords_list, str_)
    start_position, end_position, span_position = [], [], []
    for word_index in range(len(str_.split(" "))):
        word_ = str_.split(" ")[word_index]
        if word_ in keywords_list:
             start_position.append(word_index)
             end_position.append(word_index)
             span_position.append(str(word_index)+";"+str(word_index))
    return start_position, end_position, span_position
    
    
def split_string_by_word_count(input_string, max_words=30):
    # Step 1: Split the string into words
    words = input_string.split()
    
    # Step 2: Divide the list of words into chunks of max_words
    chunks = [words[i:i + max_words] for i in range(0, len(words), max_words)]
    
    # Step 3: Join the chunks back into strings
    result = [' '.join(chunk) for chunk in chunks]
    
    return result

    

def count_chat_tokens(messages, model="gpt-3.5-turbo"):
    if model.startswith("gpt-4"):
        encoding = tiktoken.encoding_for_model("gpt-4")
    elif model.startswith("gpt-3.5"):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    else:
        raise ValueError("Unsupported model")

    tokens_per_message = 4
    tokens_per_system_message = 1
    total_tokens = 0
    message_tokens = []

    for message in messages:
        tokens = encoding.encode(message["content"])
        total_tokens += tokens_per_message + len(tokens)
        if message["role"] == "system":
            total_tokens += tokens_per_system_message
        message_tokens.append((message, tokens))

    return total_tokens, message_tokens


def truncate_chat_messages(messages, max_tokens, model="gpt-3.5-turbo"):
    total_tokens, message_tokens = count_chat_tokens(messages, model)
    if total_tokens <= max_tokens:
        return messages

    encoding = tiktoken.encoding_for_model(model)
    truncated_messages = []
    truncated_total_tokens = 0

    for message, tokens in message_tokens:
        if truncated_total_tokens + len(tokens) + 4 > max_tokens:
            remaining_tokens = max_tokens - truncated_total_tokens - 4
            tokens = tokens[:remaining_tokens]
            message["content"] = encoding.decode(tokens)
            truncated_messages.append(message)
            break
        else:
            truncated_messages.append(message)
            truncated_total_tokens += len(tokens) + 4

    return truncated_messages


def openai_api_request(user_input=None):
    """
    使用openai api进行标签提取
    :param user_input:
    :return:
    """
    if user_input is None:
        user_input = {
            "uri": "https://wiki.mikrotik.com/wiki/Manual:Tools/Fetch/router",
            "title": "Manual:Tools/Fetch - MikroTik Wiki/router",
            "web_info": "Manual:Tools/Fetch - MikroTik Wiki Manual:Tools/Fetch From MikroTik Wiki < Manual:Tools Jump to navigation Jump to search Applies to RouterOS: v6 + Contents 1 Summary 2 Properties 3 Examples 3.1 Downloading files to the router 3.2 Sending information to a remote host 3.3 Return value to a variable 3.4 SFTP Summary Sub-menu: /tool fetch Standards: Fetch is one of the console tools in Mikrotik RouterOS. It is used to copy files to/from a network device via HTTP, FTP or SFTP (Support for SFTP added on v6.45), it can also be used to sent POST/GET requests and send any kind of data to a remote server. HTTPS protocol is supported; by default no certificate checks are made, but setting check-certificate to yes enables trust chain validation from local certificate store. Properties Property Description address (string; Default: ) IP address of the device to copy file from. as-value (set | not-set; Default: not-set) Store the output in a variable, should be used with the output property. ascii (yes | no; Default: no) check-certificate (yes | no; Default: no) Enables trust chain validation from local certificate store. dst-path (string; Default: ) Destination filename and path host (string; Default: ) Domain name or virtual domain name (if used on web-site, from which you want to copy information). For example, address=wiki.mikrotik.com host=forum.mikrotik.com In this example the resolved ip address is the same (66.228.113.27), but hosts are different. http-method (|delete|get|post|put; Default: get) the HTTP method to use http-data (string; Default: ) the data, that is going to be send, when using PUT or POST methods http-header-field (string; Default: *empty*) list of all header fields and their values, in the form of http-header-field=h1:fff,h2:yyy keep-result (yes | no; Default: yes) If yes, creates an input file. mode (ftp|http|tftp {!} https; Default: http) Choose the protocol of connection - http, https , ftp or tftp. output (none|file|user; Default: file) Sets where to store the downloaded data. none - do not store downloaded data file - store downloaded data in a file user - store downloaded data in the data variable password (string; Default: anonymous) Password, which is needed for authentication to the remote device. port (integer; Default: ) Connection port. src-path (string; Default: ) Title of the remote file you need to copy. upload (yes | no; Default: no) If enabled then fetch will be used to upload file to remote server. Requires src-path and dst-path parameters to be set. url (string; Default: ) URL pointing to file. Can be used instead of address and src-path parameters. user (string; Default: anonymous) User name, which is needed for authentication to the remote device. Examples Downloading files to the router The following example shows how to copy the file with filename \"conf.rsc\" from a device with ip address 192.168.88.2 by FTP protocol and save it as file with filename \"123.rsc\". User and password are needed to login into the device. [admin@mt-test] /tool> fetch address=192.168.88.2 src-path=conf.rsc \\ user=admin mode=ftp password=123 dst-path=123.rsc port=21 \\ host=\"\" keep-result=yes Example to upload file to other router: [admin@mt-test] /tool> fetch address=192.168.88.2 src-path=conf.rsc \\ user=admin mode=ftp password=123 dst-path=123.rsc upload=yes Another file download example that demonstrates the usage of url property. [admin@test_host] /> /tool fetch url=\"http://www.mikrotik.com/img/netaddresses2.pdf\" mode=http status: finished [admin@test_host] /> /file print # NAME TYPE SIZE CREATION-TIME ... 5 netaddresses2.pdf .pdf file 11547 jun/01/2010 11:59:51 Sending information to a remote host It is possible to use HTTP POST request to send information to a remote server, that is prepared to accept it. In the following example, we send geographic coordinates to a PHP page: /tool fetch http-method=post http-header-field=\"Content-Type: application/json\" http-data=\"{\\\"lat\\\":\\\"56.12\\\",\\\"lon\\\":\\\"25.12\\\"}\" url=\"http://testserver.lv/index.php\" Of course, you can use Fetch with scripts and fill the above command with variables from the RouterOS GPS menu. Return value to a variable Since RouterOS v6.43 it is possible to save the result of fetch command to a variable. For example, it is possible to trigger a certain action based on the result that a HTTP page returns. You can find a very simple example below that disables ether2 whenever a PHP page returns \"0\": { :local result [/tool fetch url=http://10.0.0.1/disable_ether2.php as-value output=user]; :if ($result->\"status\" = \"finished\") do={ :if ($result->\"data\" = \"0\") do={ /interface ethernet set ether2 disabled=yes; } else={ /interface ethernet set ether2 disabled=no; } } } SFTP Since 6.45beta50 /tool fetch support SFTP (SSH File Transfer Protocol) protocol. [admin@MikroTik] > /tool fetch url=\"sftp://10.155.126.200/home/x86/Desktop/50MB.zip\" user=x86 password=root dst-path=disk1 status: downloading downloaded: 1048KiB total: 51200KiB duration: 6s -- [Q quit|D dump|C-z pause] [ Top | Back to Content ] Retrieved from \"https://wiki.mikrotik.com/index.php?title=Manual:Tools/Fetch&oldid=34320\" Categories: ManualTools Navigation menu Personal tools Log in Namespaces ManualDiscussion English expanded collapsed Views ReadView sourceView history More expanded collapsed Search Navigation Main PageRecent changes Tools What links hereRelated changesSpecial pagesPrintable versionPermanent linkPage information This page was last edited on 21 January 2021, at 11:26. Privacy policy About MikroTik Wiki Disclaimers"
        }
        
        # user_input = {
        #      "uri": "https://wiki.mikrotik.com/wiki/Manual:Tools/Fetch/router",
        #     "title": "Manual:Tools/Fetch - MikroTik Wiki/router",
        #     "web_info": "Manual:Tools/Fetch - MikroTik Wiki Manual:Tools/Fetch From MikroTik Wiki < Manual:Tools Jump to navigation Jump to search Applies to RouterOS: v6 + Contents 1 Summary 2 Properties 3 Examples 3.1 Downloading files to the router 3.2 Sending information to a remote host 3.3 Return value to a variable 3.4 SFTP Summary Sub-menu: /tool fetch Standards: Fetch is one of the console tools in Mikrotik RouterOS. It is used to copy files to/from a network device via HTTP, FTP or SFTP (Support for SFTP added on v6.45), it can also be used to sent POST/GET requests and send any kind of data to a remote server. HTTPS protocol is supported; by default no certificate checks are made, but setting check-certificate to yes enables trust chain validation from local certificate store. Properties Property Description address (string; Default: ) IP address of the device to copy file from. as-value (set | not-set; Default: not-set) Store the output in a variable, should be used with the output property. ascii (yes | no; Default: no) check-certificate (yes | no; Default: no) Enables trust chain validation from local certificate store. dst-path (string; Default: ) Destination filename and path host (string; Default: ) Domain name or virtual domain name (if used on web-site, from which you want to copy information). For example, address=wiki.mikrotik.com host=forum.mikrotik.com In this example the resolved ip address is the same (66.228.113.27), but hosts are different. http-method (|delete|get|post|put; Default: get) the HTTP method to use http-data (string; Default: ) the data, that is going to be send, when using PUT or POST methods http-header-field (string; Default: *empty*) list of all header fields and their values, in the form of http-header-field=h1:fff,h2:yyy keep-result (yes | no; Default: yes) If yes, creates an input file. mode (ftp|http|tftp {!} https; Default: http) Choose the protocol of connection - http, https , ftp or tftp. output (none|file|user; Default: file) Sets where to store the downloaded data. none - do not store downloaded data file - store downloaded data in a file user - store downloaded data in the data variable password (string; Default: anonymous) Password, which is needed for authentication to the remote device. port (integer; Default: ) Connection port. src-path (string; Default: ) Title of the remote file you need to copy. upload (yes | no; Default: no) If enabled then fetch will be used to upload file to remote server. Requires src-path and dst-path parameters to be set. url (string; Default: ) URL pointing to file. Can be used instead of address and src-path parameters. user (string; Default: anonymous) User name, which is needed for authentication to the remote device. Examples Downloading files to the router The following example shows how to copy the file with filename \"conf.rsc\" from a device with ip address 192.168.88.2 by FTP protocol and save it as file with filename \"123.rsc\". User and password are needed to login into the device. [admin@mt-test] /tool> fetch address=192.168.88.2 src-path=conf.rsc \\ user=admin mode=ftp password=123 dst-path=123.rsc port=21 \\ host=\"\" keep-result=yes Example to upload file to other router: [admin@mt-test] /tool> fetch address=192.168.88.2 src-path=conf.rsc \\ user=admin mode=ftp password=123 dst-path=123.rsc upload=yes Another file download example that demonstrates the usage of url property. [admin@test_host] /> /tool fetch url=\"http://www.mikrotik.com/img/netaddresses2.pdf\" mode=http status: finished [admin@test_host] /> /file print # NAME TYPE SIZE CREATION-TIME ... 5 netaddresses2.pdf .pdf file 11547 jun/01/2010 11:59:51 Sending information to a remote host It is possible to use HTTP POST request to send information to a remote server, that is prepared to accept it. In the following example, we send geographic coordinates to a PHP page: /tool fetch http-method=post http-header-field=\"Content-Type: application/json\" http-data=\"{\\\"lat\\\":\\\"56.12\\\",\\\"lon\\\":\\\"25.12\\\"}\" url=\"http://testserver.lv/index.php\" Of course, you can use Fetch with scripts and fill the above command with variables from the RouterOS GPS menu. Return value to a variable Since RouterOS v6.43 it is possible to save the result of fetch command to a variable. For example, it is possible to trigger a certain action based on the result that a HTTP page returns. You can find a very simple example below that disables ether2 whenever a PHP page returns \"0\": { :local result [/tool fetch url=http://10.0.0.1/disable_ether2.php as-value output=user]; :if ($result->\"status\" = \"finished\") do={ :if ($result->\"data\" = \"0\") do={ /interface ethernet set ether2 disabled=yes; } else={ /interface ethernet set ether2 disabled=no; } } } SFTP Since 6.45beta50 /tool fetch support SFTP (SSH File Transfer Protocol) protocol. [admin@MikroTik] > /tool fetch url=\"sftp://10.155.126.200/home/x86/Desktop/50MB.zip\" user=x86 password=root dst-path=disk1 status: downloading downloaded: 1048KiB total: 51200KiB duration: 6s -- [Q quit|D dump|C-z pause] [ Top | Back to Content ] Retrieved from \"https://wiki.mikrotik.com/index.php?title=Manual:Tools/Fetch&oldid=34320\" Categories: ManualTools Navigation menu Personal tools Log in Namespaces ManualDiscussion English expanded collapsed Views ReadView sourceView history More expanded collapsed Search Navigation Main PageRecent changes Tools What links hereRelated changesSpecial pagesPrintable versionPermanent linkPage information This page was last edited on 21 January 2021, at 11:26. Privacy policy About MikroTik Wiki Disclaimers"
        # }

    aaa = 'your_key'

    url = 'https://api.openai.com/v1/chat/completions'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {aaa}',
    }

    data = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content":
                    """
               You are a WEB page entity name extractor. The user will input the basic information of the WEB page 
               related (including the uri link of the web page, the title of the page, and the text 
               information of the page). You need to determine whether the information input by the user is related to a 
               certain network device. The output information contains three dimensions: device vendor name, device 
               type, device model information
    
                User input: dictionary type {uri, title, web_info}
                Your answer output format:
                {vendor: "", type: "", product: ""}
                Attention:
                1. If the vendor or device type is unknown, the attribute value is "null".
                2. The extracted attribute value must come from the attribute value in the dictionary information ({uri, title, web_info}) input by the user
                3. If the input information does not contain network device information, the attribute value corresponding to each attribute in the dictionary is null. (The vendor and type are irrelevant to the network device.)
                4. If the model information is displayed, determine whether to describe the device based on the context. If more than one series name or model number is included and cannot be determined to be unique, the product property value is empty.
                5. Your answer only needs to be given a dictionary of results and does not need to contain additional strings
                """
            },
            {
                "role": "user",
                "content": f"user input: {user_input}",
            }
        ]
    }

    max_tokens = 4096

    truncated_messages = truncate_chat_messages(data["messages"], max_tokens, data["model"])
    data["messages"] = truncated_messages
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            res_json = response.json()
            openai_labels_dict = eval(res_json["choices"][0]["message"]["content"])
            print(openai_labels_dict)
            return openai_labels_dict
        else:
            null_result = "bad response"
            return null_result
    except:
        return "bad response"


if __name__ == "__main__":
    print(openai_api_request())