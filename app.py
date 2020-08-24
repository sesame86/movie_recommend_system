from bson import ObjectId
from flask import Flask, render_template, request, session, redirect, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'sparta'

client = MongoClient('localhost', 27017)
db = client.MovieDB


@app.route('/')
def hello_world():
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
    user_id = request.form['userID']
    password = request.form['password']
    nickname = request.form['nickname']

    db.user.insert_one({'user_id': user_id, 'password': password, 'nickname': nickname})
    return render_template('login.html')


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
    movieid_receive = request.form['movieid_give']

    # DB에 삽입할 rating 만들기
    rate = {
        'userid':userid_recive,
        'rate': rate_receive,
        'movieid': movieid_receive
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

    movieid_recieve = request.form['movieid_give']
    title_receive = request.form['title_give']
    genre_receive = request.form['genre_give']
    overview_receive = request.form['overview_give']
    nation_receive = request.form['nation_give']

    # DB에 삽입할 rating 만들기
    Mymovie_list = {
        'userid':userid_recive,
        'movieid':movieid_recieve,
        'title':title_receive,
        'genre':genre_receive,
        'overview':overview_receive,
        'nation':nation_receive
    }
    # reviews에 review 저장하기
    db.Mymovie_list.insert_one(Mymovie_list)
    # 성공 여부 & 성공 메시지 반환
    return jsonify({'result': 'success'})

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

@app.route('/countGenre', methods=['POST'])
def count_genre():
    genre_receive = request.form['genre_give']

    genre = db.MyGenre_list.find_one({'genre': genre_receive})

    new_like = genre['like'] + 1

    db.MyGenre_list.update_one({'genre': genre_receive}, {'$set': {'like': new_like}})

    return jsonify({'result': 'success'})


@app.route('/search', methods=['GET'])
def search_page():
    return render_template('search.html')

if __name__ == '__main__':
    app.run()
