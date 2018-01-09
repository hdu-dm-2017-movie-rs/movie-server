import json
import time


def store(data):
    with open('data.json', 'w') as json_file:
        json_file.write(json.dumps(data))


def load(url):
    with open(url, 'r') as json_file:
        data = json.load(json_file)
        return data


if __name__ == "__main__":
    data = load('./test.json')
    print(data)
