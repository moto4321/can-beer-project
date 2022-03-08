<<<<<<< HEAD
=======
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

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
>>>>>>> 5d8b937d5c06604664df7a3b9673e8834b735389
