### movielens使用数据
  - ratings：userId，movieId，ratings，timestamp(未使用)
  - movies：movieId，movieName，genres
    - genres：'Action|Adventure|Animation|Children\'s|Comedy|Crime|Documentary|Drama|Fantasy|Film-Noir|Horror|IMAX|Musical|Mystery|Romance|Sci-Fi|Thriller|War|Western'
  - 数据预处理：删除 ratings 中的 `timestamp` 列

### class Reshape：整理训练集和测试集
  - #### reshape_train(user)：整理训练集，构建用户-电影矩阵
    - 使用 ratings + movies 构建训练集 data ，电影评分为5分制，4以下统一为0，3以上为1
    - 除去 `no genres listed` 电影类型
    - 加入用户历史数据
    - 构建矩阵，矩阵维数为[输入的用户历史条目数，19] (19为19个电影类型)
    - 输入：用户历史数据 user
      - 数据类型 array
      - 数据格式['movieName', 'movieId', 'rating', 'genres']
      - 需预先除去 `no genres listed` 电影类型
      - 电影评分 `rating` 为5分制
    - 输出：训练集矩阵 x_train, y_train

  - #### user_matrix(recommend)：整理测试集，匹配矩阵，构建用户-电影矩阵
    - 测试集中 movieId 数据转成 `int.64` 类型，ratings 数据转成 `float64` 类型
    - 除去测试数据集 `movieId`，构建矩阵，矩阵维数为 [输入的用户历史条目数，19]
    - 输入：测试数据集 recommend
      - 数据类型 array
      - 数据格式 ['movieName', 'movieId', 'rating', 'genres']
      - 需预先除去 `no genres listed` 电影类型
      - 电影评分 `rating` 为5分制
    - 输出：测试集矩阵 x_test, y_test

### calss MovieRS：进行电影推荐
  - #### fit(x_train, y_train)：训练逻辑回归模型
  - 输入：训练集 x_train, y_train，训练集来自`class Reshape`类

  - #### predict(x_test, recommend, n=10)：预测测试集中用户可能看的电影
  - 输入：测试集 x_test，要推荐的电影数据 test_data，要推荐的电影数量 n
  - 输出：推荐的电影，数据类型 array