import json
import os


if __name__ == '__main__':
    objs_count = 0
    chunks = [*filter(lambda x: x.startswith('russia_travel_'), os.listdir())]

    for chunk in chunks:
        with open(chunk, 'r') as f:
            try:
                objs_count += len(json.loads(f.read()))
            except:
                pass

    print(len(f'objs_count: {objs_count}'))
