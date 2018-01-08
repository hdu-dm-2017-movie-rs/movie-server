# 电影推荐系统的服务器接口

## 接口

返回电影基本数据，全局有一个count属性，如果为0则表示错误或者无数据。

- `POST` ip:port/ 正式接口

- `POST` ip:port/test 测试用接口，总是返回静态数据提供调试

返回数据样例，之后会补充更多电影的属性

```json
{"count": 1,
 "subjects": [
     {"genres": "大世界",
   "movieId": "Animation",
   "movieName": 26954003,
   "rank": 3.75}
   ]
}
```

## 项目说明

依赖主目录下的ml-latest

* main.py 是主服务器
* ml.py 是推荐算法
* mysql.py 还没有使用上

[算法接口](ml_func.md)