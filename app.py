from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
import certifi
from datetime import datetime # 파일명 생성을 위한 datetime 라이브러리 사용
ca = certifi.where()
#client = MongoClient('localhost', 27017)
client = MongoClient('mongodb+srv://test:sparta@cluster0.g33mv.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbcanbear

@app.route('/')
def home():
   return render_template('layout_writing.html')


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

if __name__ == '__main__':
   app.run('0.0.0.0', port=3001, debug=True)
