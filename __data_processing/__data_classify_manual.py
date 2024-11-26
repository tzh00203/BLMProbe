"""
Classify Response Data by Protocols:
1. Categorize response data based on predefined protocol patterns.
2. Save categorized data into a JSON file.

:input: Combined response data from `sinan_iot_assets.json` and `other_ports.json`.
:output: Categorized data by protocol saved in `iot_assets_pro.json`.
"""

import json
from __utils.__path_util import global_path
from __utils.__save_file_util import save_dict_to_json

# Define paths
ROOT_PATH = global_path.__raw_data_path__
SINAN_IP_DATA_PATH = global_path.__raw_data_path__ + "data_1.json"
SINAN_IP_EXTEND_DATA_PATH = global_path.__raw_data_path__ + "data_2.json"
RESULT_PATH = global_path.__raw_data_path__

# Protocol patterns for classification
PROTOCOL_LIST = [
    "general_ftp.txt", "general_http.txt", "general_rtsp.txt", "general_snmp.txt",
    "general_ssh.txt", "general_telnet.txt",
    "IoT_amqp.txt", "IoT_coap.txt", "IoT_ipp.txt", "IoT_mqtt.txt", "IoT_quagga.txt",
    "IoT_stomp.txt", "IoT_xmpp.txt",
    "private_cisco.txt", "private_cisco_application.txt", "private_citrix_apps.txt",
    "private_citrix_ica.txt", "private_citrix_licensing.txt", "private_dahua.txt",
    "private_dji.txt", "private_hikvision.txt", "private_zebra.txt"
]


def classify_protocol():
    """
    Classify response data based on protocol patterns.
    Saves the result in a JSON file as:
        {
            "protocol1": [{"ip": ip1, "port": port1, "response_data": "data1"}, ...],
            "protocol2": [],
            ...
        }
    """
    iot_assets_pro_dict = {pro.replace(".txt", ""): [] for pro in PROTOCOL_LIST}
    record_list = []

    # Load and combine data
    ori_data = open(SINAN_IP_DATA_PATH, "r", encoding="utf-8").readlines()
    extend_data = open(SINAN_IP_EXTEND_DATA_PATH, "r", encoding="utf-8").readlines()
    all_data = ori_data + extend_data

    for line in all_data:
        json_tmp = json.loads(line)
        ip = json_tmp["ip"]
        port = json_tmp["port"]
        protocol_ori = json_tmp["protocol"]
        header = json_tmp["header"]
        body = json_tmp["body"]
        res_data = header + body

        # Avoid duplicate records
        record_key = f"{ip}:{port}"
        if record_key in record_list:
            continue
        record_list.append(record_key)

        # Classify data by protocol
        for pro in PROTOCOL_LIST:
            protocol_name = pro.replace(".txt", "")
            if protocol_name.split("_")[-1] in protocol_ori.lower() or protocol_ori.lower() in protocol_name.split("_")[-1]:
                iot_assets_pro_dict[protocol_name].append({
                    "ip": ip,
                    "port": port,
                    "response_data": res_data
                })

    # Save results
    save_dict_to_json(RESULT_PATH + "iot_assets_pro.json", iot_assets_pro_dict)
    print(f"Classification completed. Results saved to {RESULT_PATH}iot_assets_pro.json")


if __name__ == "__main__":
    classify_protocol()
