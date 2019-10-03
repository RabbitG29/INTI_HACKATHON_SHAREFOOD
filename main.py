#-*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import pymysql
import json
import sys
from passlib.hash import sha256_crypt
from datetime import datetime

app = Flask(__name__)

conn = pymysql.connect(
	host='localhost',
	user='root',
	password='aksfnghafjs1',
	db='sharefood',
	charset='utf8',
	cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

@app.route('/')
def HellloWorld():
	return "Hello Flask!"

@app.route('/user',methods=['GET'])
def readUser():
	try:
		sql = "SELECT * from User"
		cursor.execute(sql)
		result = cursor.fetchall()
		return {"code": 0, "data":result}
	except Exception as e:
		print(e)

@app.route('/user',methods=['POST'])
def registerLocation():
	try:
		latitude = request.json['latitude']
		longitude = request.json['longitude']
		uniqueID = request.json['uniqueID']
		sql = "UPDATE Users SET latitude='%lf', longitude='%lf' WHERE uniqueID='%d'" % (latitude, longitude, uniqueID)
		cursor.execute(sql)
		conn.commit()
		return {"code": 0, "msg": "위치 등록이 완료되었습니다."}

	except Exceptioin as e:
		print(e)

@app.route('/register', methods=['POST'])
def register():
	try:
		id = request.json['id']
		passwd = request.json['password']
		name = request.json['name'] 
		phone = request.json['phone']
		
		h = sha256_crypt.hash(passwd) #password hasing
		sql = "SELECT id FROM User WHERE id = '%s'" % (id)
		print(sql)
		cursor.execute(sql)
		result = cursor.fetchall()
		print(result)
		if len(result) > 0: # 이미 존재하는 경우 !
			return {"code": -1, "msg": "존재하는 아이디입니다."}

		else: #회원가입 성공, DB에 USER 등록
			sql = "INSERT INTO User (id, password, name, phoneNumber) VALUES ('%s', '%s', '%s', '%s')" % (id, h, name, phone)
			print(sql)
			cursor.execute(sql)
			conn.commit()
			return {"code": 0, "msg": "회원가입이 완료되었습니다." }
	except Exception as e:
		print(e)
	return 1
	

@app.route('/login', methods=['POST'])
def login():
	id = request.json['id']
	passwd = request.json['password']
	try:	
		if id and passwd:
			sql = "SELECT password FROM User WHERE id = '%s'" % (id)
#print(sql)
			print(sql)	
			cursor.execute(sql)
			result = cursor.fetchall()
			print(result)			
			if len(result) > 0: 
				if sha256_crypt.verify(passwd, result[0]['password']): 
					return {"code": 0, "msg": "로그인이 성공하였습니다.", "token":"%s" %(result[0]['password']) } #token 추가해야 됨
				else :
					return {"code": -1, "msg": "비밀번호가 틀렸습니다."}
			else:
				return {"code": -1, "msg": "로그인이 실패했습니다." }
		else: 
			return -1 #login 실패
	
	except Exception as e:
		print(e)
		return {"code": -1, "msg": "에러발생!"}

@app.route('/food', methods=['GET'])
def readFoods():
	uniqueID = request.json['uniqueID']
	now = datetime.now()
	if uniqueID!=0:
		sql = "SELECT * from UsersFood WHERE uniqueID='%s' AND expiredAt > '%s'" % (uniqueID,now)
	else:
		sql = "SELECT * from UsersFood"
	print(sql)
	cursor.execute(sql)
	result = cursor.fetchall()
	return {"code":0, "data":result}

@app.route('/food', methods=['POST'])
def registerFood():
	name = request.json['name']
	categoryID = request.json['categoryID']
	owner = request.json['owner'] # 사용자의 고유키
	expired = request.json['expired']
	created = request.json['created']
	try:
		if name and categoryID:
			sql = "INSERT INTO Food (foodName, categoryID) VALUES ('%s','%s') ON DUPLICATE KEY UPDATE foodID=foodID" % (name, categoryID) # 중복 체크 한번에
			print(sql)
			cursor.execute(sql)
			result = cursor.fetchall()
			sql3 = "SELECT foodID from Food WHERE foodName='%s'" % (name)
			cursor.execute(sql3)
			resultID = cursor.fetchall()[0]['foodID']
			print(resultID)
			#conn.commit()
			#return {"code":0,"msg":"음식 등록이 성공하였습니다."}
		if owner:
			sql2 = "INSERT INTO UsersFood (uniqueID, foodID, expiredAt, createdAt) VALUES ('%s','%d','%s','%s')" % (owner, resultID, expired, created)
			print(sql2)
			cursor.execute(sql2)
			result2 = cursor.fetchall()
			conn.commit()
			return {"code":0, "msg":"음식 등록이 성공하였습니다."}

	except Exception as e:
		print(e)
		return {"code": -1, "msg":"음식 등록이 실패하였습니다."}

@app.route('/review', methods=['GET'])
def readReview():
	uniqueID = request.json['uniqueID']
	sql = "SELECT * FROM Review WHERE uniqueID='%s'" % (uniqueID)
	try:
		if uniqueID:
			cursor.execute(sql)
			result = cursor.fetchall()
			conn.commit()
			return {"code":0, "data":result}
	except Exception as e:
		print(e)

@app.route('/review', methods=['POST'])
def registerReview():
	sql = "SELECT uniqueID FROM User WHERE id = '%s'" % (request.json['id'])
	print(sql)
	cursor.execute(sql)
	result = cursor.fetchall()

	uniqueID = result[0]['uniqueID']
	content = request.json['content']
	star = request.json['star']
	try:
		if uniqueID and content and star:
			sql = "INSERT INTO Review (uniqueID, content, star) VALUES ('%d','%s','%d')" % (uniqueID, content, star)
			print(sql)
			cursor.execute(sql)
			result=cursor.fetchall()
			conn.commit()
			return {"code":0,"msg":"리뷰 등록이 성공하였습니다"}
	except Exception as e:
		print(e)
		return {"code":-1,"msg":"리뷰 등록이 실패하였습니다"}


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=3000)
