import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from copy import deepcopy

ratings = pd.read_csv('ml-latest/ratings.csv')
ratings = ratings.drop(['timestamp'], axis=1)
movies = pd.read_csv('ml-latest/movies.csv')
ratings = ratings.sample(frac=0.001)


class Reshape():
    def __init__(self):
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None

    def reshape_train(self, user):
        ratings['rating'] = ratings['rating'].apply(
            lambda x: 1 if x > 3 else 0)
        genresplit = movies.set_index('movieId').genres.str.split(
            r'|', expand=True).stack().reset_index(level=1, drop=True).to_frame('genre')
        genres = pd.get_dummies(genresplit, prefix='genre', columns=[
                                'genre']).groupby(level=0).sum()
        genres = genres.drop(['genre_(no genres listed)'], axis=1)
        genres['movieId'] = genres.index
        data = pd.merge(ratings, genres, on='movieId', how='left')
        user_data = pd.DataFrame(
            user, columns=['movieName', 'movieId', 'rating', 'genres'])
        data.append(user_data)
        data = data.drop(['userId'], axis=1)
        data = data.drop(['movieId'], axis=1)
        data = data.fillna(np.nan)
        self.x_train = data.drop(['rating'], axis=1)
        self.y_train = data['rating']
        return self.x_train, self.y_train

    def user_matrix(self, array_input):
        all_id = [0, 0, 0, 'Action|Adventure|Animation|Children\'s|Comedy|Crime|Documentary|Drama|Fantasy|Film-Noir|Horror|IMAX|Musical|Mystery|Romance|Sci-Fi|Thriller|War|Western']
        array = array_input
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
        test = pd.merge(test[test.columns[1:3]],
                        genres_test, on='movieId', how='left')
        test = test.drop(['movieId'], axis=1)
        self.x_test = test.drop(['rating'], axis=1)
        self.y_test = test['rating']
        return self.x_test, self.y_test


__all__ = ['Reshape']


class MovieRS():
    def __init__(self):
        self.algo = None

    def fit(self, x_train, y_train):
        logreg = LogisticRegression(C=10, class_weight='balanced')
        logreg.fit(x_train, y_train)
        self.algo = logreg

    def predict(self, x_test, test_data, n=10):
        logreg = self.algo
        rs_id = []
        y_predlog = logreg.predict(x_test)
        count = 0
        for i in range(y_predlog.shape[0] - 1):
            if y_predlog[i] > 0:
                count += 1
                rs_id.append(test_data[i])
            if count >= n:
                return rs_id
                # print(test_data[i])
        return rs_id


__all__ = ['MovieRS']


if __name__ == '__main__':

    user = [['21', '5350027', '3.45', 'Drama|Mystery'],
            ['22', '26797419', '3.1', 'Comedy'],
            ['23', '26654146', '2.7', 'Drama'],
            ['24', '20495023', '4.55', 'Comedy|Animation|Adventure'],
            ['25', '26340419', '4.15', 'Comedy|Animation'],
            ['26', '26661191', '2.4', 'Action'],
            ['27', '26761416', '4.3', 'Drama']]
    reshape = Reshape()
    x_train, y_train = reshape.reshape_train(user)
    rs = MovieRS()
    # 训练用户画像
    rs.fit(x_train, y_train)

    recommad = [['1', '26662193', '3.1', 'Comedy'],
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
    recommad_data = deepcopy(recommad)
    user_data = deepcopy(user)

    reshape = Reshape()
    x_test, y_test = reshape.user_matrix(recommad)
    movies = rs.predict(x_test, recommad, n=10)
    # 候选电影中推荐的电影
    print(movies)
    # print(y_test)
    print(user_data == user)
    print(recommad_data == recommad)
