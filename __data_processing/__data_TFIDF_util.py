import math

key_words_num = 5


class EXPLANATION:

    """
        corpus = [
            "What is the weather like today",
            "what is for dinner tonight",
            "this is question worth pondering",
            "it is a beautiful day today",
            " ",
            "",
            "it is a beautiful day Today today today today today today today today SX-XA-IDC-DNS-RECUR-4.163"
        ]
        corpus_id = [
            1,
            3,
            5,
            7,
            8,
            9,
            10
        ]
        :return: { id1: [ip1's key words], id2: [ip2's key words], ...}
    """


class TfIdf:
    def __init__(self):
        self.num_docs = 0
        self.vocab = {}

    def add_corpus(self, corpus):
        self._merge_corpus(corpus)

        tfidf_list = []
        for sentence in corpus:
            tfidf_list.append(self.get_tfidf(sentence))
        return tfidf_list

    def _merge_corpus(self, corpus):
        """
        统计语料库，输出词表，并统计包含每个词的文档数。
        """
        self.num_docs = len(corpus)
        for sentence in corpus:
            words = sentence.strip().split()
            words = set(words)
            for word in words:
                self.vocab[word] = self.vocab.get(word, 0.0) + 1.0

    def _get_idf(self, term):
        """
        计算 IDF 值
        """
        return math.log(self.num_docs / (self.vocab.get(term, 0.0) + 1.0))

    def get_tfidf(self, sentence):
        tfidf = {}
        terms = sentence.strip().split()
        terms_set = set(terms)
        num_terms = len(terms)
        for term in terms_set:
            # 计算 TF 值
            tf = float(terms.count(term)) / num_terms
            # 计算 IDF 值，在实际实现时，可以提前将所有词的 IDF 提前计算好，然后直接使用。
            idf = self._get_idf(term)
            # 计算 TF-IDF 值
            tfidf[term] = tf * idf
        return tfidf


corpus_ = [
    "What is the weather like today",
    "what is for dinner tonight",
    "this is question worth pondering",
    "it is a beautiful day today",
    " ",
    "",
    "it is a beautiful day Today today today today today today today today SX-XA-IDC-DNS-RECUR-4.163"
]

corpus_id_ = [
    1,
    3,
    5,
    7,
    9,
    13,
    14
]


def tfidf_calc(corpus, corpus_id):

    tfidf = TfIdf()
    tfidf_values = tfidf.add_corpus(corpus)

    str_list = {}
    for index in range(len(tfidf_values)):
        id_tmp = corpus_id[index]
        str_list[id_tmp] = {}
        for word, value in tfidf_values[index].items():
            if value not in str_list[id_tmp]:
                str_list[id_tmp][value] = [word]
            else:
                str_list[id_tmp][value].append(word)

    result_list = {}
    # print(str_list)
    for id_ in str_list:
        id_key_list = []
        sort_words = sorted(str_list[id_].items(), reverse=True)
        # [(0.7219900393862153, ['account']), (0.28633233321488805, ['draytek', 'vendor', 'vigor', 'hostname', 'pptp']), (0.26229631679778237, ['firmware'])]
        for value, list_tmp in sort_words:
            id_key_list += list_tmp
            if len(id_key_list) >= key_words_num:
                break
        result_list[id_] = id_key_list


    return result_list
