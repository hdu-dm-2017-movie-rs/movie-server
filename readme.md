# 电影推荐系统的服务器接口

## 接口

返回电影基本数据，全局有一个count属性，如果为0则表示错误或者无数据。

- `POST` ip:port/ 正式接口

- `POST` ip:port/test 测试用接口，总是返回静态数据提供调试

返回数据样例，之后会补充更多电影的属性

```json
{'count': 10,
 'subjects': [{'genres': 'Animation',
   'movieId': '大世界',
   'movieName': 26954003,
   'rank': 3.75},
  {'genres': 'Drama|Romance|War',
   'movieId': '无问西东',
   'movieName': 6874741,
   'rank': 0.0},
  {'genres': 'Comedy|Crime|Mystery',
   'movieId': '迷镇凶案',
   'movieName': 2133433,
   'rank': 3.15},
  {'genres': 'Drama|War', 'movieId': '大寒', 'movieName': 26392877, 'rank': 0.0},
  {'genres': 'Drama|Romance',
   'movieId': '无法触碰的爱',
   'movieName': 27621048,
   'rank': 0.0},
  {'genres': 'Comedy|Animation',
   'movieId': '青蛙总动员',
   'movieName': 26752895,
   'rank': 1.7},
  {'genres': 'Drama', 'movieId': '芒刺', 'movieName': 27601920, 'rank': 0.0},
  {'genres': 'Drama', 'movieId': '第一夫人', 'movieName': 4849728, 'rank': 3.3},
  {'genres': 'Drama|Musical',
   'movieId': '神秘巨星',
   'movieName': 26942674,
   'rank': 4.15},
  {'genres': 'Comedy|Animation|Adventure',
   'movieId': '公牛历险记',
   'movieName': 25846857,
   'rank': 3.75}]}
```

## 项目说明

依赖主目录下的ml-latest

* main.py 是主服务器
* ml.py 是推荐算法
* mysql.py 还没有使用上

[算法接口](ml_func.md)