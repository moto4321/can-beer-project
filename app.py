from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
import certifi
from datetime import datetime # 파일명 생성을 위한 datetime 라이브러리 사용
ca = certifi.where()
#client = MongoClient('localhost', 27017)
client = MongoClient('mongodb+srv://test:sparta@cluster0.g33mv.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbcanbear


SECRET_KEY = 'SPARTA'
import jwt
import datetime
import hashlib


@app.route('/')
def home():
    content_list = list(db.content.find({}, {'_id': False}))

    for row in content_list:
        print(row['price'])
        row['one_min'] = format((min(row['price'], key=(lambda x: x['one'])))['one'], ',')
        row['four_min'] = format((min(row['price'], key=(lambda x: x['four'])))['four'], ',')

    return render_template('index.html', content_list=content_list)

@app.route('/api/writing', methods=['POST'])
def save_beer():
    content_list = list(db.content.find({}, {'_id': False}))
    beer_num = len(content_list)+1

    # 페이지에 저장된 형식 저장하기 위해서..
    beer_name = request.form['beer_name']
    beer_type = request.form['beer_type']
    beer_company= request.form['beer_company']
    beer_new_check=request.form['beer_new_check']

    #밑쪽으로는 파일 저장하기
    file = request.files["file_give"]
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    extantion = file.filename.split('.')[-1]
    filename = f'file-{mytime}'
    save_to = f'static/{filename}.{extantion}'
    file.save(save_to)

    #doc로 만들어 db에 저장하기
    doc = {
        'beer_num':beer_num,
        'beer_name':beer_name,
        'beer_type':beer_type,
        'beer_company':beer_company,
        'beer_new_check':beer_new_check,
        'file':f'{filename}.{extantion}'
    }
    db.content.insert_one(doc)

    return jsonify({'msg': '새 맥주 등록 완료'})


# 상품 디테일 페이지 GET라우트 (+ 리뷰 목록까지 가져오기)
@app.route('/detail/<beer_num>', methods=["GET"])
def beer_detail(beer_num):
    # print(beer_num)
    detail = db.content.find_one({'beer_num': int(beer_num)}, {'_id': False})
    reviews = list(db.review.find({'beer_num':int(beer_num), 'deleted': 0}, {'_id': False}))
    # print(reviews)
    # reviews = response
    return render_template('detailPage.html', detail=detail, reviews=reviews)

# 리뷰 작성 POST라우트 (+ 새로고침)
@app.route('/review', methods=["POST"])
def post_review():
    review_receive = request.form['review_give']
    star_receive = request.form['star_give']
    beer_num = request.form['beer_num']

    review_list = list(db.review.find({}, {'_id': False}))
    count = len(review_list) + 1

    data = {
        'review_num': count,
        'beer_num': int(beer_num),
        'review': review_receive,
        'star': star_receive,
        'deleted': 0
    }

    db.review.insert_one(data)
    return jsonify({'msg': '등록완료'})
    # return render_template('detailPage.html')

# 리뷰 삭제 POST라우트 (+ 새로고침)
@app.route('/remove/review', methods=["POST"])
def delete_review():
    review_num = request.form["review_num"]
    db.review.update_one({'review_num': int(review_num)},{'$set':{'deleted':1}})
    return jsonify({'msg': '삭제완료'})

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/layout_writing')
def layout_writing():
    msg = request.args.get("msg")
    return render_template('layout_writing.html', msg=msg)

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    phone_receive = request.form['phone_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    db.users.insert_one({'id': id_receive, 'pw': pw_hash, 'name': name_receive, 'phone':phone_receive})
    # db.users.insert_one({'id': id_receive, 'pw': pw_receive, 'nick': nickname_receive}) jwt쓸때 암호화 필요해서 이럼안됨

    return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.users.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        #token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

    # #회원가입시 아이디 중복체크
    # @app.route('/api/register', methods=['POST'])
    # def check_id():
    #     id_receive = request.form['id_give']
    #     user = db.users.find_one({'id': id_receive})
    #     if user is not None:  # 유저있으면
    #         return jsonify({'msg': '아이디 사용 불가'})
    #     else:
    #         return jsonify({'msg': '아이디 사용 가능'})



# [유저 정보 확인 API]
    # 로그인된 유저만 call 할 수 있는 API입니다.
    # 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
    # (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
    # @app.route('/api/nick', methods=['GET']) 토큰 필요한 주소 넣기
    # def api_valid():
    #     token_receive = request.cookies.get('mytoken')
    #     try:
    #         # token을 시크릿키로 디코딩합니다.
    #         # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
    #         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    #         print(payload)
    #
    #         # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
    #         # 여기에선 그 예로 닉네임을 보내주겠습니다.
    #         userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
    #         return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    #     except jwt.ExpiredSignatureError:
    #         # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
    #         return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    #     except jwt.exceptions.DecodeError:
    #         return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':
   app.run('0.0.0.0', port=3001, debug=True)
