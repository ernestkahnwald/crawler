import sys
import json


if __name__ == '__main__':
    file_path = sys.argv[-1]
    with open(file_path, 'r') as f:
        res = json.loads(f.read())
        print(f'{file_path} items:', len(res))
