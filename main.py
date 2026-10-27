from __data_processing.__data_format_classifier import calc
from __data_processing.__data_search_query import search_query
from __data_processing.__crawler.__crawler_concurrent import Crawler
from __data_processing.__two_roles_agent.__agent_run import AgentLabelingWorkflow


def data_processing(input_path):
    crawler = Crawler(mode='Google')
    agent_runner = AgentLabelingWorkflow(explore_mode='gpt', referee_mode='gpt')

    calc(input_path=input_path)
    search_query() 
    crawler.run_crawler()
    agent_runner.run_agent()

if __name__ == '__main__':
    import argparse
    default_path = "./data/dataset/labeled_dataset_without_label_migration_sample.json"

    parser = argparse.ArgumentParser(description="BLMProbe Label Migration Pipeline")
    parser.add_argument("--input", type=str, default=default_path,
                        help=f"Path to input JSON file (default: {default_path})")

    args = parser.parse_args()
    input_ = args.input
 
    data_processing(input_path=input_)
    
    from __label_migration.__label_migration import label_migration
    # from __classification_model.__train_bert import train_bert
    label_migration(origin_ip_path=input_, mode="no_train")
    # train_bert()