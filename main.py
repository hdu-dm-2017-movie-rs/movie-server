import json
from copy import deepcopy
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


def to_list(json_data):
    '''把豆瓣电影类型格式为适合推荐系统的数据结构二维list，过滤无类型电影，并把电影类型转为英文'''
    data = []
    for v in json_data['subjects']:
        arr = []
        arr.append(v['title'])
        arr.append(int(v['id']))
        arr.append(float(v['rating']['average']) / 2)
        # arr.append(v['images']['large'])
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
        data.append(arr)

    return data


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


def movies_to_list(json_data):
    '''把豆瓣json转换为可以推荐的list格式'''
    if json_data == '' or json_data == None:
        return None
    data = []
    # 这里处理单个电影数据
    if json_data.get('count') == None:
        print('one movie')
        arr = []
        v = json_data
        arr.append(v['title'])
        arr.append(int(v['id']))
        arr.append(float(v['rating']['average']) / 2)

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
        arr.append(v['images']['large'])
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
        arr.append(float(v['rating']['average']) / 2)

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
        movies = get_recommend_movies(model, data['user'], data['recommend'], n=10)
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

            new_movie = movies_to_list(douban_data)
            if new_movie is not None:
                new_movies.append(new_movie)

        temp_json = list_to_json(new_movies, header=['movieName', 'movieId', 'rating', 'genres', 'img', 'summary'])
        resp = make_response(jsonify(temp_json))
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp
    except BaseException as err:
        return error_res("api error")
 


# @app.route('/test', methods=['GET', 'POST'])
# def test():
#     '''测试用api，返回静态数据'''
#     data = {"user":{"count":3,"subjects":[{"genres":"动作|科幻|冒险","movieId":10440138,"rating":2.3,"userId":1},{"genres":"剧情|爱情|同性","movieId":1291546,"rating":9,"userId":1},{"genres":"剧情|家庭|奇幻|冒险","movieId":1291545,"rating":8.7,"userId":1}]},"recommend":{"count":100,"subjects":[{"genres":"剧情","movieId":1419918,"moviename":"天若有情3烽火佳人 天若有情Ⅲ烽火佳人","rank":"6.9"},{"genres":"动画|冒险","movieId":1512037,"moviename":"奇诺之旅 キノの旅 -the Beautiful World-","rank":"8.9"},{"genres":"喜剧|动作|奇幻","movieId":25827963,"moviename":"西游记之孙悟空三打白骨精","rank":"5.6"},{"genres":"纪录片","movieId":3443389,"moviename":"海洋","rank":"9"},{"genres":"剧情|悬疑|惊悚","movieId":1292217,"moviename":"穆赫兰道 Mulholland Dr.","rank":"8.3"},{"genres":"动作|武侠|古装","movieId":1300265,"moviename":"六指琴魔","rank":"7.0"},{"genres":"科幻|动画|悬疑|冒险","movieId":2119796,"moviename":"宠物小精灵：裂空的访问者 劇場版ポケットモンスター アドバンスジェネレーション 裂空の訪問者 デオキシス","rank":"7.5"},{"genres":"剧情|动画","movieId":19899704,"moviename":"AIURA あいうら","rank":"8.2"},{"genres":"剧情","movieId":5156113,"moviename":"书道教授 書道教授","rank":"7.5"},{"genres":"喜剧|爱情","movieId":26674021,"moviename":"爱情冻住了 我的蛋男情人","rank":"5.4"},{"genres":"歌舞|家庭|奇幻|冒险","movieId":1304402,"moviename":"妙妙龙 Pete&#39;s Dragon","rank":"7.2"},{"genres":"剧情|爱情|武侠","movieId":1297447,"moviename":"倩女幽魂","rank":"8.6"},{"genres":"剧情|喜剧|动画|家庭","movieId":22790508,"moviename":"有顶天家族 有頂天家族","rank":"8.9"},{"genres":"动画","movieId":26754736,"moviename":"爆音少女！！OAD ばくおん!! OAD","rank":"5.5"},{"genres":"喜剧|动作|爱情","movieId":1309199,"moviename":"史密斯夫妇 Mr. &amp; Mrs. Smith","rank":"7.6"},{"genres":"喜剧|动画|冒险","movieId":1437339,"moviename":"篱笆墙外 Over the Hedge","rank":"7.4"},{"genres":"剧情|动画","movieId":25738795,"moviename":"无限斯特拉托斯OVA：一夏的思绪 IS＜インフィニット?ストラトス＞ 一夏の想いで","rank":"5.9"},{"genres":"剧情|惊悚|犯罪","movieId":1484760,"moviename":"黑社会2：以和为贵 黑社會以和為貴","rank":"7.7"},{"genres":"剧情|动画","movieId":26434811,"moviename":"终物语 終物語","rank":"8.7"},{"genres":"动画|奇幻","movieId":3893384,"moviename":"化物语 化物語","rank":"8.7"},{"genres":"剧情|历史|战争","movieId":26591654,"moviename":"地雷区 Under sandet","rank":"8.5"},{"genres":"喜剧|动作","movieId":1292867,"moviename":"快餐车","rank":"7.4"},{"genres":"喜剧","movieId":1308520,"moviename":"恋上你的床","rank":"5.8"},{"genres":"动作|动画|冒险","movieId":5339104,"moviename":"海贼王特别篇16 简单易懂 路飞大百科 海贼王SP12-2005-简单易懂 路飞大百科","rank":"7.1"},{"genres":"动画","movieId":26303572,"moviename":"出包王女Darkness OAD5 To LOVEる -とらぶる- ダークネス OAD5","rank":"8.0"},{"genres":"动画","movieId":6829661,"moviename":"因果论 UN-GO episode:0 因果論","rank":"8.0"},{"genres":"剧情","movieId":1292270,"moviename":"梦之安魂曲","rank":"8.7"},{"genres":"剧情|爱情","movieId":1293929,"moviename":"廊桥遗梦 The Bridges of Madison County","rank":"8.6"},{"genres":"剧情|历史|西部","movieId":27063332,"moviename":"金珠玛米","rank":"5.2"},{"genres":"剧情","movieId":1308749,"moviename":"忘不了","rank":"7.7"},{"genres":"悬疑|惊悚","movieId":1310175,"moviename":"群鸟 The Birds","rank":"8.1"},{"genres":"动画|短片","movieId":2286087,"moviename":"谁的本领大","rank":"7.8"},{"genres":"剧情","movieId":2343718,"moviename":"波之塔 松本清張ドラマスペシャル 波の塔","rank":"6.7"},{"genres":"剧情|家庭","movieId":26259677,"moviename":"垫底辣妹 ビリギャル","rank":"8.1"},{"genres":"喜剧|动画|冒险","movieId":3731581,"moviename":"里约大冒险 Rio","rank":"8.3"},{"genres":"喜剧|动作|爱情","movieId":1295064,"moviename":"城市猎人 城市獵人","rank":"7.2"},{"genres":"科幻|动画|冒险","movieId":26746802,"moviename":"数码宝贝大冒险tri. 第4章：丧失 デジモンアドベンチャー tri. 第4章 喪失","rank":"6.3"},{"genres":"动画|短片|戏曲","movieId":1441797,"moviename":"张飞审瓜","rank":"7.9"},{"genres":"动作|惊悚|犯罪","movieId":6537500,"moviename":"速度与激情6 Furious 6","rank":"7.7"},{"genres":"动画|短片|儿童","movieId":1431714,"moviename":"小鲤鱼跳龙门","rank":"7.9"},{"genres":"剧情|爱情","movieId":2213597,"moviename":"朗读者","rank":"8.5"},{"genres":"恐怖","movieId":2255841,"moviename":"死亡录像 [Rec]","rank":"7.5"},{"genres":"剧情|动作|冒险","movieId":1294671,"moviename":"中华英雄 中華英雄","rank":"6.3"},{"genres":"喜剧","movieId":1388196,"moviename":"绝种好男人","rank":"5.8"},{"genres":"剧情|动作|科幻|动画","movieId":1300798,"moviename":"飞跃巅峰 トップをねらえ!","rank":"8.9"},{"genres":"剧情","movieId":25727519,"moviename":"上锁的房间SP 鍵のかかった部屋 スペシャル","rank":"7.7"},{"genres":"动画","movieId":26598637,"moviename":"高中舰队 ハイスクール?フリート","rank":"7.7"},{"genres":"惊悚|恐怖","movieId":26779294,"moviename":"冥界 Nightworld","rank":"3.9"},{"genres":"奇幻|冒险","movieId":25845294,"moviename":"勇士之门","rank":"3.5"},{"genres":"剧情|爱情|同性","movieId":1291546,"moviename":"霸王别姬","rank":"9.5"},{"genres":"剧情","movieId":1291870,"moviename":"雨人 Rain Man","rank":"8.6"},{"genres":"剧情|爱情|同性","movieId":1308575,"moviename":"蓝色大门 藍色大門","rank":"8.3"},{"genres":"剧情|动作|爱情|惊悚|犯罪","movieId":3808604,"moviename":"危情三日 The Next Three Days","rank":"7.9"},{"genres":"悬疑|惊悚|犯罪","movieId":1298412,"moviename":"三十九级台阶 The 39 Steps","rank":"7.8"},{"genres":"剧情|动作|犯罪","movieId":1300741,"moviename":"枪火 鎗火","rank":"8.6"},{"genres":"科幻|犯罪","movieId":10462705,"moviename":"白金数据 プラチナデータ","rank":"6.8"},{"genres":"悬疑|惊悚|恐怖","movieId":1293181,"moviename":"惊魂记 Psycho","rank":"8.9"},{"genres":"剧情","movieId":25958787,"moviename":"深夜食堂电影版 映画 深夜食堂","rank":"7.8"},{"genres":"喜剧|动画|歌舞","movieId":26354572,"moviename":"欢乐好声音 Sing","rank":"8.2"},{"genres":"剧情|爱情|战争","movieId":6874741,"moviename":"无问西东","rank":"0"},{"genres":"喜剧|动画|家庭","movieId":1292973,"moviename":"小鸡快跑 Chicken Run","rank":"7.5"},{"genres":"剧情","movieId":6973370,"moviename":"再也不诱拐了 もう誘拐なんてしない","rank":"6.9"},{"genres":"恐怖","movieId":26587772,"moviename":"莫丽·哈特莉的驱魔 The Exorcism of Molly Hartley","rank":"4.8"},{"genres":"剧情|喜剧|动画","movieId":10573483,"moviename":"我的妹妹哪有这么可爱 第二季 俺の妹がこんなに可愛いわけがない。","rank":"7.4"},{"genres":"动画","movieId":2280004,"moviename":"海贼王剧场版5：被诅咒的圣剑 ONE PIECE 呪われた聖剣","rank":"7.7"},{"genres":"喜剧|动画|短片|家庭","movieId":1304958,"moviename":"粉红豹 The Pink Phink","rank":"7.6"},{"genres":"动画|短片","movieId":26415289,"moviename":"神速のRouge","rank":"6.8"},{"genres":"喜剧|爱情|动画|歌舞|家庭|冒险","movieId":1293369,"moviename":"终极傻瓜 A Goofy Movie","rank":"7.4"},{"genres":"剧情|科幻","movieId":1298405,"moviename":"第三类接触 Close Encounters of the Third Kind","rank":"7.2"},{"genres":"喜剧|动画|短片|家庭|西部","movieId":2191102,"moviename":"牛仔德鲁比 Drag-A-Long Droopy","rank":"8.7"},{"genres":"剧情|家庭|传记","movieId":1300572,"moviename":"童年往事","rank":"8.8"},{"genres":"喜剧|动画|冒险","movieId":1907966,"moviename":"疯狂原始人 The Croods","rank":"8.7"},{"genres":"剧情|爱情|惊悚|奇幻","movieId":2135981,"moviename":"画皮 畫皮","rank":"6.5"},{"genres":"喜剧|动画|短片|家庭","movieId":5262268,"moviename":"父子烤肉野餐 Barbecue Brawl","rank":"8.8"},{"genres":"剧情|传记|运动","movieId":1293155,"moviename":"愤怒的公牛 Raging Bull","rank":"8.3"},{"genres":"动画","movieId":3118781,"moviename":"米奇的圣诞颂歌 Mickey&#39;s Christmas Carol","rank":"8.3"},{"genres":"动作|犯罪","movieId":1310185,"moviename":"三岔口","rank":"6.5"},{"genres":"剧情|悬疑|犯罪","movieId":24719063,"moviename":"烈日灼心","rank":"7.9"},{"genres":"科幻","movieId":1294852,"moviename":"宇宙终点之旅 Ikarie XB 1","rank":"7.4"},{"genres":"剧情","movieId":2042219,"moviename":"天然子结构 天然コケッコー","rank":"7.6"},{"genres":"剧情|喜剧","movieId":1300883,"moviename":"赌神","rank":"7.9"},{"genres":"科幻|动画","movieId":2043155,"moviename":"反叛的鲁路修 コードギアス 反逆のルルーシュ","rank":"8.9"},{"genres":"喜剧|音乐|犯罪","movieId":1301509,"moviename":"修女也疯狂 Sister Act","rank":"8.0"},{"genres":"喜剧","movieId":1424743,"moviename":"这个阿爸真爆炸","rank":"6.0"},{"genres":"剧情|爱情|同性","movieId":6829652,"moviename":"女朋友○男朋友","rank":"7.5"},{"genres":"剧情|喜剧","movieId":1300566,"moviename":"赌侠","rank":"7.4"},{"genres":"剧情","movieId":2085537,"moviename":"马拉松 マラソン","rank":"8.7"},{"genres":"喜剧|犯罪","movieId":1862151,"moviename":"疯狂的石头","rank":"8.2"},{"genres":"剧情|悬疑|犯罪","movieId":26996783,"moviename":"大嫂","rank":"3.3"},{"genres":"悬疑","movieId":3235947,"moviename":"罗宾计划 ルパンの消息","rank":"7.9"},{"genres":"喜剧|动画|短片|家庭","movieId":2346316,"moviename":"高空跳水 High Diving Hare","rank":"8.8"},{"genres":"剧情|音乐|传记","movieId":1293399,"moviename":"莫扎特传 Amadeus","rank":"8.6"},{"genres":"悬疑|惊悚","movieId":1294979,"moviename":"足迹 Sleuth","rank":"8.4"},{"genres":"动画","movieId":5361548,"moviename":"棒球大联盟 OVA MAJOR OVA","rank":"8.4"},{"genres":"剧情|爱情","movieId":25827935,"moviename":"七月与安生","rank":"7.6"},{"genres":"动画|家庭","movieId":1755552,"moviename":"小熊维尼:长鼻怪万圣节 Pooh&#39;s Heffalump Halloween Movie","rank":"7.7"},{"genres":"剧情|科幻|悬疑|惊悚","movieId":1292343,"moviename":"蝴蝶效应 The Butterfly Effect","rank":"8.7"},{"genres":"悬疑|惊悚|犯罪","movieId":1301230,"moviename":"夺魂索 Rope","rank":"8.0"},{"genres":"动作|科幻|动画|战争","movieId":20473395,"moviename":"K 剧场版 劇場版 K MISSING KINGS","rank":"7.7"},{"genres":"剧情|动画|悬疑|惊悚|恐怖|犯罪|奇幻","movieId":11499092,"moviename":"空之境界 未来福音 劇場版 空の境界 未来福音","rank":"9.1"}]}}

#     return resp


@app.route('/test2', methods=['GET', 'POST'])
def test2():
    '''测试用api，返回豆瓣的数据'''
    movies = movies_to_list(requests.get(one_movie).json())
    temp_json = list_to_json(movies,  header=['movieName', 'movieId', 'rating', 'genres', 'img', 'summary'])
    resp = make_response(jsonify(temp_json))
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    # request.data 表示请求体
    app.logger.error(request.get_data())
    print(request.data)
    return resp


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
