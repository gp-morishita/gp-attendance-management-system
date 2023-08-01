# coding: utf-8


# 既成のモジュールをインポートする
import os
import flask
import sqlite3
import datetime
import pytz
import threading
import webbrowser
from datetime import timedelta
from flask import Flask, render_template, request, url_for, redirect, session, flash, send_file
from flask_paginate import Pagination, get_page_parameter


# 管理者用パスワードを宣言する
ADMIN_PASSWORD = "gp1192"

# ダウンロードファイルのパスを宣言する
DOWNLOAD_PATH = "cache_data/export_attendance.csv"

# Flask本体を構築する
app = flask.Flask(__name__, static_folder="static",
                  template_folder="templates")

# セッションキーを設定する
app.config["SECRET_KEY"] = "python-flask-application__session-secret-key"


# 「index」のURLエンドポイントを定義する
@app.route("/",      methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    row_num = 0

    session.clear()

    if request.method == "POST":

        conn = sqlite3.connect("app_usrs.db")
        cur = conn.cursor()

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

            flash("そのユーザーは登録されていません")

            return render_template("index.html")

        sql3 = """SELECT psswrd FROM users WHERE usr_nm=?;"""
        cur.execute(sql3, [request.form["username"]])

        for row in cur.fetchall():
            if row != (request.form["password"],):
                cur.close()
                conn.close()

                flash("そのパスワードは間違っています")

                return render_template("index.html")

        cur.close()
        conn.close()

        session["username"] = request.form["username"]
        session["is_logged_in"] = True
        app.permanent_session_lifetime = timedelta(minutes=30)

        return redirect(url_for("prompt"))

    else:

        return render_template("index.html")


# 「modify_user」のURLエンドポイントを定義する
@app.route("/modify_user", methods=["GET", "POST"])
def modify_user():
    itms = []
    row_num = 0

    if request.method == "GET":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrs.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM users WHERE id=?;"""

        cur.execute(sql2, [session["item-number"]])

        for row in cur.fetchall():
            itms.append(row)

        return render_template("modify_user.html", usr_info=itms)

    if request.method == "POST":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrs.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT usr_nm FROM users WHERE usr_nm=?;"""
        cur.execute(sql2, [request.form["username"]])

        for row in cur.fetchall():
            row_num = row_num + 1

        if row_num > 0:
            cur.close()
            conn.close()

            flash("そのユーザーは既に登録されています")

            return render_template("modify_user.html")

        sql3 = """UPDATE users SET usr_nm=?, psswrd=? WHERE id=?;"""
        cur.execute(
            sql3, (request.form["username"], request.form["password"], session["item-number"]))
        conn.commit()

        cur.close()
        conn.close()

        flash("そのユーザー情報を修正しました")

        return render_template("modify_user.html")


# 「register_user」のURLエンドポイントを定義する
@app.route("/register_user", methods=["GET", "POST"])
def register_user():

    if request.method == "GET":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("register_user.html")

    if request.method == "POST":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrs.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                   usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT usr_nm FROM users WHERE usr_nm=?;"""
        cur.execute(sql2, [request.form["username"]])

        for row in cur.fetchall():
            if row == (request.form["username"],):
                flash("そのユーザーは既に登録されています")
                cur.close()
                conn.close()

                return render_template("register_user.html")

        sql2 = """INSERT INTO users(usr_nm, psswrd) VALUES (?,?);"""
        cur.execute(sql2, (request.form["username"], request.form["password"]))
        conn.commit()

        cur.close()
        conn.close()

        flash("そのユーザーを登録しました")

        return render_template("register_user.html")


# 「erasure_user」のURLエンドポイントを定義する
@app.route("/erasure_user", methods=["GET", "POST"])
def erasure_user():
    row_num = 0

    if request.method == "GET":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("erasure_user.html")

    if request.method == "POST":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrs.db")
        cur = conn.cursor()

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

            flash("そのユーザーは登録されていません")

            return render_template("erasure_user.html")

        sql1 = """UPDATE users SET usr_nm="ERASED", psswrd="ERASED" WHERE usr_nm=?;"""
        cur.execute(sql1, [request.form["username"]])
        conn.commit()

        cur.close()
        conn.close()

        flash("そのユーザーを抹消しました")

        return render_template("erasure_user.html")


# 「admin_login」のURLエンドポイントを定義する
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    session.clear()

    if request.method == "GET":

        return render_template("admin_login.html")

    if request.method == "POST":

        if ADMIN_PASSWORD != request.form["password"]:

            flash("そのパスワードは間違っています")

            return render_template("admin_login.html")

        session["is_admin"] = True
        app.permanent_session_lifetime = timedelta(minutes=30)

        return redirect(url_for("admin_prompt"))


# 「show_users」のURLエンドポイントを定義する
@app.route("/show_users", methods=["GET", "POST"])
def show_users():
    itms = []

    if request.method == "GET":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrs.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * From users;"""
        cur.execute(sql2)

        for row in cur.fetchall():
            itms.append(row)

        cur.close()
        conn.close()

        per_pg = 8
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
        pgntn = Pagination(page=pg, total=len(
            itms), per_page=per_pg, css_framework="bootstrap4")

        return render_template("show_users.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":
        session["item-number"] = request.form["hidden-item-number"]
        print(session["item-number"])

        return redirect(url_for("modify_user"))


# 「show_attendance」のURLエンドポイントを定義する
@app.route("/show_attendance", methods=["GET"])
def show_attendance():
    itms = []

    if request.method == "GET":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM attendance;"""
        cur.execute(sql2)

        for row in cur.fetchall():
            itms.append(row)

        cur.close()
        conn.close()

        per_pg = 8
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
        pgntn = Pagination(page=pg, total=len(
            itms), per_page=per_pg, css_framework="bootstrap4")

        return render_template("show_attendance.html", pagination=pgntn, page_data=pg_dat)


# 「modify_attendance」のURLエンドポイントを定義する
@app.route("/modify_attendance", methods=["GET", "POST"])
def modify_attendance():
    row_num = 0

    if request.method == "GET":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("modify_attendance.html")

    if request.method == "POST":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT id FROM attendance WHERE id=?;"""
        cur.execute(sql2, [request.form["id"]])

        for row in cur.fetchall():
            row_num = row_num + 1

        if row_num == 0:

            flash("そのIDは存在しません")

            return render_template("modify_attendance.html")

        sql3 = """UPDATE attendance SET usr_nm=?, bgn_dttm=?, end_dttm=? WHERE id=?;"""
        cur.execute(
            sql3, (request.form["user_name"], request.form["begin_datetime"], request.form["end_datetime"], request.form["id"]))
        conn.commit()

        cur.close()
        conn.close()

        flash("そのIDに対応する情報を修正しました")

        return render_template("modify_attendance.html")


# 「erasure_attendance」のURLエンドポイントを定義する
@app.route("/erasure_attendance", methods=["GET", "POST"])
def erasure_attendance():
    row_num = 0

    if request.method == "GET":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("erasure_attendance.html")

    if request.method == "POST":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT id FROM attendance WHERE id=?;"""
        cur.execute(sql2, [request.form["id"]])

        for row in cur.fetchall():
            row_num = row_num + 1

        if row_num == 0:

            flash("そのIDは存在しません")

            return render_template("erasure_attendance.html")

        sql3 = """UPDATE attendance SET usr_nm="ERASED", bgn_dttm="ERASED", end_dttm="ERASED" WHERE id=?;"""
        cur.execute(sql3, [request.form["id"]])
        conn.commit()

        cur.close()
        conn.close()

        flash("そのIDに対応する情報を抹消しました")

        return render_template("erasure_attendance.html")


# 「export_to_csv」のURLエンドポイントを定義する
@app.route("/export_to_csv", methods=["GET"])
def export_to_csv():
    spr_itms = []

    if request.method == "GET":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        try:
            os.remove(DOWNLOAD_PATH)
        except FileNotFoundError:
            pass

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM attendance;"""
        cur.execute(sql2)

        for row in cur.fetchall():
            buf = str(row[0]) + ", " + row[1] + ", " + \
                row[2] + ", " + row[3] + "\n"
            spr_itms.append(buf)

        cur.close()
        conn.close()

        fl = open(DOWNLOAD_PATH, "x", encoding="UTF-8")

        fl.writelines(spr_itms)

        fl.close()

        return render_template("export_to_csv.html")


# 「download」のURLエンドポイントを定義する
@app.route("/download", methods=["GET"])
def download():

    return send_file(DOWNLOAD_PATH, as_attachment=True)


# 「prompt」のURLエンドポイントを定義する
@app.route("/prompt", methods=["GET", "POST"])
def prompt():
    row_num = 0
    row_id = 0

    if request.method == "GET":

        if "is_logged_in" not in session:

            return redirect(url_for("index"))

        elif session["is_logged_in"] == False:

            return redirect(url_for("index"))

        else:

            return render_template("prompt.html", user_name=session["username"])

    if request.method == "POST":

        if "is_logged_in" not in session:

            return redirect(url_for("index"))

        elif session["is_logged_in"] == False:

            return redirect(url_for("index"))

    conn = sqlite3.connect("app_tmm.db")
    cur = conn.cursor()

    sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
    cur.execute(sql1)
    conn.commit()

    if request.form["attendance"] == "出勤":

        sql2 = """SELECT * FROM attendance WHERE usr_nm=?;"""
        cur.execute(sql2, [session["username"]])

        for row in cur.fetchall():
            if row[3] == "UNDECIDED":

                flash("出勤日時は既に記録されています")
                return render_template("prompt.html", user_name=session["username"])

        for row in cur.fetchall():
            row_num = row_num + 1

        if row_num == 0:

            sql3 = """INSERT INTO attendance (usr_nm, bgn_dttm, end_dttm) VALUES (?, ?, ?);"""
            crrnt_tm_in_asa_tky = datetime.datetime.now(
                pytz.timezone("Asia/Tokyo"))
            cur.execute(sql3, (session["username"],
                        crrnt_tm_in_asa_tky, "UNDECIDED"))
            conn.commit()

            cur.close()
            conn.close()

            flash("出勤日時を記録しました")

            return render_template("prompt.html", user_name=session["username"])

    if request.form["attendance"] == "退勤":

        sql4 = """SELECT * FROM attendance WHERE usr_nm=?;"""
        cur.execute(sql4, [session["username"]])

        for row in cur.fetchall():

            if row[3] == "UNDECIDED":
                row_num = row_num + 1
                row_id = row[0]

        if row_num != 0:
            sql5 = """UPDATE attendance SET end_dttm=? WHERE id=?;"""
            crrnt_tm_in_asa_tky = datetime.datetime.now(
                pytz.timezone("Asia/Tokyo"))
            cur.execute(sql5, (crrnt_tm_in_asa_tky, row_id))
            conn.commit()

            cur.close()
            conn.close()

            flash("退勤日時を記録しました")

            return render_template("prompt.html", user_name=session["username"])

        else:

            flash("出勤日時が記録されていません")

            return render_template("prompt.html", user_name=session["username"])


# 「admin_prompt」のURLエンドポイントを定義する
@app.route("/admin_prompt", methods=["GET"])
def admin_prompt():

    if request.method == "GET":

        if "is_admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is_admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("admin_prompt.html")


def main():
    session.clear()


# 当該モジュールが実行起点かどうかを確認した上でFlask本体を起動する
if __name__ == '__main__':

    app.run(debug=True, host="localhost", port=5000)
