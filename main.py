import json
from copy import deepcopy
from flask import Flask
from flask import url_for
from flask import request
from flask import make_response
from flask import render_template
import requests
import numpy as np
# import ml


app = Flask(__name__)
in_theaters = 'http://api.douban.com/v2/movie/in_theaters?count=100'
coming_soon = 'http://api.douban.com/v2/movie/coming_soon?count=100'


def transform(genre, lang='cn'):
    '''电影类型的中英文互转'''
    data = {
        'Action': '动作',
        'Adventure': '冒险',
        'Animation': '动画',
        'Children\'s': '儿童',
        'Comedy': '喜剧',
        'Crime': '犯罪',
        'Documentary': '纪录片',
        'Drama': '剧情',
        'Fantasy': '魔幻',
        'Film-Noir': '黑色电影',
        'Horror': '恐怖',
        'Musical': '音乐',
        'Mystery': '悬疑',
        'Romance': '爱情',
        'Sci-Fi': '科幻',
        'Thriller': '惊悚',
        'War': '战争',
        'Western': '西部',
        '(no genres listed)': None
    }

    if lang == 'cn':
        return data.get(genre)

    # en
    for k, v in data.items():
        if genre == v:
            return k

    return '(no genres listed)'


def to_list(json_data):
    '''把豆瓣电影类型格式为适合推荐系统的数据结构二维list，过滤到无类型电影，并把电影类型转为英文'''
    data = []
    for v in json_data['subjects']:
        arr = []
        arr.append(v['title'])
        arr.append(int(v['id']))
        arr.append(float(v['rating']['average']) / 2)
        # arr.append(v['images']['large'])
        str = ''
        for genre in v['genres']:
            genre = transform(genre, 'en')
            if genre is not None and genre != '(no genres listed)':
                str += genre
                str += '|'
        str = str[:-1]
        if str == '':
            continue
        arr.append(str)
        data.append(arr)

    return data


def to_json(list_data, header=['movieName', 'movieId', 'rating', 'genres', 'img', 'summary']):
    '''把二维list电影数据转换为json，对外提供接口'''
    try:
        # list_data = data
        subjects = []
        for item in list_data:
            obj = {}
            for i in range(len(item)):
                obj[header[i]] = item[i]
            subjects.append(obj)

    except BaseException as err:
        return {'count': 0, 'error': err.args[0]}

    return {'subjects': subjects, 'count': len(list_data)}


def get_movie_data(urls):
    '''封装了豆瓣api获取所需要的电影数据，返回适合推荐系统训练的二维list'''
    # movies_data = []
    # for url in urls:
    #     json_data = requests.get(url).json()
    #     to_json
    return 


# def get_movie_rs(user_data):
#     '''训练某个用户的推荐系统模型'''
#     reshape = ml.Reshape()
#     x_train, y_train = reshape.reshape_train(user_data)
#     rs = ml.MovieRS()
#     # 训练用户画像
#     rs.fit(x_train, y_train)
#     return rs


# def get_recommend_data(rs, recommend, n=10):
#     '''从候选电影中给该用户推荐电影'''
#     reshape = ml.Reshape()
#     x_test, y_test = reshape.user_matrix(recommend)
#     movies = rs.predict(x_test, recommend, n)

#     # 查找movies相关的电影数据

#     return movies


def recommend_movies(rs, recommend_data, n=10):
    '''根据该用户模型和候选电影推荐适合电影'''
    # x_test, y_test = reshape.user_matrix(recommad_data)
    # return rs.predict(x_test, recommad, n)
    pass


test_user_data = [['21', '5350027', '3.45', 'Drama|Mystery'],
                  ['22', '26797419', '3.1', 'Comedy'],
                  ['23', '26654146', '2.7', 'Drama'],
                  ['24', '20495023', '4.55', 'Comedy|Animation|Adventure'],
                  ['25', '26340419', '4.15', 'Comedy|Animation'],
                  ['26', '26661191', '2.4', 'Action'],
                  ['27', '26761416', '4.3', 'Drama']]

test_recommend_data = [['1', '26662193', '3.1', 'Comedy'],
                       ['2', '26862829', '3.9', 'Drama|War'],
                       ['3', '26966580', '2.4', 'Comedy'],
                       ['4', '5350027', '3.45', 'Drama|Mystery'],
                       ['5', '26797419', '3.1', 'Comedy'],
                       ['6', '26654146', '2.7', 'Drama'],
                       ['7', '20495023', '4.55', 'Comedy|Animation|Adventure'],
                       ['8', '26340419', '4.15', 'Comedy|Animation'],
                       ['9', '26774722', '3.05', 'Action|Crime|Mystery'],
                       ['10', '26729868', '2.5', 'Drama|Action|Sci-Fi'],
                       ['11', '26887161', '0.0', "Children's|Animation"],
                       ['12', '25837262', '4.3', 'Drama|Animation'],
                       ['13', '27193475', '0.0', "Children's|Animation"],
                       ['14', '26661191', '2.4', 'Action'],
                       ['15', '26761416', '4.3', 'Drama']]

test_recommend_data = [
    ['大世界', 26954003, 3.75, 'Animation', 'http://www.baidu.com', '简介测试'],
    ['无问西东', 6874741, 0.0, 'Drama|Romance|War', 'http://www.baidu.com', '简介测试'],
    ['迷镇凶案', 2133433, 3.15, 'Comedy|Crime|Mystery', 'http://www.baidu.com', '简介测试'],
    ['大寒', 26392877, 0.0, 'Drama|War', 'http://www.baidu.com', '简介测试'],
    ['无法触碰的爱', 27621048, 0.0, 'Drama|Romance', 'http://www.baidu.com', '简介测试'],
    ['青蛙总动员', 26752895, 1.7, 'Comedy|Animation', 'http://www.baidu.com', '简介测试'],
    ['芒刺', 27601920, 0.0, 'Drama', 'http://www.baidu.com', '简介测试'],
    ['第一夫人', 4849728, 3.3, 'Drama', 'http://www.baidu.com', '简介测试'],
    ['神秘巨星', 26942674, 4.15, 'Drama|Musical', 'http://www.baidu.com', '简介测试'],
    ['公牛历险记', 25846857, 3.75, 'Comedy|Animation|Adventure', 'http://www.baidu.com', '简介测试']
]


@app.route('/api', methods=['POST'])
def root():
    '''对外提供推荐系统api'''
    user_data = deepcopy(test_user_data)
    recommend_data = deepcopy(test_recommend_data)

    # 推荐
    rs = get_movie_rs(user_data)
    movies = get_recommend_data(rs, recommend_data, n=10)
    print(movies)

    resp = make_response(json.dumps(to_json(movies, header=['movieName', 'movieId', 'rating', 'genres', 'img', 'summary'])))
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


@app.route('/test', methods=['GET', 'POST'])
def test():
    '''测试用api，返回静态数据'''
    resp = make_response(json.dumps(to_json(test_recommend_data, header=['movieName', 'movieId', 'rating', 'genres', 'img', 'summary'])))
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
    # user_data = deepcopy(test_user_data)
    # recommend_data = deepcopy(test_recommend_data)

    # 推荐
    # rs = get_movie_rs(user_data)
    # movies = get_recommend_data(rs, recommend_data, n=10)
    # print(movies)

    # data = json.dumps(to_json(movies, header=['movieName', 'movieId', 'rating', 'genres', 'img', 'summary']))
    pass