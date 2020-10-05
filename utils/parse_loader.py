import os

from scrapy import cmdline


def execute(group_ids):
    for id_ in group_ids:
        file_name = f'russia_travel_{id_}.json'
        file_path = '../parsed/' + file_name

        os.system(f'rm {file_path}')
        cmdline.execute(f'scrapy crawl russia_travel_landmark -a group_id={id_} -s group={id_} -o {file_path}'.split())


if __name__ == '__main__':
    group_ids = ['5', '124', '122', '41', '103', '2', '62', '123', '10', '125', '101', '102', '104', '3', '1', '6', '121', '61', '4']
    execute(['4'])
