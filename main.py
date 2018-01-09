import json
from flask import Flask
from flask import url_for
from flask import request
from flask import make_response
from flask import render_template
from flask import jsonify
import requests
import numpy as np
import ml


app = Flask(__name__)
in_theaters = 'http://api.douban.com/v2/movie/in_theaters?count=100'
coming_soon = 'http://api.douban.com/v2/movie/coming_soon?count=100'
one_movie = 'http://api.douban.com/v2/movie/subject/1764796'

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
    ['大世界', 26954003, 3.75, 'Animation',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试'],
    ['无问西东', 6874741, 0.0, 'Drama|Romance|War',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试'],
    ['迷镇凶案', 2133433, 3.15, 'Comedy|Crime|Mystery',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试'],
    ['大寒', 26392877, 0.0, 'Drama|War',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试'],
    ['无法触碰的爱', 27621048, 0.0, 'Drama|Romance',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试'],
    ['青蛙总动员', 26752895, 1.7, 'Comedy|Animation',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试'],
    ['芒刺', 27601920, 0.0, 'Drama',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试'],
    ['第一夫人', 4849728, 3.3, 'Drama',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试'],
    ['神秘巨星', 26942674, 4.15, 'Drama|Musical',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试'],
    ['公牛历险记', 25846857, 3.75, 'Comedy|Animation|Adventure',
        'https://img3.doubanio.com/view/photo/m/public/p2221186392.webp', '简介测试']
]


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


# def to_list(json_data):
#     '''把豆瓣电影类型格式为适合推荐系统的数据结构二维list，过滤无类型电影，并把电影类型转为英文'''
#     data = []
#     for v in json_data['subjects']:
#         arr = []
#         arr.append(v['title'])
#         arr.append(int(v['id']))
#         arr.append(float(v['rating']['average']))
#         # arr.append(v['images']['large'])
#         string = ''
#         for genre in v['genres']:
#             genre = transform(genre, 'en')
#             if genre is not None and genre != '(no genres listed)':
#                 string += genre
#                 string += '|'
#         string = string[:-1]
#         if string == '':
#             continue
#         arr.append(string)
#         data.append(arr)

#     return data


def list_to_json(list_data, header=['movieName', 'movieId', 'rating', 'genres']):
    '''把二维list电影数据转换为json dict，对外提供接口'''
    try:
        subjects = []
        for item in list_data:
            obj = {}
            for i in range(len(item)):
                obj[header[i]] = item[i]
            subjects.append(obj)

    except BaseException as err:
        return {'count': 0, 'error': err.args[0]}

    return {'subjects': subjects, 'count': len(list_data)}


def json_to_list(json_data, header=['movieName', 'movieId', 'rating', 'genres']):
    '''把请求的用户json转换为可以训练的list'''
    if json_data == '' or json_data == None:
        print('json_to_list error')
        return None
    data = []
    for v in json_data['subjects']:
        arr = []
        for k in header:
            arr.append(v[k])

        # arr.append(v['movieName'])
        # arr.append(int(v['movieId']))
        # arr.append(float(v['rating']))
        # arr.append(v['genres'])

        data.append(arr)

    return data


def douban_movies_to_list(json_data):
    '''把豆瓣json转换为可以推荐的list格式'''
    if json_data == '' or json_data == None:
        print('douban_movies_to_list error')        
        return None
    data = []
    # 这里处理单个电影数据
    if json_data.get('count') == None:
        print('one movie')
        arr = []
        v = json_data

        arr.append(v['title'])
        arr.append(int(v['id']))
        arr.append(float(v['rating']['average']))

        # genres
        string = ''
        for genre in v['genres']:
            genre = transform(genre, 'en')
            if genre is not None and genre != '(no genres listed)':
                string += genre
                string += '|'
        string = string[:-1]
        if string == '':
            return []
        arr.append(string)
        # img
        arr.append(v['images']['large'])
        # summary
        summary = v.get('summary')
        if summary is None:
            arr.append('')
        else:
            arr.append(summary)

        data.append(arr)
        return data

    print(json_data.get('count'))

    # 这里处理多个电影数据
    for v in json_data['subjects']:
        arr = []
        arr.append(v['title'])
        arr.append(int(v['id']))
        arr.append(float(v['rating']['average']))

        string = ''
        for genre in v['genres']:
            genre = transform(genre, 'en')
            if genre is not None and genre != '(no genres listed)':
                string += genre
                string += '|'
        string = string[:-1]
        if string == '':
            continue
        arr.append(string)
        arr.append(v['images']['large'])
        summary = v.get('summary')
        if summary is None:
            arr.append('')
        else:
            arr.append(summary)

        data.append(arr)

    return data


def init_movie_rs():
    '''初始化推荐系统，返回模型'''
    print('start movie-rs')
    x_train, y_train = ml.reshape_train()
    rs = ml.MovieRS()
    rs.fit(x_train, y_train)
    print('train finished')
    return rs


model = init_movie_rs()


def get_recommend_movies(rs, user_data, recommend_data, n=5):
    '''根据模型，用户历史数据，候选电影数据和个数，返回相应的推荐电影数据'''
    user_movies = rs.predict(user_data, n)
    print('user_movies', user_movies)
    return rs.CosineSim(recommend_data, user_movies)


def error_res(msg="error"):
    return jsonify({"count": 0, "message": msg})


@app.route('/api', methods=['POST'])
def api():
    '''对外提供推荐系统api'''
    try:
        base_url = 'http://api.douban.com/v2/movie/subject/'
        # 推荐算法
        # java给的接口{"user": {...}, "recommend":{...}}
        data = json.loads(str(request.get_data(), 'utf-8'))
        print('get_recommend_movies')

        user_data = data['user']
        recommend_data = data['recommend']

        user_data = json_to_list(user_data)
        recommend_data = json_to_list(recommend_data)
        
        movies = get_recommend_movies(model, user_data, recommend_data, n=10)
        print('get_recommend_movies end')
        print('movies', movies)
        new_movies = []

        # 向豆瓣请求获得更详细的数据
        for movie in movies:

            res = requests.get(base_url + str(movie['movieId']))
            print('movieId:', movie['movieId'])
            if res.ok:
                douban_data = res.json()
            else:
                douban_data = ''

            new_movie = douban_movies_to_list(douban_data)
            if new_movie is not None:
                new_movies.append(new_movie)

        temp_json = list_to_json(new_movies, header=[
                                 'movieName', 'movieId', 'rating', 'genres', 'img', 'summary'])
        resp = make_response(jsonify(temp_json))
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp
    except BaseException as err:
        print(request.get_data())
        return error_res("api error")


# @app.route('/test', methods=['GET', 'POST'])
# def test():
#     '''测试用api，返回静态数据'''
#     return "test"

@app.route('/test2', methods=['GET', 'POST'])
def test2():
    '''测试用api，返回豆瓣的数据'''
    movies = douban_movies_to_list(requests.get(one_movie).json())
    temp_json = list_to_json(
        movies,  header=['movieName', 'movieId', 'rating', 'genres', 'img', 'summary'])
    resp = make_response(jsonify(temp_json))
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    # request.data 表示请求体
    print(request.get_data())
    return resp


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
