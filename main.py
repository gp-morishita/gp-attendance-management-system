# coding: utf-8


# 既成のモジュールをインポートする
import os
import re
import csv
import datetime
import pytz
import flask
import sqlite3
from datetime import timedelta
from flask import Flask, render_template, request, url_for, redirect, session, flash, send_file
from flask_paginate import Pagination, get_page_parameter

# 管理者用パスワードを宣言する
ADMIN_PASS_WORD = "gp1192"

# インポートするCSVファイルの場所を宣言する
IMPORT_PATH = "./cache_data"

# エクスポートするCSVファイルの場所を宣言する
EXPORT_PATH = "cache_data/export_attendance.csv"

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

    if request.method == "GET":

        return render_template("index.html")

    if request.method == "POST":

        conn = sqlite3.connect("app_usrm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM users WHERE usr_nm=?;"""
        cur.execute(sql2, [request.form["user-name"]])

        for row in cur:
            if (row[1] == "----------------" and row[2] == "--------"):
                flash("そのユーザーは既に抹消されています")
                return render_template("index.html")

            row_num = row_num + 1

        if row_num == 0:
            cur.close()
            conn.close()

            flash("そのユーザーは登録されていません")

            return render_template("index.html")

        sql3 = """SELECT psswrd FROM users WHERE usr_nm=?;"""
        cur.execute(sql3, [request.form["user-name"]])

        for row in cur:
            if row != (request.form["pass-word"],):
                cur.close()
                conn.close()

                flash("そのパスワードは登録されていません")

                return render_template("index.html")

        cur.close()
        conn.close()

        session["user-name"] = request.form["user-name"]
        session["is-logged-in"] = True
        app.permanent_session_lifetime = timedelta(minutes=10)

        return redirect(url_for("prompt"))


# 「modify_user」のURLエンドポイントを定義する
@app.route("/modify_user", methods=["GET", "POST"])
def modify_user():
    itms = []
    usr_id_shrt = ""
    row_num = 0

    usr_id_lngth = len(str(session["modify-item-number"]))

    if usr_id_lngth > 4:
        usr_id_shrt = str(session["modify-item-number"])[0:4] + "..."

    else:
        usr_id_shrt = str(session["modify-item-number"])

    if request.method == "GET":

        if "is-admin" not in session:
            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:
            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM users WHERE id=?;"""

        cur.execute(sql2, [session["modify-item-number"]])

        for row in cur:
            itms.append(row)

        return render_template("modify_user.html", user_info=itms, user_id=usr_id_shrt)

    if request.method == "POST":

        if "is-admin" not in session:
            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:
            return redirect(url_for("admin_login"))

        if len(request.form["user-name"]) > 16:
            flash("ユーザー名は16文字以内にしてください")
            return render_template("modify_user.html", user_id=usr_id_shrt)

        if len(request.form["pass-word"]) > 8:
            flash("パスワードは8文字以内にしてください")
            return render_template("modify_user.html", user_id=usr_id_shrt)

        if (" " in request.form["user-name"] or "　" in request.form["user-name"]):
            flash("ユーザー名に半角・全角スペースは使えません")
            return render_template("modify_user.html", user_id=usr_id_shrt)

        if (" " in request.form["pass-word"] or "　" in request.form["pass-word"]):
            flash("パスワードに半角・全角スペースは使えません")
            return render_template("modify_user.html", user_id=usr_id_shrt)

        if (request.form["user-name"] == "--/--/--" or request.form["user-name"] == "--:--"):
            flash("ユーザー名を日付や時刻の形式にすることはできません")
            return render_template("modify_user.html", user_id=usr_id_shrt)

        if (request.form["pass-word"] == "--/--/--" or request.form["pass-word"] == "--:--"):
            flash("パスワードを日付や時刻の形式にすることはできません")
            return render_template("modify_user.html", user_id=usr_id_shrt)

        pttrn_not_usr_nm = r"(-)+"
        is_not_usr_nm = re.fullmatch(
            pttrn_not_usr_nm, request.form["user-name"])

        if is_not_usr_nm is not None:
            flash("ユーザー名を「 - 」のみにすることはできません")
            return render_template("modify_user.html", user_id=usr_id_shrt)

        pttrn_not_psswrd = r"(-)+"
        is_not_psswrd = re.fullmatch(
            pttrn_not_psswrd, request.form["pass-word"])

        if is_not_psswrd == True:
            flash("パスワードを「 - 」のみにすることはできません")

            return render_template("modify_user.html", user_id=usr_id_shrt)

        pttrn_dt1 = r"[0-9][0-9]-[0-9][0-9]"
        pttrn_dt2 = r"[0-9][0-9]/[0-9][0-9]"
        pttrn_tm = r"[0-9][0-9]:[0-9][0-9]"

        try:
            is_dt1 = re.fullmatch(pttrn_dt1, request.form["user-name"])
            is_dt2 = re.fullmatch(pttrn_dt2, request.form["user-name"])
            is_tm = re.fullmatch(pttrn_tm, request.form["user-name"])

            if (is_dt1 is not None or is_dt2 is not None or is_tm is not None):
                flash("ユーザー名を日付や時刻にすることはできません")
                return render_template("modify_user.html", user_id=usr_id_shrt)

        except IndexError:
            flash("入力エラー, おそらくカンマやスペースが原因と考えられます")
            return render_template("modify_user.html", user_id=usr_id_shrt)

        try:
            is_dt1 = re.fullmatch(pttrn_dt1, request.form["pass-word"])
            is_dt2 = re.fullmatch(pttrn_dt2, request.form["pass-word"])
            is_tm = re.fullmatch(pttrn_tm, request.form["pass-word"])

            if (is_dt1 is not None or is_dt2 is not None or is_tm is not None):
                flash("パスワードを日付や時刻にすることはできません")
                return render_template("modify_user.html", user_id=usr_id_shrt)

        except IndexError:
            flash("入力エラー, おそらくカンマやスペースが原因と考えられます")
            return render_template("modify_user.html", user_id=usr_id_shrt)

        conn = sqlite3.connect("app_usrm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM users WHERE usr_nm=?;"""
        cur.execute(sql2, [request.form["user-name"]])

        for row in cur:
            if (row[1] == "----------------" and row[2] == "--------"):
                flash("そのユーザーは既に抹消されています")
                return render_template("modify_user.html.html", user_id=usr_id_shrt)

            row_num = row_num + 1

        if row_num != 0:
            flash("そのユーザー名は既に登録されています", user_id=usr_id_shrt)
            cur.close()
            conn.close()

            return render_template("modify_user.html", user_id=usr_id_shrt)

        sql3 = """UPDATE users SET usr_nm=?, psswrd=? WHERE id=?;"""
        cur.execute(
            sql3, (request.form["user-name"], request.form["pass-word"], session["modify-item-number"]))
        conn.commit()

        cur.close()
        conn.close()

        flash("そのユーザー情報を修正しました")

        return render_template("modify_user.html", user_id=usr_id_shrt)


# 「register_user」のURLエンドポイントを定義する
@app.route("/register_user", methods=["GET", "POST"])
def register_user():

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("register_user.html")

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                   usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        if len(request.form["user-name"]) > 16:
            flash("ユーザー名は16文字以内にしてください")
            return render_template("register_user.html")

        if len(request.form["pass-word"]) > 8:
            flash("パスワードは8文字以内にしてください")
            return render_template("register_user.html")

        if (" " in request.form["user-name"] or "　" in request.form["user-name"]):
            flash("ユーザー名に半角・全角スペースは使えません")
            return render_template("register_user.html")

        if (" " in request.form["pass-word"] or "　" in request.form["pass-word"]):
            flash("パスワードに半角・全角スペースは使えません")
            return render_template("register_user.html")

        if (request.form["user-name"] == "--/--/--" or request.form["user-name"] == "--:--"):
            flash("日付や時刻の形式をユーザー名にすることはできません")
            return render_template("register_user.html")

        if (request.form["pass-word"] == "--/--/--" or request.form["pass-word"] == "--:--"):
            flash("日付や時刻の形式をパスワードにすることはできません")
            return render_template("register_user.html")

        pttrn_not_usr_nm = r"(-)+"
        is_not_usr_nm = re.fullmatch(
            pttrn_not_usr_nm, request.form["user-name"])

        if is_not_usr_nm is not None:
            flash("ユーザー名を「 - 」のみにすることはできません")
            return render_template("register_user.html")

        pttrn_not_psswrd = r"(-)+"
        is_not_psswrd = re.fullmatch(
            pttrn_not_psswrd, request.form["pass-word"])

        if is_not_psswrd == True:
            flash("パスワードを「 - 」のみにすることはできません")
            return render_template("register_user.html")

        pttrn_dt1 = r"[0-9][0-9]-[0-9][0-9]"
        pttrn_dt2 = r"[0-9][0-9]/[0-9][0-9]"
        pttrn_tm = r"[0-9][0-9]:[0-9][0-9]"

        try:
            is_dt1 = re.fullmatch(pttrn_dt1, request.form["user-name"])
            is_dt2 = re.fullmatch(pttrn_dt2, request.form["user-name"])
            is_tm = re.fullmatch(pttrn_tm, request.form["user-name"])

            if (is_dt1 is not None or is_dt2 is not None or is_tm is not None):
                flash("ユーザー名を日付や時刻にすることはできません")
                return render_template("register_user.html")

        except IndexError:
            flash("入力エラー, おそらくカンマやスペースが原因と考えられます")
            return render_template("register_user.html")

        try:
            is_dt1 = re.fullmatch(pttrn_dt1, request.form["pass-word"])
            is_dt2 = re.fullmatch(pttrn_dt2, request.form["pass-word"])
            is_tm = re.fullmatch(pttrn_tm, request.form["pass-word"])

            if (is_dt1 is not None or is_dt2 is not None or is_tm is not None):
                flash("パスワードを日付や時刻にすることはできません")
                return render_template("register_user.html")

        except IndexError:
            flash("入力エラー, おそらくカンマやスペースが原因と考えられます")
            return render_template("register_user.html")

        sql2 = """SELECT usr_nm FROM users WHERE usr_nm=?;"""
        cur.execute(sql2, [request.form["user-name"]])

        for row in cur:
            if row == (request.form["user-name"],):
                flash("そのユーザー名は既に登録されています")
                cur.close()
                conn.close()

                return render_template("register_user.html")

        sql3 = """INSERT INTO users(usr_nm, psswrd) VALUES (?,?);"""
        cur.execute(
            sql3, (request.form["user-name"], request.form["pass-word"]))
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

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("erasure_user.html")

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM users WHERE usr_nm=?;"""
        cur.execute(sql2, [request.form["user-name"]])

        for row in cur:
            if (row[1] == "----------------" and row[2] == "--------"):
                flash("そのユーザーは既に抹消されています")
                return render_template("erasure_user.html")

            row_num = row_num + 1

        if row_num == 0:
            cur.close()
            conn.close()

            flash("そのユーザーは登録されていません")

            return render_template("erasure_user.html")

        sql1 = """UPDATE users SET usr_nm="----------------", psswrd="--------" WHERE usr_nm=?;"""
        cur.execute(sql1, [request.form["user-name"]])
        conn.commit()

        cur.close()
        conn.close()

        flash("そのユーザーを抹消しました")

        return render_template("erasure_user.html")


# 「erasure_user2」のURLエンドポイントを定義する
@app.route("/erasure_user2", methods=["GET", "POST"])
def erasure_user2():
    usr_id_shrt = ""
    row_num = 0

    usr_id_lngth = len(str(session["erasure-item-number"]))

    if usr_id_lngth > 4:
        usr_id_shrt = str(session["erasure-item-number"])[0:4] + "..."

    else:
        usr_id_shrt = str(session["erasure-item-number"])

    if request.method == "GET":

        if "is-admin" not in session:
            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:
            return redirect(url_for("admin_login"))

        return render_template("erasure_user2.html", user_id=usr_id_shrt)

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM users WHERE id=?;"""
        cur.execute(sql2, [session["erasure-item-number"]])

        for row in cur:
            if (row[1] == "----------------" and row[2] == "--------"):
                flash("そのユーザーは既に抹消されています")
                return render_template("erasure_user2.html", user_id=usr_id_shrt)

            row_num = row_num + 1

        if row_num == 0:
            cur.close()
            conn.close()

            flash("そのユーザーは登録されていません")

            return render_template("erasure_user2.html", user_id=usr_id_shrt)

        sql1 = """UPDATE users SET usr_nm="----------------", psswrd="--------" WHERE id=?;"""
        cur.execute(sql1, [session["erasure-item-number"]])
        conn.commit()

        cur.close()
        conn.close()

        flash("そのユーザーを抹消しました")

        return render_template("erasure_user2.html", user_id=usr_id_shrt)


# 「admin_login」のURLエンドポイントを定義する
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    session.clear()

    if request.method == "GET":

        return render_template("admin_login.html")

    if request.method == "POST":

        if ADMIN_PASS_WORD != request.form["pass-word"]:

            flash("そのパスワードは登録されていません")

            return render_template("admin_login.html")

        session["is-admin"] = True
        app.permanent_session_lifetime = timedelta(minutes=10)

        return redirect(url_for("admin_prompt"))


# 「show_users」のURLエンドポイントを定義する
@app.route("/show_users", methods=["GET", "POST"])
def show_users():
    itms = []

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_usrm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * From users;"""
        cur.execute(sql2)

        for row in cur:
            itms.append(row)

        cur.close()
        conn.close()

        per_pg = 40
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
        pgntn = Pagination(page=pg, total=len(
            itms), per_page=per_pg, css_framework="bootstrap4")

        return render_template("show_users.html", page_data=pg_dat, pagination=pgntn)

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        session["modify-item-number"] = request.form["hidden-modify-item-number"]
        session["erasure-item-number"] = request.form["hidden-erasure-item-number"]

        if session["modify-item-number"] != "none":
            return redirect(url_for("modify_user"))

        elif session["erasure-item-number"] != "none":
            return redirect(url_for("erasure_user2"))


# 「show_attendance」のURLエンドポイントを定義する
@app.route("/show_attendance", methods=["GET", "POST"])
def show_attendance():
    itms = []

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL , bgn_dttm TEXT NOT NULL , end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM attendance;"""
        cur.execute(sql2)

        for row in cur:
            itms.append(row)

        cur.close()
        conn.close()

        per_pg = 40
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = itms[(pg - 1) * per_pg: pg * per_pg]
        pgntn = Pagination(page=pg, total=len(
            itms), per_page=per_pg, css_framework="bootstrap4")

        return render_template("show_attendance.html", pagination=pgntn, page_data=pg_dat)

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        session["modify-item-number"] = request.form["hidden-modify-item-number"]
        session["erasure-item-number"] = request.form["hidden-erasure-item-number"]

        if session["modify-item-number"] != "none":
            return redirect(url_for("modify_attendance"))

        elif session["erasure-item-number"] != "none":
            return redirect(url_for("erasure_attendance2"))


# 「modify_attendance」のURLエンドポイントを定義する
@app.route("/modify_attendance", methods=["GET", "POST"])
def modify_attendance():
    itms1 = []
    itms2 = []
    attndnc_id_shrt = ""

    attndnc_id_lngth = len(str(session["modify-item-number"]))

    if attndnc_id_lngth > 4:
        attndnc_id_shrt = str(session["modify-item-number"])[0:4] + "..."

    else:
        attndnc_id_shrt = str(session["modify-item-number"])

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL , bgn_dttm TEXT NOT NULL , end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM attendance WHERE id=?;"""
        cur.execute(sql2, [session["modify-item-number"]])

        for row in cur:
            itms1.append(row)

        for itm in itms1:
            bgn_dttm_frmttd1 = itm[2].replace(' ', 'T')
            end_dttm_frmttd1 = itm[3].replace(' ', 'T')
            bgn_dttm_frmttd2 = bgn_dttm_frmttd1.replace('/', '-')
            end_dttm_frmttd2 = end_dttm_frmttd1.replace('/', '-')
            itms2.append([itm[0], itm[1], bgn_dttm_frmttd2, end_dttm_frmttd2])

        cur.close()
        conn.close()

        return render_template("modify_attendance.html", attendance_info=itms2, attndnc_id=attndnc_id_shrt)

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        if 16 < len(request.form["user-name"]):
            flash("ユーザー名は16文字以内にしてください")

            return render_template("modify_attendance.html", attndnc_id=attndnc_id_shrt)

        if (" " in request.form["user-name"] or "　" in request.form["user-name"]):
            flash("ユーザー名に半角・全角スペースは使えません", attndnc_id=attndnc_id_shrt)

            return render_template("modify_attendance.html")

        pttrn_not_usr_nm = r"(-)+"
        is_not_usr_nm = re.fullmatch(
            pttrn_not_usr_nm, request.form["user-name"])

        if is_not_usr_nm is not None:
            flash("ユーザー名を「 - 」のみにすることはできません")

            return render_template("modify_attendance.html", attndnc_id=attndnc_id_shrt)

        bgn_dttm_tmp = datetime.datetime.strptime(
            request.form["begin-datetime"], "%Y-%m-%dT%H:%M")
        end_dttm_tmp = datetime.datetime.strptime(
            request.form["end-datetime"], "%Y-%m-%dT%H:%M")

        if bgn_dttm_tmp > end_dttm_tmp:
            flash("退勤日時を出勤日時よりも前にすることはできません")
            return render_template("modify_attendance.html", attndnc_id=attndnc_id_shrt)

        if bgn_dttm_tmp == end_dttm_tmp:
            flash("出勤日時と退勤日時を同時にすることはできません")
            return render_template("modify_attendance.html", attndnc_id=attndnc_id_shrt)

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL , bgn_dttm TEXT NOT NULL , end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        rqst_bgn_dttm_frmttd1 = request.form["begin-datetime"].replace(" ", "")
        rqst_end_dttm_frmttd1 = request.form["end-datetime"].replace(" ", "")
        rqst_bgn_dttm_frmttd2 = rqst_bgn_dttm_frmttd1.replace("T", " ")
        rqst_end_dttm_frmttd2 = rqst_end_dttm_frmttd1.replace("T", " ")
        rqst_bgn_dttm_frmttd3 = rqst_bgn_dttm_frmttd2.replace("-", "/")
        rqst_end_dttm_frmttd3 = rqst_end_dttm_frmttd2.replace("-", "/")

        sql2 = """UPDATE attendance SET usr_nm=?, bgn_dttm=?, end_dttm=? WHERE id=?;"""
        cur.execute(sql2, (request.form["user-name"], rqst_bgn_dttm_frmttd3,
                    rqst_end_dttm_frmttd3, session["modify-item-number"]))
        conn.commit()

        cur.close()
        conn.close()

        flash("勤怠情報を修正しました")

        return render_template("modify_attendance.html", attndnc_id=attndnc_id_shrt)


# 「register_attendance」のURLエンドポイントを定義する
@app.route("/register_attendance", methods=["GET", "POST"])
def register_attendance():
    row_num = 0

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("register_attendance.html")

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        if 16 < len(request.form["user-name"]):
            flash("ユーザー名は16文字以内にしてください")

            return render_template("register_attendance.html")

        if (" " in request.form["user-name"] or "　" in request.form["user-name"]):
            flash("ユーザー名に半角・全角スペースは使えません")

            return render_template("register_attendance.html")

        pttrn_not_usr_nm = r"(-)+"
        is_not_usr_nm = re.fullmatch(
            pttrn_not_usr_nm, request.form["user-name"])

        if is_not_usr_nm is not None:
            flash("ユーザー名を「 - 」のみにすることはできません")

            return render_template("register_attendance.html")

        bgn_dttm_tmp = datetime.datetime.strptime(
            request.form["begin-datetime"], "%Y-%m-%dT%H:%M")
        end_dttm_tmp = datetime.datetime.strptime(
            request.form["end-datetime"], "%Y-%m-%dT%H:%M")

        if bgn_dttm_tmp > end_dttm_tmp:
            flash("退勤日時を出勤日時よりも前にすることはできません")
            return render_template("modify_attendance.html")

        if bgn_dttm_tmp == end_dttm_tmp:
            flash("出勤日時と退勤日時を同時にすることはできません")
            return render_template("modify_attendance.html")

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL , bgn_dttm TEXT NOT NULL , end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        rqst_bgn_dttm_frmttd1 = request.form["begin-datetime"].replace(" ", "")
        rqst_end_dttm_frmttd1 = request.form["end-datetime"].replace(" ", "")
        rqst_bgn_dttm_frmttd2 = rqst_bgn_dttm_frmttd1.replace("T", " ")
        rqst_end_dttm_frmttd2 = rqst_end_dttm_frmttd1.replace("T", " ")
        rqst_bgn_dttm_frmttd3 = rqst_bgn_dttm_frmttd2.replace("-", "/")
        rqst_end_dttm_frmttd3 = rqst_end_dttm_frmttd2.replace("-", "/")

        sql2 = """SELECT * FROM attendance WHERE usr_nm=? AND bgn_dttm=? AND end_dttm=?;"""
        cur.execute(
            sql2, (request.form["user-name"], rqst_bgn_dttm_frmttd3, rqst_end_dttm_frmttd3))

        for row in cur:
            if (row[1] == "----------------" and row[2] == "--------"):
                flash("そのユーザーは既に抹消されています")
                return render_template("register_attendance.html")

        if row_num > 0:
            flash("その勤怠情報は既に記録されています")
            return render_template("register_attendance.html")

        sql3 = """INSERT INTO attendance (usr_nm, bgn_dttm, end_dttm) VALUES (?, ?, ?);"""
        cur.execute(
            sql3, (request.form["user-name"], rqst_bgn_dttm_frmttd3, rqst_end_dttm_frmttd3))
        conn.commit()

        cur.close()
        conn.close()

        flash("勤怠情報を記録しました")

        return render_template("register_attendance.html")


# 「erasure_attendance」のURLエンドポイントを定義する
@app.route("/erasure_attendance", methods=["GET", "POST"])
def erasure_attendance():
    row_num = 0

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("erasure_attendance.html")

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM attendance WHERE id=?;"""
        cur.execute(sql2, [request.form["id"]])

        for row in cur:
            if (row[1] == "----------------" or row[2] == "--/--/-- --:--" or row[3] == "--/--/-- --:--"):
                flash("その打刻は既に抹消されているか, 無効です")
                return render_template("erasure_attendance.html")

            row_num = row_num + 1

        if row_num == 0:
            flash("その打刻は登録されていません")
            return render_template("erasure_attendance.html")

        sql3 = """UPDATE attendance SET usr_nm="----------------", bgn_dttm="--/--/-- --:--", end_dttm="--/--/-- --:--" WHERE id=?;"""
        cur.execute(sql3, [request.form["id"]])
        conn.commit()

        cur.close()
        conn.close()

        flash("その打刻を抹消しました")

        return render_template("erasure_attendance.html")


# 「erasure_attendance2」のURLエンドポイントを定義する
@app.route("/erasure_attendance2", methods=["GET", "POST"])
def erasure_attendance2():
    usr_id_shrt = ""
    row_num = 0

    usr_id_lngth = len(str(session["erasure-item-number"]))

    if usr_id_lngth > 4:
        usr_id_shrt = str(session["erasure-item-number"])[0:4] + "..."

    else:
        usr_id_shrt = str(session["erasure-item-number"])

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("erasure_attendance2.html", user_id=usr_id_shrt)

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT * FROM attendance WHERE id=?;"""
        cur.execute(sql2, [session["erasure-item-number"]])

        for row in cur:
            if (row[1] == "----------------" or row[2] == "--/--/-- --:--" or row[3] == "--/--/-- --:--"):
                flash("その打刻は既に抹消されているか, 無効です")
                return render_template("erasure_attendance2.html", user_id=usr_id_shrt)

            row_num = row_num + 1

        if row_num == 0:
            flash("その打刻は登録されていません")
            return render_template("erasure_attendance2.html", user_id=usr_id_shrt)

        sql3 = """UPDATE attendance SET usr_nm="----------------", bgn_dttm="--/--/-- --:--", end_dttm="--/--/-- --:--" WHERE id=?;"""
        cur.execute(sql3, [session["erasure-item-number"]])
        conn.commit()

        cur.close()
        conn.close()

        flash("その打刻を抹消しました")

        return render_template("erasure_attendance2.html", user_id=usr_id_shrt)


# 「import_from_csv」のURLエンドポイントを定義する
@app.route("/import_from_csv", methods=["GET", "POST"])
def import_from_csv():
    itms = []

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("import_from_csv.html")

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        csv_file = request.files["upload-file"]
        csv_file.save(os.path.join(IMPORT_PATH, csv_file.filename))

        open_csv = open(os.path.join(
            IMPORT_PATH, csv_file.filename), "r", encoding="UTF-8")
        read_csv = csv.reader(open_csv)

        for row in read_csv:
            if 4 < len(row):
                flash("CSVファイル内のデータの列数が一致しません")
                return render_template("import_from_csv.html")

            if row[0] == "":
                flash("ユーザー名が入力されていません")
                return render_template("import_from_csv.html")

            if (row[1] == "" or row[2] == "" or row[3] == ""):
                flash("日付や時刻が入力されていません")
                return render_template("import_from_csv.html")

            if len(row[0]) > 16:
                flash("ユーザー名の長さが16文字を超えています")
                return render_template("import_from_csv.html")

            if (row[0] == "--/--/--" or row[0] == "--:--"):
                flash("ユーザー名が日付や時刻の形式になっています")
                return render_template("import_from_csv.html")

            if (" " in row[0] or "　" in row[0]):
                flash("ユーザー名に半角・全角スペースが含まれています")
                return render_template("import_from_csv.html")

            pttrn_dt = r"[0-9][0-9][0-9][0-9]/[0-1][1-2]/[0-3][1-9]"
            pttrn_tm = r"[0-2][0-3]:[0-5][0-9]"

            try:
                is_dt = re.fullmatch(pttrn_dt, row[1])
                is_tm1 = re.fullmatch(pttrn_tm, row[2])
                is_tm2 = re.fullmatch(pttrn_tm, row[3])

                if (is_dt is not None or is_tm1 is not None or is_tm2 is not None):
                    flash("日付や時刻が間違っているか, データが欠落しています")
                    return render_template("import_from_csv.html")

            except IndexError:
                flash("入力エラー, おそらくカンマやスペースが原因と考えられます")
                return render_template("import_from_csv.html")

            sql2 = """CREATE TABLE IF NOT EXISTS attendance_csv (usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
            cur.execute(sql2)
            conn.commit()

            sql3 = """INSERT INTO attendance_csv (usr_nm, bgn_dttm, end_dttm) VALUES (?, ?, ?);"""
            cur.execute(
                sql3, (row[0], (row[1] + " " + row[2]), (row[1] + " " + row[3])))
            conn.commit()

        sql4 = """SELECT usr_nm, bgn_dttm, end_dttm FROM attendance
          WHERE usr_nm <> "----------------" OR bgn_dttm <> "--/--/-- --:--" OR end_dttm <> "--/--/-- --:--"
              UNION  SELECT usr_nm, bgn_dttm, end_dttm FROM attendance_csv
                WHERE usr_nm <> "----------------" OR bgn_dttm <> "--/--/-- --:--" OR end_dttm <> "--/--/-- --:--";"""
        cur.execute(sql4)
        conn.commit()

        for row in cur:
            itms.append(row)

        sql5 = """DROP TABLE attendance;"""
        cur.execute(sql5)
        conn.commit()

        sql6 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql6)
        conn.commit()

        for itm in itms:
            sql7 = """INSERT INTO attendance (usr_nm, bgn_dttm, end_dttm) VALUES (?, ?, ?);"""
            cur.execute(sql7, (itm[0], itm[1], itm[2]))
            conn.commit()

        sql8 = """DROP TABLE attendance_csv;"""
        cur.execute(sql8)
        conn.commit()

        cur.close()
        conn.close()

        open_csv.close()

        flash("CSVファイルをインポートしました")

        return render_template("import_from_csv.html")


# 「export_to_csv」のURLエンドポイントを定義する
@app.route("/export_to_csv", methods=["GET", "POST"])
def export_to_csv():
    bgn_dttm = []
    end_dttm = []
    itms = []

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("export_to_csv.html")

    if request.method == "POST":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        try:
            os.remove(EXPORT_PATH)
        except FileNotFoundError:
            pass

        conn = sqlite3.connect("app_tmm.db")
        cur = conn.cursor()

        sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql1)
        conn.commit()

        sql2 = """SELECT usr_nm, bgn_dttm, end_dttm FROM attendance
                  WHERE usr_nm <> "----------------" OR bgn_dttm <> "--/--/-- --:--" OR end_dttm <> "--/--/-- --:--";"""
        cur.execute(sql2)

        for row in cur:

            if (row[0] == "----------------" or row[1] == "--/--/-- --:--" or row[2] == "--/--/-- --:--"):
                continue

            usr_nm = row[0]

            bgn_dttm = row[1].split(" ")
            end_dttm = row[2].split(" ")

            bgn_dt = bgn_dttm[0]
            bgn_dt_frmttd = bgn_dt.replace('-', '/')

            bgn_tm = bgn_dttm[1]
            end_tm = end_dttm[1]

            buf = usr_nm + "," + bgn_dt_frmttd + "," + bgn_tm + "," + end_tm + "\n"
            itms.append(buf)

        cur.close()
        conn.close()

        fl = open(EXPORT_PATH, "x", encoding="UTF-8")

        fl.writelines(itms)

        fl.close()

        flash("CSVファイルをエクスポートしました")

        return send_file(EXPORT_PATH, as_attachment=True)


# 「prompt」のURLエンドポイントを定義する
@app.route("/prompt", methods=["GET", "POST"])
def prompt():
    # past_bgn_dttm = ""
    prsnt_bgn_dttm_hr = 0
    prsnt_end_dttm_hr = 0
    row_num = 0
    row_id = 0

    if request.method == "GET":

        if "is-logged-in" not in session:

            return redirect(url_for("index"))

        elif session["is-logged-in"] == False:

            return redirect(url_for("index"))

        else:

            return render_template("prompt.html", user_name=session["user-name"])

    if request.method == "POST":

        if "is-logged-in" not in session:

            return redirect(url_for("index"))

        elif session["is-logged-in"] == False:

            return redirect(url_for("index"))

    conn = sqlite3.connect("app_tmm.db")
    cur = conn.cursor()

    sql1 = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
    cur.execute(sql1)
    conn.commit()

    if request.form["attendance"] == "出勤":

        sql2 = """SELECT * FROM attendance WHERE usr_nm=?;"""
        cur.execute(sql2, [session["user-name"]])

        for row in cur:
            if row[3] == "--/--/-- --:--":

                flash("出勤日時は既に記録されています")
                return render_template("prompt.html", user_name=session["user-name"])

        prsnt_bgn_dttm = datetime.datetime.now(
            pytz.timezone("Asia/Tokyo"))

        if (prsnt_bgn_dttm.minute >= 0 and prsnt_bgn_dttm.minute <= 29):
            prsnt_bgn_dttm_min = 30
            prsnt_bgn_dttm_hr = prsnt_bgn_dttm.hour

        elif (prsnt_bgn_dttm.minute >= 30 and prsnt_bgn_dttm.minute <= 59):
            prsnt_bgn_dttm_min = 0
            prsnt_bgn_dttm_hr = prsnt_bgn_dttm.hour + 1

        bgn_dttm_amndd = prsnt_bgn_dttm.replace(
            hour=prsnt_bgn_dttm_hr, minute=prsnt_bgn_dttm_min, second=0, microsecond=0)

        prsnt_bgn_dttm_frmttd = datetime.datetime.strftime(
            bgn_dttm_amndd, "%Y/%m/%d %H:%M")

        sql2 = """INSERT INTO attendance (usr_nm, bgn_dttm, end_dttm) VALUES (?, ?, ?);"""
        cur.execute(
            sql2, (session["user-name"], prsnt_bgn_dttm_frmttd, "--/--/-- --:--"))
        conn.commit()

        cur.close()
        conn.close()

        flash("出勤日時を記録しました")

        return render_template("prompt.html", user_name=session["user-name"])

    if request.form["attendance"] == "退勤":

        sql4 = """SELECT * FROM attendance WHERE usr_nm=?;"""
        cur.execute(sql4, [session["user-name"]])

        for row in cur:
            if row[3] == "--/--/-- --:--":
                row_num = row_num + 1
                row_id = row[0]

        if row_num == 0:

            flash("出勤日時が記録されていません")

            return render_template("prompt.html", user_name=session["user-name"])

        if row_num != 0:

            prsnt_end_dttm = datetime.datetime.now(
                pytz.timezone("Asia/Tokyo"))

            if (prsnt_end_dttm.minute >= 0 and prsnt_end_dttm.minute <= 29):
                prsnt_end_dttm_min = 30
                prsnt_end_dttm_hr = prsnt_end_dttm.hour

            elif (prsnt_end_dttm.minute >= 30 and prsnt_end_dttm.minute <= 59):
                prsnt_end_dttm_min = 0
                prsnt_end_dttm_hr = prsnt_end_dttm.hour + 1

            end_dttm_amndd = prsnt_end_dttm.replace(
                hour=prsnt_end_dttm_hr, minute=prsnt_end_dttm_min, second=0, microsecond=0)

            prsnt_end_dttm_frmttd = datetime.datetime.strftime(
                end_dttm_amndd, "%Y/%m/%d %H:%M")

            sql5 = """UPDATE attendance SET end_dttm=? WHERE id=?;"""
            cur.execute(
                sql5, (prsnt_end_dttm_frmttd, row_id))
            conn.commit()

            cur.close()
            conn.close()

            flash("退勤日時を記録しました")

            return render_template("prompt.html", user_name=session["user-name"])


# 「admin_prompt」のURLエンドポイントを定義する
@app.route("/admin_prompt", methods=["GET"])
def admin_prompt():

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("admin_prompt.html")


# 「search_users」のURLエンドポイントを定義する
@app.route("/search_users", methods=["GET"])
def search_users():

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("search_users.html")


# 「search_attendance」のURLエンドポイントを定義する
@app.route("/search_attendance", methods=["GET"])
def search_attendance():

    if request.method == "GET":

        if "is-admin" not in session:

            return redirect(url_for("admin_login"))

        elif session["is-admin"] == False:

            return redirect(url_for("admin_login"))

        return render_template("search_attendance.html")


# 当該モジュールが実行起点かどうかを確認した上でFlask本体を起動する
if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5000)
