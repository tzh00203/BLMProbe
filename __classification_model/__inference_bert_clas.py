import sys
import os
import json
import re
import torch
from __data_processing.__data_sanitization import sanitization_string
from __train_bert_clas import Model, Config
from __generate_util import loading_animation
from __label_migration.__label_migration_utils import split_string_by_word_count
from __utils.__path_util import global_path
from __utils.__save_file_util import save_dict_to_json

# Load classification dictionary
with open(global_path.__label_dict_path__, 'r', encoding='utf-8') as file:
    clas_dict = {value: key for key, value in json.load(file).items()}


# Load or initialize TFIDF data
def load_tfidf_data(tfidf_path):
    if os.path.exists(tfidf_path):
        tfidf_dataset = json.load(open(tfidf_path, 'r'))
        return (
            tfidf_dataset["tfidf_corpus"],
            tfidf_dataset["tfidf_corpus_id"],
            len(tfidf_dataset["tfidf_corpus_id"]) + 1,
        )
    else:
        iot_assets_ip_new_path = global_path.__label_migration_result_path__ + "tmp_iot_assets_ip_new.json"
        iot_assets_ip_new_dict = eval(open(iot_assets_ip_new_path, "r", encoding="utf-8").read())
        
        tfidf_corpus, tfidf_corpus_id, corpus_id = [], [], 1
        response_set = set()

        for ip_data in iot_assets_ip_new_dict.values():
            for response in ip_data["response_data"]:
                sanitized_response = sanitization_string(response)
                if sanitized_response not in response_set:
                    response_set.add(sanitized_response)
                    tfidf_corpus.append(sanitized_response)
                    tfidf_corpus_id.append(corpus_id)
                    corpus_id += 1

        save_dict_to_json(tfidf_path, {"tfidf_corpus": tfidf_corpus, "tfidf_corpus_id": tfidf_corpus_id})
        return tfidf_corpus, tfidf_corpus_id, corpus_id


tfidf_path = "./tfidf_data.json"
tfidf_corpus, tfidf_corpus_id, corpus_id = load_tfidf_data(tfidf_path)


# Generate a fingerprint for the given response
def gen_fingerprint(response_tt, vendor, type_, product):
    from _3_data_processing._3_data_TFIDF_util import tfidf_calc
    tfidf_corpus.append(response_tt)
    tfidf_corpus_id.append(corpus_id)
    tfidf_words_dict = tfidf_calc(tfidf_corpus, tfidf_corpus_id)

    return {
        "fingerprint": tfidf_words_dict[corpus_id],
        "assets": {"vendor": vendor, "type": type_, "product": product},
    }


# Perform inference on the given response data
def inference(response_data):
    sanitized_response = sanitization_string(response_data)
    response_tt = sanitized_response.replace("\t", " ")

    # Load model and config
    config = Config('dataset')
    model = Model(config=config).to(config.device)
    model.load_state_dict(torch.load('./datasetbertrnn.cuda.protocol.extend.ckpt', map_location=config.device))
    model.eval()

    res_list = split_string_by_word_count(response_tt.strip())
    if len(res_list) > 1:
        label_counts = {}
        for res_text in res_list:
            label, _, _, _ = inference_str(res_text, model, config)
            label_counts[label] = label_counts.get(label, 0) + 1

        label = max(label_counts, key=label_counts.get)
        assets_dict = eval(clas_dict[label[1:-1]])
    else:
        label, vendor, type_, product = inference_str(res_list[0], model, config)

    fingerprint = gen_fingerprint(response_tt, vendor, type_, product)
    print(f"Sanitized Response: [{response_tt}]")
    print(f"Fingerprint: {fingerprint['fingerprint']}")
    print(f"Inference Result:\n Label: {label}\n Vendor: [{vendor}]\n Type: [{type_}]\n Product: [{product}]")


# Inference for a single string
def inference_str(input_str, model, config):
    input_ids, seq_len, mask = preprocess_text(input_str, config)
    with torch.no_grad():
        outputs = model((input_ids, seq_len, mask))
        predict_label = str(torch.max(outputs.data, 1)[1].cpu().numpy())
        assets_dict = eval(clas_dict[predict_label[1:-1]])
        return predict_label, assets_dict["vendor"], assets_dict["type"], assets_dict["product"]


# Preprocess the input text for BERT
def preprocess_text(text, config):
    text = text.strip()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"(\b\w+'[a-z]{1,2}\b)", lambda m: m.group(0).replace("'", " "), text)  # Handle contractions

    token = ['[CLS]'] + config.tokenizer.tokenize(text)
    seq_len = len(token)
    token_ids = config.tokenizer.convert_tokens_to_ids(token)

    if len(token_ids) < config.pad_size:
        mask = [1] * len(token_ids) + [0] * (config.pad_size - len(token_ids))
        token_ids += [0] * (config.pad_size - len(token_ids))
    else:
        mask = [1] * config.pad_size
        token_ids = token_ids[:config.pad_size]
        seq_len = config.pad_size

    return (
        torch.LongTensor([token_ids]).to(config.device),
        torch.LongTensor([seq_len]).to(config.device),
        torch.LongTensor([mask]).to(config.device),
    )


if __name__ == "__main__":
    response_data = """
        RAW DATA: \"0\\x82\\x01%\\x02\\x01\\x00\\x04\\x06public\\xa2\\x82\\x01\\x16\\x02\\x02e(\\x02\\x01\\x00\\x02\\x01\\x000\\x82\\x01\\b0\\x82\\x01\\x04\\x06\\b+\\x06\\x01\\x02\\x01\\x01\\x01\\x00\\x04\\x81\\xf\"
    """
    inference(response_data)
