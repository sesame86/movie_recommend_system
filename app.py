import collections
from scipy.spatial import distance
import pandas as pd
import math
from operator import itemgetter

from bson import ObjectId
from flask import Flask, render_template, request, session, redirect, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'sparta'

client = MongoClient('localhost', 27017)
db = client.MovieDB

@app.route('/')
def check():
    # 세션에 'sessionID'라는 변수가 있는
    if 'sessionID' in session:
        # 세션에 'sessionID'라는 변수의 값을 가져와서
        session_id = session['sessionID']
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 user DB에 있는지 확인
        user = db.user.find_one({'_id': ObjectId(session_id)})

        # 세션에 'sessionID'라는 변수의 값이 비어있거나
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 없다면
        if session_id is None or user is None:
            # 로그인 페이지를 띄워줌
            return render_template('login.html')
        # 아니라면 로그인 한 세션이 있는 유저이므로 메인 페이지로 보냄
        return render_template('main.html', nickname=user['nickname'])
    return render_template('login.html')


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['userID']
    password = request.form['password']

    user = db.user.find_one({'user_id': user_id, 'password': password})


    if user is not None:
        # 세션을 생성하는데
        # 세션에 'sessionID'라는 변수에
        # 유저 생성시 만들어진 _id 값을 넣어둠(유저 고유 식별자이기 때문)
        session['sessionID'] = str(user['_id'])
        return redirect('/')
    return render_template('login.html')


@app.route('/signUp', methods=['GET'])
def sign_up_page():
    return render_template('signUp.html')


@app.route('/signUp', methods=['POST'])
def sign_up():
    user_id = request.form['userid_give']
    password = request.form['password_give']
    nickname = request.form['nickname_give']

    db.user.insert_one({'user_id': user_id, 'password': password, 'nickname': nickname})
    return jsonify({'result': 'success'})


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('sessionID')
    return jsonify({'result': 'success'})

@app.route('/rating', methods=['GET'])
def rate_page():
    return render_template('rate.html')

@app.route('/rating', methods=['POST'])
def give_rate():
    userid_recive = session['sessionID']
    # rate_receive 클라이언트가 준 rate 가져오기
    rate_receive = request.form['rate_give']
    # movieid_receive 클라이언트가 준 movieid 가져오기
    tmdbid_receive = request.form['tmdbid_give']

    # DB에 삽입할 rating 만들기
    rate = {
        'userid':userid_recive,
        'rate': rate_receive,
        'tmdbid': tmdbid_receive
    }
    # reviews에 review 저장하기
    db.rate.insert_one(rate)
    # 성공 여부 & 성공 메시지 반환
    return jsonify({'result': 'success', 'msg': '별점저장 완료😎'})

@app.route('/genre', methods=['GET'])
def genre_page():
    return render_template('genre.html')

@app.route('/mypage', methods=['GET'])
def my_page():
    return render_template('mypage.html')


@app.route('/mymovie', methods=['POST'])
def create_movie():
    userid_recive = session['sessionID']

    tmdbid_recieve = request.form['tmdbid_give']
    title_receive = request.form['title_give']
    genre_receive = request.form['genre_give']
    overview_receive = request.form['overview_give']
    nation_receive = request.form['nation_give']

    Mymovie_list = {
        'userid':userid_recive,
        'tmdbid':tmdbid_recieve,
        'title':title_receive,
        'genre':genre_receive,
        'overview':overview_receive,
        'nation':nation_receive
    }
    db.Mymovie_list.insert_one(Mymovie_list)

    return jsonify({'result': 'success'})

@app.route('/recommendMovie', methods=['GET'])
def movie_recommend():
    all_rating = pd.DataFrame(db.all_rating.find({}, {'_id': False}))
    links = pd.DataFrame(db.links.find({}, {'_id': False}))
    rate = pd.DataFrame(db.rate.find({}, {'_id': False}))

    tmdbMovieRating = pd.merge(all_rating,links)
    tmdbMovieRating = tmdbMovieRating[['userId','rating','tmdbId']]
    tmdbMovieRating.rename(columns={'userId': 'userid', 'rating':'rate', 'tmdbId': 'tmdbid'}, inplace=True)

    #tmdbMovieRating['userid'] = tmdbMovieRating['userid'].astype(object)
    concatRateData = pd.concat([tmdbMovieRating, rate], axis=0)

    # pivote table
    UM_matrix_ds = pd.pivot_table(tmdbMovieRating,index='userid', columns='tmdbid', values='rate')

    def distance_euclidean(a, b):
        return 1 / (distance.euclidean(a, b) + 1)

    def nearest_neighbor_user(user, topN, simFunc):
        u1 = UM_matrix_ds.loc[user].dropna()
        ratedIndex = u1.index
        nn = {}

        ## Brote Force Compute
        for uid, row in UM_matrix_ds.iterrows():
            interSectionU1 = []
            interSectionU2 = []
            if uid == user:
                continue

            for i in ratedIndex:
                if False == math.isnan(row[i]):
                    interSectionU1.append(u1[i])
                    interSectionU2.append(row[i])
            interSectionLen = len(interSectionU1)

            ## At least 3 intersection items
            if interSectionLen < 3:
                continue

            ## similarity functon
            sim = simFunc(interSectionU1, interSectionU2)

            if math.isnan(sim) == False:
                nn[uid] = sim

        ## top N returned
        return sorted(nn.items(), key=itemgetter(1), reverse=True)[:(topN + 1)]
        # return sorted(nn.items(),key=itemgetter(1))[:-(topN+1):-1]

    def predictRating(userid, nn=50, simFunc=distance_euclidean):

        ## neighboorhood
        neighbor = nearest_neighbor_user(userid, nn, simFunc)
        # userid : similarity 의 dictionary

        neighbor_id = [id for id, sim in neighbor]
        # 비슷한 유사도를 보이는 유저 리스트

        ## 4개이상이 NaN인 경우 제거
        neighbor_movie = UM_matrix_ds.loc[neighbor_id].dropna(1, how='all', thresh=4)
        # 유저id x 영화id 의 DataFrame. 단, column의 NaN이 4개 이상인 경우 삭제했음.

        neighbor_dic = (dict(neighbor))
        ret = []  # ['movieId', 'predictedRate']

        # 각 column을 순회한다. key : userid, column : movieid, value : rating
        for movieId, row in neighbor_movie.iteritems():
            jsum, wsum = 0, 0
            for v in row.dropna().iteritems():
                sim = neighbor_dic.get(v[0], 0)
                jsum += sim
                wsum += (v[1] * sim)
            ret.append([movieId, wsum / jsum])

        return ret

    session_id = session['sessionID']
    result = predictRating(session_id, nn=50, simFunc=distance_euclidean)
    predict = pd.DataFrame(result, columns=['tmdbid', 'predicted_rating'])
    predict = (predict.sort_values(['predicted_rating'], ascending=False)).values.tolist()

    return jsonify({'result': 'success', 'predict_list': predict})

# @app.route('/myGenre', methods=['POST'])
# def save_genre():
#     genre_receive = request.form['genre_give']
#
#     # DB에 삽입할 rating 만들기
#     MyGenre_list = {
#         'genre':genre_receive,
#         'like':0
#     }
#     # reviews에 review 저장하기
#     db.MyGenre_list.insert_one(MyGenre_list)
#     # 성공 여부 & 성공 메시지 반환
#     return jsonify({'result': 'success'})

# @app.route('/countGenre', methods=['POST'])
# def count_genre():
#     genre_receive = request.form['genre_give']
#
#     genre = db.MyGenre_list.find_one({'genre': genre_receive})
#
#     new_like = genre['like'] + 1
#
#     db.MyGenre_list.update_one({'genre': genre_receive}, {'$set': {'like': new_like}})
#
#     return jsonify({'result': 'success'})
#
#
# @app.route('/countGenre', methods=['GET'])
# def genre_data():
#     genre = list(db.MyGenre_list.find({}, {'_id': False}))
#
#     return jsonify({'result': 'success', 'genre_list': genre})
@app.route('/countGenre', methods=['GET'])
def count_genre():
    session_id = session['sessionID']
    genres = list(db.Mymovie_list.find({'userid':session_id}, {'_id': False, 'userid': False, 'tmdbid': False, 'title': False,
                                                'overview': False, 'nation': False}))
    genre_list = []
    for i in genres:
        for index, genre in i.items():
            genre_list.append(genre)
    genre_count = collections.Counter(genre_list)

    return jsonify({'result': 'success', 'genre_list': genre_count})

@app.route('/countRating', methods=['GET'])
def count_rate():
    session_id = session['sessionID']
    rates = list(db.rate.find({'userid':session_id}, {'_id': False, 'userid':False, 'tmdbid':False}))

    rate_list = []

    for i in rates:
        for index, rate in i.items():
            rate_list.append(rate)
    rate_count = collections.Counter(rate_list)


    return jsonify({'result': 'success', 'rate_list': rate_count})

@app.route('/countNation', methods=['GET'])
def count_nation():
    session_id = session['sessionID']
    nations = list(db.Mymovie_list.find({'userid':session_id}, {'_id': False, 'userid':False, 'tmdbid':False, 'title':False, 'genre':False, 'overview':False}))

    nation_list = []
    for i in nations:
        for index, nation in i.items():
            nation_list.append(nation)
    nation_count = collections.Counter(nation_list)

    return jsonify({'result': 'success', 'nation_list': nation_count})

@app.route('/search', methods=['GET'])
def search_page():
    return render_template('search.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
