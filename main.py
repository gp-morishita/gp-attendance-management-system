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




#管理者用パスワード
ADMIN_PASSWORD = "secret"




#Flask本体を構築する
app = flask.Flask(__name__, static_folder="static", template_folder="templates")

#セッションキーを設定する
app.config["SECRET_KEY"] = "python_flask_chatbot__session_secret_key"








#「index」のURLURLエンドポイントを定義する
@app.route("/",      methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    row_num = 0


    session.clear()


    if   request.method == "POST":

         conn = sqlite3.connect("app_usrs.db")
         cur  = conn.cursor()

         sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, ml_addr TEXT NOT NULL, psswrd TEXT NOT NULL);"""
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
                                                   usr_nm TEXT NOT NULL, ml_addr TEXT NOT NULL, psswrd TEXT NOT NULL);"""
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


       sql2 = """INSERT INTO users(usr_nm, ml_addr, psswrd) VALUES (?, ?, ?);"""
       cur.execute(sql2, (request.form["username"], request.form["mailaddress"], request.form["password"]))
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
                                                     usr_nm TEXT NOT NULL, ml_addr TEXT NOT NULL, psswrd TEXT NOT NULL);"""
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


         sql1 = """UPDATE users SET usr_nm="ERASED", ml_addr="ERASED", psswrd="ERASED" WHERE usr_nm=? AND ml_addr=? AND psswrd=?;"""
         cur.execute(sql1, (request.form["username"], request.form["mailaddress"], request.form["password"]))
         conn.commit()

         cur.close()
         conn.close()

         session.clear()
         flash("またのご利用お待ちしております")

         return render_template("byebye.html")

    else:

         return render_template("signout.html")




#「login」のURLエンドポイントを定義する
@app.route("/login", methods=["GET", "POST"])
def login():
    row_num = 0


    if   request.method == "POST":

         conn = sqlite3.connect("app_usrs.db")
         cur  = conn.cursor()

         sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, ml_addr TEXT NOT NULL, psswrd TEXT NOT NULL);"""
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

            return render_template("login.html")


         sql3 = """SELECT usr_nm FROM users WHERE usr_nm=?;"""
         cur.execute(sql3, [request.form["password"]])

         for row in cur.fetchall():
             if row != request.form["password"]:
                cur.close()
                conn.close()

                flash("そのパスワードは間違っています！")

                return render_template("login.html")


         cur.close()
         conn.close()


         session["user_name"] = request.form["username"]
         session["logged_in"] = True
         app.permanent_session_lifetime = timedelta(minutes=30)


         return redirect(url_for("prompt"))


    else:

         return render_template("login.html")





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




#「logout」のURLエンドポイントを定義する
@app.route("/logout", methods=["GET"])
def logout():

    session.clear()

    flash("ログアウトしました")


    return render_template("logout.html")





#「show_users」のURLエンドポイントを定義する
@app.route("/show_users", methods=["GET"])
def show_users():
    itms = []


    if request.method == "GET":

       if   "logged_in" not in session:
            
             return redirect(url_for("login"))

       elif  session["logged_in"] == False:

             return redirect(url_for("login"))


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




#「show_images」のURLエンドポイントを定義する
@app.route("/show_images", methods=["GET"])
def show_images():
    itms = []


    if request.method == "GET":

       if  "logged_in" not in session:
            
            return redirect(url_for("login"))

       elif session["logged_in"] == False:

            return redirect(url_for("login"))


       conn = sqlite3.connect("app_imgs.db")
       cur  = conn.cursor()


       sql1 = """CREATE TABLE IF NOT EXISTS images (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                    orign_img_pth TEXT NOT NULL, gnrtd_img_pth TEXT NOT NULL);"""
       cur.execute(sql1)
       conn.commit()


       sql2 = """SELECT * FROM images;"""
       cur.execute(sql2)

 
       for row in cur.fetchall():
           itms.append(row[1])
           itms.append(row[2])


       cur.close()
       conn.close()


       per_pg = 8
       pg     = request.args.get(get_page_parameter(), type=int, default=1)
       pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
       pgntn  = Pagination(page=pg, total=len(itms), per_page=per_pg, css_framework="bootstrap4")


       return render_template("show_images.html", pagination=pgntn, page_data=pg_dat)




#「show_messages」のURLエンドポイントを定義する
@app.route("/show_messages", methods=["GET"])
def show_messages():
    itms = []

    if request.method == "GET":

       if   "logged_in" not in session:
            
             return redirect(url_for("login"))

       elif  session["logged_in"] == False:

             return redirect(url_for("login"))


       conn = sqlite3.connect("app_mssgs.db")
       cur  = conn.cursor()


       sql1 = """CREATE TABLE IF NOT EXISTS messages (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                      usr_nm TEXT NOT NULL, tm_stmp TEXT NOT NULL, orign_txts TEXT NOT NULL, gnrtd_txts TEXT NOT NULL);"""
       cur.execute(sql1)
       conn.commit()


       sql2 = """SELECT * FROM messages;"""
       cur.execute(sql2)


       for row in cur.fetchall():
           itms.append(row)

 
       cur.close()
       conn.close()


       per_pg = 8
       pg     = request.args.get(get_page_parameter(), type=int, default=1)
       pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
       pgntn  = Pagination(page=pg, total=len(itms), per_page=per_pg, css_framework="bootstrap4")


       return render_template("show_messages.html", pagination=pgntn, page_data=pg_dat)




#「show_results」のURLエンドポイントを定義する
@app.route("/show_results", methods=["GET"])
def show_results():
    itms = []

    if request.method == "GET":

       if   "logged_in" not in session:
            
             return redirect(url_for("login"))

       elif  session["logged_in"] == False:

             return redirect(url_for("login"))


       conn = sqlite3.connect("app_rslts.db")
       cur  = conn.cursor()


       sql1 = """CREATE TABLE IF NOT EXISTS results (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     tpc TEXT NOT NULL, cntxt TEXT NOT NULL,
                                                     txt_djst TEXT NOT NULL, txt_sntmnt TEXT NOT NULL, uttrnc_mdl TEXT NOT NULL);"""
       cur.execute(sql1)
       conn.commit()


       sql2 = """SELECT * FROM results;"""
       cur.execute(sql2)


       for row in cur.fetchall():
           itms.append(row)

 
       cur.close()
       conn.close()


       per_pg = 8
       pg     = request.args.get(get_page_parameter(), type=int, default=1)
       pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
       pgntn  = Pagination(page=pg, total=len(itms), per_page=per_pg, css_framework="bootstrap4")


       return render_template("show_results.html", pagination=pgntn, page_data=pg_dat)




#「prompt」のURLエンドポイントを定義する
@app.route("/prompt", methods=["GET", "POST"])
def prompt():

    if request.method == "GET":

       if  "logged_in" not in session:

            return redirect(url_for("login"))

       elif session["logged_in"] == False:

            return redirect(url_for("login"))

       else:

            return render_template("prompt.html", user_name=session["user_name"])


    if request.method == "POST":

       if  "logged_in" not in session:

            return redirect(url_for("login"))

       elif session["logged_in"] == False:

            return redirect(url_for("login"))


    if   request.form["syutaikin"] == "出勤":
         flash("出勤時刻を記録しました")

         return render_template("prompt.html", user_name=session["user_name"])

    if   request.form["syutaikin"] == "退勤":
         flash("退勤時刻を記録しました")

         return render_template("prompt.html", user_name=session["user_name"])




#「admin_prompt」のURLエンドポイントを定義する
@app.route("/admin_prompt", methods=["GET"])
def admin_prompt():

    if request.method == "GET":

       if  "logged_in" not in session:

            return redirect(url_for("login"))

       elif session["logged_in"] == False:

            return redirect(url_for("login"))

       else:

            return render_template("admin_prompt.html")




#当該モジュールが実行起点かどうかを確認した上で、Flask本体を起動する
if __name__ == '__main__':
   app.run(debug=True, host="localhost", port=5000)