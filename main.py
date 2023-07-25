# coding: utf-8




#既成のモジュールをインポートする
import os
import flask
import sqlite3
import datetime
import pytz
from datetime import timedelta
from flask import Flask, render_template, request, url_for, redirect, session, flash, abort
from flask_paginate import Pagination, get_page_parameter




#管理者用パスワードを宣言する
ADMIN_PASSWORD = "secret"




#Flask本体を構築する
app = flask.Flask(__name__, static_folder="static", template_folder="templates")

#セッションキーを設定する
app.config["SECRET_KEY"] = "python_flask_chatbot__session_secret_key"








#「index」のURLエンドポイントを定義する
@app.route("/",      methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    row_num = 0


    session.clear()


    if   request.method == "POST":

         conn = sqlite3.connect("app_usrs.db")
         cur  = conn.cursor()

         sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
         cur.execute(sql1)
         conn.commit()


         sql2 = """SELECT usr_nm FROM users WHERE usr_nm=?;"""
         cur.execute(sql2, [request.form["username"]])

         for row in cur.fetchall():
             row_num = row_num + 1

         if row_num == 0:
            cur.close()
            conn.close()

            flash("そのユーザー名は登録されていません！")

            return render_template("index.html")


         sql3 = """SELECT usr_nm FROM users WHERE usr_nm=?;"""
         cur.execute(sql3, [request.form["password"]])

         for row in cur.fetchall():
             if row != request.form["password"]:
                cur.close()
                conn.close()

                flash("そのパスワードは間違っています！")

                return render_template("index.html")


         cur.close()
         conn.close()


         session["user_name"] = request.form["username"]
         session["logged_in"] = True
         app.permanent_session_lifetime = timedelta(minutes=30)


         return redirect(url_for("prompt"))


    else:

         return render_template("index.html")





#「usage」のURLエンドポイントを定義する
@app.route("/usage", methods=["GET"])
def usage():

    session.clear()


    return render_template("usage.html")




#「about」のURLエンドポイントを定義する
@app.route("/about", methods=["GET"])
def about():

    session.clear()


    return render_template("about.html")




#「signup」のURLエンドポイントを定義する
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

       conn = sqlite3.connect("app_usrs.db")
       cur  = conn.cursor()


       sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                   usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
       cur.execute(sql1)
       conn.commit()


       sql2 = """SELECT usr_nm FROM users WHERE usr_nm=?;"""
       cur.execute(sql2, [request.form["username"]])

       for row in cur.fetchall():
           if row == (request.form["username"],):
              flash("そのユーザー名は既に登録されています！")
              cur.close()
              conn.close()

              return render_template("signup.html")


       sql2 = """INSERT INTO users(usr_nm, psswrd) VALUES (?,?);"""
       cur.execute(sql2, (request.form["username"], request.form["password"]))
       conn.commit()

       cur.close()
       conn.close()

       session["user_name"] = request.form["username"]
       session["logged_in"] = True
       app.permanent_session_lifetime = timedelta(minutes=30)


       return redirect(url_for("prompt"))


    else:


       return render_template("signup.html")




#「signout」のURLエンドポイントを定義する
@app.route("/signout", methods=["GET", "POST"])
def signout():
    row_num = 0


    if   request.method == "POST":

         conn = sqlite3.connect("app_usrs.db")
         cur  = conn.cursor()

         sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
         cur.execute(sql1)
         conn.commit()


         sql2 = """SELECT usr_nm FROM users WHERE usr_nm=?;"""
         cur.execute(sql2, [request.form["username"]])

         for row in cur.fetchall():
             row_num = row_num + 1

         if row_num == 0:
            cur.close()
            conn.close()

            flash("そのユーザー名は登録されていません！")

            return render_template("signout.html")


         sql1 = """UPDATE users SET usr_nm="ERASED", psswrd="ERASED" WHERE usr_nm=? AND ml_addr=? AND psswrd=?;"""
         cur.execute(sql1, (request.form["username"], request.form["password"]))
         conn.commit()

         cur.close()
         conn.close()

         session.clear()

         return redirect(url_for("index"))

    else:

         return render_template("signout.html")




#「admin_login」のURLエンドポイントを定義する
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if   request.method == "POST":

         if ADMIN_PASSWORD != request.form["password"]:

             flash("そのパスワードは間違っています")

             return render_template("admin_login.html")


         session["is_admin"]  = True
         session["logged_in"] = True
         app.permanent_session_lifetime = timedelta(minutes=30)

         return redirect(url_for("admin_prompt"))

    else:

         return render_template("admin_login.html")





#「show_users」のURLエンドポイントを定義する
@app.route("/show_users", methods=["GET"])
def show_users():
    itms = []


    if request.method == "GET":

       if   "logged_in" not in session:
            
             return redirect(url_for("index"))

       elif  session["logged_in"] == False:

             return redirect(url_for("index"))


    if request.method == "GET":

       if  "is_admin" not in session:

            return redirect(url_for("index"))

       elif session["is_admin"] == False:

            return redirect(url_for("index"))


    conn = sqlite3.connect("app_usrs.db")
    cur  = conn.cursor()


    sql1 = """SELECT * From users;"""
    cur.execute(sql1)

    for row in cur.fetchall():
        itms.append(row)


    cur.close()
    conn.close()

    per_pg = 8
    pg     = request.args.get(get_page_parameter(), type=int, default=1)
    pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
    pgntn  = Pagination(page=pg, total=len(itms), per_page=per_pg, css_framework="bootstrap4")


    return render_template("show_users.html", pagination=pgntn, page_data=pg_dat)




#「show_attendance」のURLエンドポイントを定義する
@app.route("/show_attendance", methods=["GET"])
def show_attendance():
    itms = []


    if request.method == "GET":

       if   "logged_in" not in session:
            
             return redirect(url_for("index"))

       elif  session["logged_in"] == False:

             return redirect(url_for("index"))


    if request.method == "GET":

       if  "is_admin" not in session:

            return redirect(url_for("index"))

       elif session["is_admin"] == False:

            return redirect(url_for("index"))


       conn = sqlite3.connect("app_tmm.db")
       cur  = conn.cursor()


       sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL, bgn_dttm, end_dttm);"""
       cur.execute(sql1)
       conn.commit()


       sql2 = """SELECT * FROM attendance;"""
       cur.execute(sql2)

 
       for row in cur.fetchall():
           itms.append(row)


       cur.close()
       conn.close()


       per_pg = 8
       pg     = request.args.get(get_page_parameter(), type=int, default=1)
       pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
       pgntn  = Pagination(page=pg, total=len(itms), per_page=per_pg, css_framework="bootstrap4")


       return render_template("show_attendance.html", pagination=pgntn, page_data=pg_dat)




#「export_to_csv」のURLエンドポイントを定義する
@app.route("/export_to_csv", methods=["GET"])
def export_to_csv():
    itms = []


    if request.method == "GET":

       if   "logged_in" not in session:
            
             return redirect(url_for("index"))

       elif  session["logged_in"] == False:

             return redirect(url_for("index"))


    if request.method == "GET":

       if  "is_admin" not in session:

            return redirect(url_for("index"))

       elif session["is_admin"] == False:

            return redirect(url_for("index"))
       

       conn = sqlite3.connect("app_tmm.db")
       cur  = conn.cursor()


       sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL, bgn_dttm TEXT, end_dttm TEXT);"""
       cur.execute(sql1)
       conn.commit()


       sql2 = """SELECT * FROM attendance;"""
       cur.execute(sql2)

 
       for row in cur.fetchall():
           itms.append(row)


       cur.close()
       conn.close()


       per_pg = 8
       pg     = request.args.get(get_page_parameter(), type=int, default=1)
       pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
       pgntn  = Pagination(page=pg, total=len(itms), per_page=per_pg, css_framework="bootstrap4")


       return render_template("export_to_csv.html", pagination=pgntn, page_data=pg_dat)




#「prompt」のURLエンドポイントを定義する
@app.route("/prompt", methods=["GET", "POST"])
def prompt():
    itms = []


    if request.method == "GET":

       if  "logged_in" not in session:

            return redirect(url_for("index"))

       elif session["logged_in"] == False:

            return redirect(url_for("index"))

       else:

            return render_template("prompt.html", user_name=session["user_name"])


    if request.method == "POST":

       if  "logged_in" not in session:

            return redirect(url_for("index"))

       elif session["logged_in"] == False:

            return redirect(url_for("index"))

    conn = sqlite3.connect("app_tmm.db")
    cur  = conn.cursor()


    sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT, end_dttm TEXT);"""
    cur.execute(sql1)
    conn.commit()

    if   request.form["syutaikin"] == "出勤":
         flash("出勤時刻を記録しました")

         sql2 = """INSERT INTO attendance (usr_nm, bgn_dttm) VALUES (?, ?);"""
         crrnt_tm_in_asa_tky = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
         cur.execute(sql2, (session["user_name"], crrnt_tm_in_asa_tky))
         conn.commit()

         print(session["user_name"])
         print(crrnt_tm_in_asa_tky)


         cur.close()
         conn.close()


         return render_template("prompt.html", user_name=session["user_name"])




    if   request.form["syutaikin"] == "退勤":
         flash("退勤時刻を記録しました")

         sql3 = """INSERT INTO attendance(usr_nm, end_dttm) VALUES (?,?);"""
         crrnt_tm_in_asa_tky = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
         cur.execute(sql3, (session["user_name"], crrnt_tm_in_asa_tky))
         conn.commit()

         cur.close()
         conn.close()


         return render_template("prompt.html", user_name=session["user_name"])




#「admin_prompt」のURLエンドポイントを定義する
@app.route("/admin_prompt", methods=["GET"])
def admin_prompt():

    if request.method == "GET":

       if   "logged_in" not in session:
            
             return redirect(url_for("index"))

       elif  session["logged_in"] == False:

             return redirect(url_for("index"))


       if  "is_admin" not in session:

            return redirect(url_for("index"))

       elif session["is_admin"] == False:

            return redirect(url_for("index"))

    
       return render_template("admin_prompt.html")








#当該モジュールが実行起点かどうかを確認した上で、Flask本体を起動する
if __name__ == '__main__':
   app.run(debug=True, host="localhost", port=5000)