# encoding=utf8
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import copy
import math
import time

ratings = pd.read_csv('ml-latest/ratings.csv')
ratings = ratings.drop(['timestamp'], axis=1)
movies = pd.read_csv('ml-latest/movies.csv')
ratings = ratings.sample(frac=0.5)

# 构建训练集矩阵[电影数量，电影类型19]，使用预先载入数据集


def reshape_train():
    rating = copy.copy(ratings)
    movie = copy.copy(movies)
    ratings['rating'] = ratings['rating'].apply(lambda x: 1 if x > 3 else 0)
    genresplit = movies.set_index('movieId').genres.str.split(
        r'|', expand=True).stack().reset_index(level=1, drop=True).to_frame('genre')
    genres = pd.get_dummies(genresplit, prefix='genre', columns=[
                            'genre']).groupby(level=0).sum()
    genres = genres.drop(['genre_(no genres listed)'], axis=1)
    genres['movieId'] = genres.index
    data = pd.merge(ratings, genres, on='movieId', how='left')
    # user_data = pd.DataFrame(user, columns=['movieName', 'movieId', 'rating', 'genres'])
    # data.append(user_data)
    data = data.drop(['userId'], axis=1)
    data = data.drop(['movieId'], axis=1)
    data = data.fillna(np.nan)
    x_train = data.drop(['rating'], axis=1)
    y_train = data['rating']
    return x_train, y_train

# 传入用户数据和推荐数据，将传入的数据构建成矩阵


def user_matrix(array_input):
    array = copy.copy(array_input)
    all_id = [0, 0, 0, 'Action|Adventure|Animation|Children\'s|Comedy|Crime|Documentary|Drama|Fantasy|Film-Noir|Horror|IMAX|Musical|Mystery|Romance|Sci-Fi|Thriller|War|Western']
    array.append(all_id)
    test = pd.DataFrame(
        array, columns=['movieName', 'movieId', 'rating', 'genres'])
    test['movieId'] = test['movieId'].astype(np.int64)
    test['rating'] = test['rating'].astype(
        np.float64).apply(lambda x: 1 if x > 2 else 0)
    genresplit_test = test.set_index('movieId').genres.str.split(
        r'|', expand=True).stack().reset_index(level=1, drop=True).to_frame('genre')
    genres_test = pd.get_dummies(genresplit_test, prefix='genre', columns=[
                                 'genre']).groupby(level=0).sum()
    genres_test['movieId'] = genres_test.index
    test = pd.merge(test[test.columns[1:3]], genres_test,
                    on='movieId', how='left')
    test = test.drop(['movieId'], axis=1)
    x_test = test.drop(['rating'], axis=1)
    return x_test


# 进行逻辑回归并推荐出相似度高的电影
class MovieRS():
    def __init__(self):
        self.algo = None
        self.user = None
        self.rs_id = None
        self.X = None
        self.Y = None

    # 传入之前的训练集进行模型训练,使用随机森林模型
    def fit(self, x_train, y_train):
        # logreg = LogisticRegression(C=10, class_weight='balanced')
        # logreg.fit(x_train, y_train)
        # self.algo = logreg
        RFC = RandomForestClassifier(bootstrap=True, class_weight='balanced', criterion='gini', random_state=None,
                                     verbose=0, warm_start=False)
        RFC.set_params(n_estimators=10)
        RFC.fit(x_train, y_train)
        self.algo = RFC

    # 对输入的用户数据进行模型拟合
    def predict(self, user_input, n=5):
        self.user = user_input
        RFC = self.algo
        x_test = user_matrix(self.user)
        y_pred = RFC.predict(x_test)
        rs_id = []
        count = 0
        for i in range(y_pred.shape[0] - 1):
            if y_pred[i] > 0:
                count += 1
                rs_id.append(self.user[i])
            if count >= n:
                return rs_id
        return rs_id

    # 计算与要推荐的电影之间的余弦相似度
    def CosineSim(self, x, y, rate=0.5):
        self.X = x
        self.Y = y
        M1 = user_matrix(self.X)
        M2 = user_matrix(self.Y)
        w1 = []
        w2 = []
        sim = []
        result = []
        for i in range(len(self.X) - 1):
            w1.append(np.dot(np.array(M1), np.array(M2).T)[i].sum())
            w2.append(math.sqrt((np.array(M1) ** 2)
                                [i].sum()) * math.sqrt((np.array(M2).T ** 2).sum()))
            sim.append(w1[i] / w2[i])
            if sim[i] > rate:
                result.append(self.X[i])
        return result


__all__ = ['MovieRS']

if __name__ == '__main__':
    # 测试代码
    # like Comedy Animation Drama
    user1 = [['21', '15350027', '3.45', 'Drama|Mystery'],
             ['22', '26797419', '3.1', 'Comedy'],
             ['22', '26797419', '3.1', 'Comedy'],
             ['22', '26797419', '3.1', 'Comedy'],
             ['22', '26797419', '3.1', 'Comedy'],
             ['22', '26797419', '3.1', 'Comedy'],
             ['22', '26797419', '3.1', 'Comedy'],
             ['22', '26797419', '3.1', 'Comedy'],
             ['22', '26797419', '3.1', 'Comedy'],
             ['22', '26797419', '3.1', 'Comedy'],
             # ['23', '26654146', '2.7', 'Drama'],
             # ['24', '20495023', '4.55', 'Animation|Adventure'],
             # ['25', '26340419', '4.15', 'Comedy|Animation'],
             # ['26', '26661191', '2.4', 'Action'],
             # ['27', '26761416', '4.3', 'Drama'],
             # ['28', '82376484', '1.1', 'Mystery'],
             ['29', '21982364', '0.0', 'Action']]

    # like Sci-Fi Mystery Action
    user2 = [['31', '45350027', '4.0', 'Action'],
             # ['32', '26797419', '1.1', 'Mystery'],
             # ['33', '26729668', '4.5', 'Action|Sci-Fi'],
             # ['34', '20495023', '1.55', 'Animation|Adventure'],
             # ['35', '2634419', '1.15', 'Comedy|Animation'],
             # ['36', '20661191', '4.4', 'Action'],
             # ['37', '26761646', '0.3', 'Thriller'],
             ['38', '82376484', '4.7', 'Mystery'],
             ['38', '82376484', '4.7', 'Mystery'],
             ['38', '82376484', '4.7', 'Mystery'],
             ['38', '82376484', '4.7', 'Mystery'],
             ['38', '82376484', '4.7', 'Mystery'],
             ['38', '82376484', '4.7', 'Mystery'],
             ['38', '82376484', '4.7', 'Mystery'],
             ['38', '82376484', '4.7', 'Mystery'],
             ['39', '21922364', '4.6', 'Sci-Fi']]

    # like children Comedy
    user3 = [['41', '53500272', '1.0', 'Action|Mystery'],
             #  ['42', '26797419', '4.1', 'Comedy'],
             ['43', '26729168', '2.5', 'Sci-Fi'],
             ['43', '26729168', '2.5', 'Sci-Fi'],
             ['43', '26729168', '2.5', 'Sci-Fi'],
             ['43', '26729168', '2.5', 'Sci-Fi'],
             ['43', '26729168', '2.5', 'Sci-Fi'],
             ['43', '26729168', '2.5', 'Sci-Fi'],
             ['43', '26729168', '2.5', 'Sci-Fi'],
             #  ['44', '20495023', '3.5', 'Animation|Adventure'],
             #  ['45', '26740419', '3.1', 'Comedy|Animation'],
             #  ['46', '26661191', '2.4', 'Action'],
             #  ['47', '26761416', '1.3', 'Romance'],
             #  ['48', '82296484', '0.7', 'Mystery'],
             #  ['49', '21982564', '1.6', 'Action'],
             #  ['50', '27193475', '5.0', "Children's|Animation"],
             ['441', '21982324', '4.8', "War"]]

    # like Action Animation
    user4 = [['51', '53500272', '5.0', 'Action|Mystery'],
             ['52', '26797419', '3.1', 'Comedy'],
             ['53', '26729168', '4.5', 'IMAX'],
             ['53', '26729168', '4.5', 'IMAX'],
             ['53', '26729168', '4.5', 'IMAX'],
             ['53', '26729168', '4.5', 'IMAX'],
             ['53', '26729168', '4.5', 'IMAX'],
             ['53', '26729168', '4.5', 'IMAX'],
             ['53', '26729168', '4.5', 'IMAX'],
             #  ['54', '20495023', '4.2', 'IMAX|Adventure'],
             #  ['55', '26740419', '2.1', 'Comedy|Animation'],
             #  ['56', '26661191', '0.4', 'Musical'],
             #  ['57', '26761416', '3.9', 'Action'],
             #  ['58', '82296484', '0.7', 'Mystery'],
             #  ['59', '21982564', '4.6', 'Action'],
             #  ['60', '27193475', '3.0', "Children's|Animation"],
             ['61', '21982324', '1.8', "Children's"]]

    recommend = [['1', '26662193', '3.1', 'Comedy'],
                 ['2', '26862829', '3.9', 'Drama|War'],
                 ['3', '26966580', '2.4', 'IMAX|War'],
                 ['4', '53500237', '3.45', 'Drama|Mystery'],
                 ['5', '26797419', '3.1', 'Comedy'],
                 ['6', '26654146', '2.7', 'Drama'],
                 ['7', '20495023', '4.55', 'Comedy|Animation|Adventure'],
                 ['8', '26340419', '4.15', 'IMAX|Animation'],
                 ['9', '26774722', '3.05', 'Action|Crime|Mystery'],
                 ['10', '26729868', '2.5', 'Drama|Action|Sci-Fi'],
                 ['11', '26887161', '0.0', "Children's|Animation"],
                 ['12', '25837262', '4.3', 'Drama|Animation'],
                 ['13', '27193475', '0.0', "Children's|Animation"],
                 ['14', '26661191', '2.4', 'Action'],
                 ['15', '26761416', '4.3', 'Musical'],
                 ['16', '26340419', '4.8', 'Mystery|Animation'],
                 ['17', '26774722', '3.5', 'Crime|Mystery'],
                 ['18', '26429868', '2.5', 'Action|Sci-Fi'],
                 ['19', '26887161', '1.0', "Children's|Animation"],
                 ['20', '25836262', '4.3', 'Crime|Action'],
                 ['21', '27113475', '4.0', "Children's|Animation"],
                 ['22', '28661191', '2.4', 'Crime'],
                 ['23', '26261416', '4.3', "Drama|Children's"]]

    print(time.clock())
    x_train, y_train = reshape_train()
    rs = MovieRS()
    rs.fit(x_train, y_train)

    print(time.clock())
    user_movies1 = rs.predict(user1, n=5)
    user_movies2 = rs.predict(user2, n=5)
    user_movies3 = rs.predict(user3, n=5)
    user_movies4 = rs.predict(user4, n=5)

    result1 = rs.CosineSim(recommend, user_movies1)
    result2 = rs.CosineSim(recommend, user_movies2)
    result3 = rs.CosineSim(recommend, user_movies3)
    result4 = rs.CosineSim(recommend, user_movies4)
    print(time.clock())

    print(result1)
    print()

    print(result2)
    print()

    print(result3)
    print()

    print(result4)
    print()
