from flask import Flask
from flask import url_for
from flask import request
from flask import make_response
from flask import render_template
import requests
import json
import numpy as np
import ml


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
        arr.append(int(v['id']))gi
        arr.append(float(v['rating']['average']) / 2)
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


def to_json(list_data, header=['movieId', 'movieName', 'rank', 'genres']):
    '''把二维list电影数据转换为json，对外提供接口'''
    data = [
        ['大世界', 26954003, 3.75, 'Animation'],
        ['无问西东', 6874741, 0.0, 'Drama|Romance|War'],
        ['迷镇凶案', 2133433, 3.15, 'Comedy|Crime|Mystery'],
        ['大寒', 26392877, 0.0, 'Drama|War'],
        ['无法触碰的爱', 27621048, 0.0, 'Drama|Romance'],
        ['青蛙总动员', 26752895, 1.7, 'Comedy|Animation'],
        ['芒刺', 27601920, 0.0, 'Drama'],
        ['第一夫人', 4849728, 3.3, 'Drama'],
        ['神秘巨星', 26942674, 4.15, 'Drama|Musical'],
        ['公牛历险记', 25846857, 3.75, 'Comedy|Animation|Adventure']
    ]
    try:
        list_data = data
        subjects = []
        for item in list_data:
            for i in range(item):
                subjects.append({header[i]: list_data})

    except BaseException as err:
        return {'count': 0, 'error': err.args[0]}

    return {'subjects': subjects, 'count': len(list_data)}


def get_movie_data(url):
    '''封装了豆瓣api获取所需要的电影数据，返回适合推荐系统训练的二维list'''
    json_data = requests.get(url).json()
    data_list = to_list(json_data)
    return data_list


def get_movie_rs(user_data):
    '''训练某个用户的推荐系统模型'''
    reshape = Reshape()
    x_train, y_train = reshape.reshape_train(user_data)
    rs = MovieRS()
    rs.fit(x_train, y_train)
    return rs


def recommad_movies(rs, recommad_data, n=10):
    '''根据该用户模型和候选电影推荐适合电影'''
    x_test, y_test = reshape.user_matrix(recommad_data)
    return rs.predict(x_test, recommad, n)


@app.route('/', methods=['POST'])
def root():
    '''对外提供推荐系统api'''
    resp = make_response()
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'

    app.logger.info('test')

    if request.method == 'POST':
        return request.form['test']
    return 'GET'


if __name__ == '__main__':
    # app.run('0.0.0.0', 5000)

    # 训练模型
    reshape = ml.Reshape()
    x_train, y_train = reshape.reshape_train()
    rs = ml.MovieRS()
    rs.fit(x_train, y_train)

    in_theaters = 'http://api.douban.com/v2/movie/in_theaters?count=100'
    coming_soon = 'http://api.douban.com/v2/movie/coming_soon?count=100'
