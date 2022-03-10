import random

from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)
import os
from pymongo import MongoClient
import certifi
from datetime import datetime, timedelta # 파일명 생성을 위한 datetime 라이브러리 사용
#from datetime import datetime # 파일명 생성을 위한 datetime 라이브러리 사용

ca = certifi.where()
#client = MongoClient('localhost', 27017)
client = MongoClient('mongodb+srv://test:sparta@cluster0.g33mv.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbcanbear

SECRET_KEY = 'SPARTA'
import jwt
import hashlib

# 메인 페이지
@app.route('/')
def home():
    # 토큰 확인
    token_receive = request.cookies.get('mytoken')
    isLogin = False
    # 토큰이 있으면 로그인 플래그 설정
    if token_receive is not None:
        isLogin = True

    # 맥주 리스트 조회
    content_list = list(db.content.find({}, {'_id': False}))

    # 맥주별 최저가를 구해서 맥주 리스트에 추가
    for row in content_list:
        row['one_min'] = (min(row['price'], key=(lambda x: x['one'])))['one']
        row['four_min'] = (min(row['price'], key=(lambda x: x['four'])))['four']

        # 맥주별 리뷰를 조회해서 별점 평균값을 맥주 리스트에 추가
        review_list = list(db.review.find({'beer_num': row['beer_num']}, {'_id': False}))
        sum_star = 0
        if len(review_list) != 0:
            for review_row in review_list:
                sum_star += review_row['star']

            row['star_point'] = round(sum_star / len(review_list), 1)
        else:
            row['star_point'] = 0

        # 맥주 출시일과 오늘간 날짜를 비교하여 신상품 여부를 맥주 리스트에 추가
        beer_date = datetime.strptime(row['beer_date'], '%Y-%m-%d')
        diff_date = datetime.today() - beer_date
        if diff_date.days <= 30:
            row['new_beer'] = True
        else:
            row['new_beer'] = False

    # 정렬 타입 확인하여
    if 'align_type' in request.args:
        align_type = int(request.args.get('align_type'))
    else:
        align_type = 0

    # 맥주 리스트 정렬
    if align_type == 0: # 기본 정렬
        content_list = content_list
    elif align_type == 1:   # 최근 상품순
        content_list = sorted(content_list, key=(lambda x: x['beer_date']))
    elif align_type == 2:   # 오래된 상품순
        content_list = sorted(content_list, key=(lambda x: x['beer_date']), reverse=True)
    elif align_type == 3:   # 1개 가격 낮은순
        content_list = sorted(content_list, key=(lambda x: x['one_min']))
    elif align_type == 4:   # 1개 가격 높은순
        content_list = sorted(content_list, key=(lambda x: x['one_min']), reverse=True)
    elif align_type == 5:   # 4개 가격 낮은순
        content_list = sorted(content_list, key=(lambda x: x['four_min']))
    elif align_type == 6:   # 4개 가격 높은순
        content_list = sorted(content_list, key=(lambda x: x['four_min']), reverse=True)
    elif align_type == 7:   # 별점 높은순
        content_list = sorted(content_list, key=(lambda x: x['star_point']), reverse=True)
    elif align_type == 8:   # 별점 낮은순
        content_list = sorted(content_list, key=(lambda x: x['star_point']))
    elif align_type == 9:   #  랜덤
        random.shuffle(content_list)

    return render_template('index.html', content_list=content_list, isLogin=isLogin)


# @app.route('/api/index', methods=['GET'])
# def check_login():
#     token_receive = request.cookies.get('mytoken')
#     if token_receive is not None:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
#         return jsonify({'id': userinfo['id']})
#     else:
#         return jsonify({'fail':'fail'})




@app.route('/api/writing', methods=['POST'])
def save_beer():
    def checking(a):
        print(a)
        if a == "":
            a=0
            print("빈 문자열 발견")
        return (a)
    content_list = list(db.content.find({}, {'_id': False}))

    # updateState = False
    beer_num_old = request.form['beer_num_old']
    print('hello')
    print(beer_num_old)
    # 수정페이지에서 온거라면
    # if beer_num_old != '' or beer_num_old != None or beer_num_old != 'undefined' or beer_num_old != :
    updateState = True

    if beer_num_old == 'empty':
        updateState = False
    beer_num = len(content_list)+1

    # 페이지에 저장된 형식 저장하기 위해서..
    beer_name = request.form['beer_name']
    beer_type = request.form['beer_type']
    beer_company= request.form['beer_company']
    beer_date= request.form['beer_date']
    beer_country=request.form['beer_country']
    #가격정보 전부 가져오기

    mini_price_1 = int(checking(request.form['mini_price_1']))
    mini_price_4 = int(checking(request.form['mini_price_4']))
    gs_price_1 = int(checking(request.form['gs_price_1']))
    gs_price_4 = int(checking(request.form['gs_price_4']))
    cu_price_1 = int(checking(request.form['cu_price_1']))
    cu_price_4 = int(checking(request.form['cu_price_4']))
    seven_price_1 = int(checking(request.form['seven_price_1']))
    seven_price_4 = int(checking(request.form['seven_price_4']))
    nobrand_price_1 = int(checking(request.form['nobrand_price_1']))
    nobrand_price_4 = int(checking(request.form['nobrand_price_4']))
    dic_temp=[]
    if cu_price_1 != 0:
        dic_temp.append({'store': 'CU', 'one': cu_price_1, 'four':cu_price_4})
    if gs_price_1 != 0:
        dic_temp.append({'store': 'gs', 'one': gs_price_1, 'four':gs_price_4})
    if seven_price_1 != 0:
        dic_temp.append({'store': 'seven', 'one': seven_price_1, 'four':seven_price_4})
    if mini_price_1 != 0:
        dic_temp.append({'store': 'mini', 'one': mini_price_1, 'four':mini_price_4})
    if nobrand_price_1 != 0:
        dic_temp.append({'store': 'nobrand', 'one': nobrand_price_1, 'four':nobrand_price_4})


    #밑쪽으로는 파일 저장하기
    file = request.files["file_give"]
    today = datetime.now() #원래 dateime.now()
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
        'beer_date':beer_date,
        'beer_country': beer_country,
        'file':f'{filename}.{extantion}',
        'price':dic_temp
    }
    update_doc = {
        'beer_name': beer_name,
        'beer_type': beer_type,
        'beer_company': beer_company,
        'beer_date': beer_date,
        'beer_country': beer_country,
        'price': dic_temp
    }
    print(updateState) # True??? why
    print(beer_num_old) # undefined
    if updateState == True:
        db.content.update_one({'beer_num':int(beer_num_old)}, {'$set': update_doc})
        return jsonify({'msg': '맥주 정보 업데이트 완료'})
    else:
        db.content.insert_one(doc)
        return jsonify({'msg': '새 맥주 등록 완료'})


# 상품 디테일 페이지 GET라우트 (+ 리뷰 목록까지 가져오기)
@app.route('/detail/<beer_num>', methods=["GET"])
def beer_detail(beer_num):
    # print(beer_num)
    detail = db.content.find_one({'beer_num': int(beer_num)}, {'_id': False})
    reviews = list(db.review.find({'beer_num':int(beer_num), 'deleted': 0}, {'_id': False}))
    # print(reviews["star"])
    star_amt = 0
    star_avg = 0
    if len(reviews) != 0:
        for review in reviews:
            star_amt += review['star']
        star_avg = round(star_amt / len(reviews), 1)
    else:
        star_avg = 0


    # 현재 접속되어있는 사용자
    try:
        token_receive = request.cookies.get('mytoken')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
        current_id = userinfo['id']
    except jwt.exceptions.DecodeError:
        return render_template(
        'detailPage.html',
        detail=detail,
        reviews=reviews,
        beer_num=beer_num,
        star_avg=star_avg
    )

    # print(reviews)
    return render_template(
        'detailPage.html',
        detail=detail,
        reviews=reviews,
        beer_num=beer_num,
        current_id=current_id,
        star_avg=star_avg
    )



# 리뷰 작성 POST라우트 (+ 새로고침)
@app.route('/review', methods=["POST"])
def post_review():
    review_receive = request.form['review_give']
    star_receive = request.form['star_give']
    beer_num = request.form['beer_num']

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
    id = userinfo['id']

    review_list = list(db.review.find({}, {'_id': False}))
    count = len(review_list) + 1

    data = {
        'id': id,
        'review_num': count,
        'beer_num': int(beer_num),
        'review': review_receive,
        'star': int(star_receive),
        'deleted': 0
    }
    db.review.insert_one(data)
    return jsonify({'msg': '등록완료'})


#리뷰 삭제 POST라우트 (+ 새로고침)
@app.route('/remove/review', methods=["POST"])
def delete_review():
    review_num = request.form["review_num"]

    print(review_num)

    # db.review.update_one({'review_num': int(review_num)}, {'$set': {'deleted': 1}})
    # return jsonify({'msg': '삭제완료'})

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
    writer = db.review.find_one({'id':userinfo['id']})

    if userinfo['id'] == writer['id']:
        db.review.update_one({'review_num': int(review_num)}, {'$set': {'deleted': 1}})
        return jsonify({'msg': '삭제완료'})
    else:
        return jsonify({'msg': '삭제 불가'})




# 유저 정보 확인
@app.route('/api/detailPage', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 그리고 유저정보의 id 를 꺼내는 과정
        userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
        #return jsonify({'result': 'success', 'id': userinfo['id']})
        return render_template('detailPage.html', id=userinfo["id"])
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})



@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    msg = request.args.get("msg")
    return render_template('logout.html', msg=msg)

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
            # 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
            # 'exp': datetime.utcnow() + timedelta(seconds=10)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        #token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


#아이디 중복 레크
@app.route('/register/check_dup', methods=['POST'])
def check_dup():
    userid_receive = request.form['userid_give']
    exists = bool(db.users.find_one({"id": userid_receive}))
    return jsonify({'result': 'success', 'exists': exists})



if __name__ == '__main__':
   app.run('0.0.0.0', port=3001, debug=True)
