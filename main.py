# coding: utf-8


# 既成のモジュールをインポートする
import os
import re
import csv
import datetime
import calendar
import pytz
import flask
import sqlite3
from datetime import timedelta
from flask import Flask, render_template, request, url_for, redirect, session, flash, send_file
from flask_paginate import Pagination, get_page_parameter

# 管理者用パスワードを宣言する
ADMIN_PASS_WORD = 'gp1192'

# セッションの持続時間を宣言する
SESSION_TIME = 20

# ユーザー情報のデータベースを宣言する
USERS_DATABASE = 'app_usrm.db'

# 勤怠・打刻情報のデータベースを宣言する
ATTENDANCE_DATABASE = 'app_tmm.db'

# 一画面ごとに表示する項目の数を宣言する
ITEM_PER_PAGE = 40

# インポートするCSVファイルの場所を宣言する
IMPORT_PATH = './cache_data'

# エクスポートするCSVファイルの場所を宣言する
EXPORT_PATH = 'cache_data/export_attendance.csv'

# Flask本体を構築する
app = flask.Flask(__name__, static_folder='static',
                  template_folder='templates')

# セッションキーを設定する
app.config['SECRET_KEY'] = 'python-flask-application__session-secret-key'


# 「index」のURLエンドポイントを定義する
@app.route('/',      methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    hit_cnt = 0

    session.clear()

    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        try:
            conn = sqlite3.connect(USERS_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('index.html')

        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        sql = """SELECT * FROM users WHERE usr_nm=?;"""
        cur.execute(sql, [request.form['login-user-name']])

        for row in cur:
            if (row[1] == '----------------' and row[2] == '--------'):
                flash('そのユーザーは既に抹消されています')
                return render_template('index.html')

            hit_cnt = hit_cnt + 1

        if hit_cnt == 0:
            cur.close()
            conn.close()

            flash('そのユーザーは登録されていません')

            return render_template('index.html')

        sql = """SELECT psswrd FROM users WHERE usr_nm=?;"""
        cur.execute(sql, [request.form['login-user-name']])

        for row in cur:
            if row != (request.form['login-pass-word'],):
                cur.close()
                conn.close()

                flash('そのパスワードは登録されていません')

                return render_template('index.html')

        cur.close()
        conn.close()

        session['login-user-name'] = request.form['login-user-name']
        session['is-logged-in'] = True
        app.permanent_session_lifetime = timedelta(minutes=SESSION_TIME)

        return redirect(url_for('prompt'))


# 「modify_user」のURLエンドポイントを定義する
@app.route('/modify_user', methods=['GET', 'POST'])
def modify_user():
    rows = []
    usr_id_shrt = ''
    hit_cnt = 0

    usr_id_lngth = len(str(session['modify-item-id']))

    if usr_id_lngth > 4:
        usr_id_shrt = str(session['modify-item-id'])[0:4] + '...'
    else:
        usr_id_shrt = str(session['modify-item-id'])

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(USERS_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('modify_user.html')
        cur = conn.cursor()
        conn.commit()

        sql = """SELECT * FROM users WHERE id=?;"""
        cur.execute(sql, [session['modify-item-id']])

        for row in cur:
            rows.append(row)

        return render_template('modify_user.html', user_info=rows, user_id=usr_id_shrt)

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        if len(request.form['modify-user-name']) > 16:
            flash('ユーザー名は16文字以内にしてください')
            return render_template('modify_user.html', user_id=usr_id_shrt)

        if len(request.form['modify-pass-word']) > 8:
            flash('パスワードは8文字以内にしてください')
            return render_template('modify_user.html', user_id=usr_id_shrt)

        if (' ' in request.form['modify-user-name'] or '　' in request.form['modify-user-name']):
            flash('ユーザー名にスペースは使えません')
            return render_template('modify_user.html', user_id=usr_id_shrt)

        if (' ' in request.form['modify-pass-word'] or '　' in request.form['modify-pass-word']):
            flash('パスワードにスペースは使えません')
            return render_template('modify_user.html', user_id=usr_id_shrt)

        pttrn_not_usr_nm = r'(-)+'
        is_not_usr_nm = re.fullmatch(
            pttrn_not_usr_nm, request.form['modify-user-name'])

        if is_not_usr_nm is not None:
            flash('ユーザー名を「 - 」のみにすることはできません')
            return render_template('modify_user.html', user_id=usr_id_shrt)

        pttrn_not_psswrd = r'(-)+'
        is_not_psswrd = re.fullmatch(
            pttrn_not_psswrd, request.form['modify-pass-word'])

        if is_not_psswrd == True:
            flash('パスワードを「 - 」のみにすることはできません')
            return render_template('modify_user.html', user_id=usr_id_shrt)

        try:
            conn = sqlite3.connect(USERS_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('modify_user.html')
        cur = conn.cursor()
        sql = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        sql = """SELECT * FROM users WHERE usr_nm=?;"""
        cur.execute(sql, [request.form['modify-user-name']])

        for row in cur:
            if (row[1] == '----------------' and row[2] == '--------'):
                flash('そのユーザーは既に抹消されています')
                return render_template('modify_user.html', user_id=usr_id_shrt)

            hit_cnt = hit_cnt + 1

        if hit_cnt != 0:
            flash('そのユーザー名は既に登録されています')
            cur.close()
            conn.close()

            return render_template('modify_user.html', user_id=usr_id_shrt)

        sql = """UPDATE users SET usr_nm=?, psswrd=? WHERE id=?;"""
        cur.execute(
            sql, (request.form['modify-user-name'], request.form['modify-pass-word'], session['modify-item-id']))
        conn.commit()

        cur.close()
        conn.close()

        flash('そのユーザー情報を修正しました')
        return render_template('modify_user.html', user_id=usr_id_shrt)


# 「register_user」のURLエンドポイントを定義する
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('register_user.html')

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(USERS_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('register_user.html')

        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                   usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        if len(request.form['register-user-name']) > 16:
            flash('ユーザー名は16文字以内にしてください')
            return render_template('register_user.html')

        if len(request.form['register-pass-word']) > 8:
            flash('パスワードは8文字以内にしてください')
            return render_template('register_user.html')

        if (' ' in request.form['register-user-name'] or '　' in request.form['register-user-name']):
            flash('ユーザー名にスペースは使えません')
            return render_template('register_user.html')

        if (' ' in request.form['register-pass-word'] or '　' in request.form['register-pass-word']):
            flash('パスワードにスペースは使えません')
            return render_template('register_user.html')

        pttrn_not_usr_nm = r'(-)+'
        is_not_usr_nm = re.fullmatch(
            pttrn_not_usr_nm, request.form['register-user-name'])

        if is_not_usr_nm is not None:
            flash('ユーザー名を「 - 」のみにすることはできません')
            return render_template('register_user.html')

        pttrn_not_psswrd = r'(-)+'
        is_not_psswrd = re.fullmatch(
            pttrn_not_psswrd, request.form['register-pass-word'])

        if is_not_psswrd == True:
            flash('パスワードを「 - 」のみにすることはできません')
            return render_template('register_user.html')

        sql = """SELECT usr_nm FROM users WHERE usr_nm=?;"""
        cur.execute(sql, [request.form['register-user-name']])

        for row in cur:
            if row == (request.form['user-name'],):
                flash('そのユーザー名は既に登録されています')
                cur.close()
                conn.close()

                return render_template('register_user.html')

        sql = """INSERT INTO users(usr_nm, psswrd) VALUES (?,?);"""
        cur.execute(
            sql, (request.form['register-user-name'], request.form['register-pass-word']))
        conn.commit()

        cur.close()
        conn.close()

        flash('そのユーザーを登録しました')
        return render_template('register_user.html')


# 「erasure_user」のURLエンドポイントを定義する
@app.route('/erasure_user', methods=['GET', 'POST'])
def erasure_user():
    usr_id_shrt = ''
    hit_cnt = 0

    usr_id_lngth = len(str(session['erasure-item-id']))

    if usr_id_lngth > 4:
        usr_id_shrt = str(session['erasure-item-id'])[0:4] + '...'
    else:
        usr_id_shrt = str(session['erasure-item-id'])

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('erasure_user.html', user_id=usr_id_shrt)

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(USERS_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('erasure_user.html')

        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        sql = """SELECT * FROM users WHERE id=?;"""
        cur.execute(sql, [session['erasure-item-id']])

        for row in cur:
            if (row[1] == '----------------' and row[2] == '--------'):
                flash('そのユーザーは既に抹消されています')
                return render_template('erasure_user.html', user_id=usr_id_shrt)

            hit_cnt = hit_cnt + 1

        if hit_cnt == 0:
            cur.close()
            conn.close()

            flash('そのユーザーは登録されていません')
            return render_template('erasure_user.html', user_id=usr_id_shrt)

        sql = """UPDATE users SET usr_nm='----------------', psswrd='--------' WHERE id=?;"""
        cur.execute(sql, [session['erasure-item-id']])
        conn.commit()

        cur.close()
        conn.close()

        flash('そのユーザーを抹消しました')
        return render_template('erasure_user.html', user_id=usr_id_shrt)


# 「admin_login」のURLエンドポイントを定義する
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    session.clear()

    if request.method == 'GET':
        return render_template('admin_login.html')

    if request.method == 'POST':
        if ADMIN_PASS_WORD != request.form['login-pass-word']:
            flash('そのパスワードは登録されていません')
            return render_template('admin_login.html')

        session['is-admin'] = True
        app.permanent_session_lifetime = timedelta(minutes=SESSION_TIME)

        return redirect(url_for('admin_prompt'))


# 「show_users」のURLエンドポイントを定義する
@app.route('/show_users', methods=['GET', 'POST'])
def show_users():
    rows = []

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(USERS_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('show_users.html')
        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        sql = """SELECT * From users;"""
        cur.execute(sql)

        for row in cur:
            rows.append(row)

        cur.close()
        conn.close()

        per_pg = ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = rows[(pg - 1) * per_pg: pg * per_pg]
        pgntn = Pagination(page=pg, total=len(
            rows), per_page=per_pg, css_framework='bootstrap4')

        return render_template('show_users.html', page_data=pg_dat, pagination=pgntn)

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        session['modify-item-id'] = request.form['hidden-modify-item-id']
        session['erasure-item-id'] = request.form['hidden-erasure-item-id']

        if session['modify-item-id'] != 'none':
            return redirect(url_for('modify_user'))

        elif session['erasure-item-id'] != 'none':
            return redirect(url_for('erasure_user'))


# 「show_attendance」のURLエンドポイントを定義する
@app.route('/show_attendance', methods=['GET', 'POST'])
def show_attendance():
    rows = []

    if request.method == 'GET':
        if 'is-admin' not in session:

            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:

            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('show_attendance.html')
        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL , bgn_dttm TEXT NOT NULL , end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        sql = """SELECT * FROM attendance;"""
        cur.execute(sql)

        for row in cur:
            rows.append(row)

        cur.close()
        conn.close()

        per_pg = ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = rows[(pg - 1) * per_pg: pg * per_pg]
        pgntn = Pagination(page=pg, total=len(
            rows), per_page=per_pg, css_framework='bootstrap4')

        return render_template('show_attendance.html', pagination=pgntn, page_data=pg_dat)

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        session['modify-item-id'] = request.form['hidden-modify-item-id']
        session['erasure-item-id'] = request.form['hidden-erasure-item-id']

        if session['modify-item-id'] != 'none':
            return redirect(url_for('modify_attendance'))

        elif session['erasure-item-id'] != 'none':
            return redirect(url_for('erasure_attendance'))


# 「modify_attendance」のURLエンドポイントを定義する
@app.route('/modify_attendance', methods=['GET', 'POST'])
def modify_attendance():
    rows = []
    attndnc_id_shrt = ''

    attndnc_id_lngth = len(str(session['modify-item-id']))

    if attndnc_id_lngth > 4:
        attndnc_id_shrt = str(session['modify-item-id'])[0:4] + '...'
    else:
        attndnc_id_shrt = str(session['modify-item-id'])

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('modify_attendance.html')
        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL , bgn_dttm TEXT NOT NULL , end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        sql = """SELECT * FROM attendance WHERE id=?;"""
        cur.execute(sql, [session['modify-item-id']])

        for row in cur:
            bgn_dttm1 = row[2].replace(' ', 'T')
            end_dttm1 = row[3].replace(' ', 'T')
            bgn_dttm2 = bgn_dttm1.replace('/', '-')
            end_dttm2 = end_dttm1.replace('/', '-')
            rows.append([row[1], bgn_dttm2, end_dttm2])

        cur.close()
        conn.close()

        return render_template('modify_attendance.html', attendance_info=rows, attndnc_id=attndnc_id_shrt)

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        if len(request.form['modify-user-name']) > 16:
            flash('ユーザー名は16文字以内にしてください')
            return render_template('modify_attendance.html', attndnc_id=attndnc_id_shrt)

        if (' ' in request.form['modify-user-name'] or '　' in request.form['modify-user-name']):
            flash('ユーザー名にスペースは使えません', attndnc_id=attndnc_id_shrt)
            return render_template('modify_attendance.html')

        pttrn_not_usr_nm = r'(-)+'
        is_not_usr_nm = re.fullmatch(
            pttrn_not_usr_nm, request.form['modify-user-name'])

        if is_not_usr_nm is not None:
            flash('ユーザー名を「 - 」のみにすることはできません')
            return render_template('modify_attendance.html', attndnc_id=attndnc_id_shrt)

        mdfy_bgn_dttm = datetime.datetime.strptime(
            request.form['modify-begin-datetime'], '%Y-%m-%dT%H:%M')
        mdfy_end_dttm = datetime.datetime.strptime(
            request.form['modify-end-datetime'], '%Y-%m-%dT%H:%M')

        if mdfy_bgn_dttm > mdfy_end_dttm:
            flash('出勤日時と退勤日時を前後させることはできません')
            return render_template('modify_attendance.html', attndnc_id=attndnc_id_shrt)

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('modify_attendance.html')
        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL , bgn_dttm TEXT NOT NULL , end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        mdfy_bgn_dttm1 = request.form['modify-begin-datetime'].replace(' ', '')
        mdfy_end_dttm1 = request.form['modify-end-datetime'].replace(' ', '')
        mdfy_bgn_dttm2 = mdfy_bgn_dttm1.replace('T', ' ')
        mdfy_end_dttm2 = mdfy_end_dttm1.replace('T', ' ')
        mdfy_bgn_dttm3 = mdfy_bgn_dttm2.replace('-', '/')
        mdfy_end_dttm3 = mdfy_end_dttm2.replace('-', '/')

        sql = """UPDATE attendance SET usr_nm=?, bgn_dttm=?, end_dttm=? WHERE id=?;"""
        cur.execute(sql, (request.form['modify-user-name'], mdfy_bgn_dttm3,
                    mdfy_end_dttm3, session['modify-item-id']))
        conn.commit()

        cur.close()
        conn.close()

        flash('勤怠情報を修正しました')
        return render_template('modify_attendance.html', attndnc_id=attndnc_id_shrt)


# 「register_attendance」のURLエンドポイントを定義する
@app.route('/register_attendance', methods=['GET', 'POST'])
def register_attendance():
    hit_cnt = 0
# k
    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('register_attendance.html')

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        if 16 < len(request.form['register-user-name']):
            flash('ユーザー名は16文字以内にしてください')
            return render_template('register_attendance.html')

        if (' ' in request.form['register-user-name'] or '　' in request.form['register-user-name']):
            flash('ユーザー名にスペースは使えません')
            return render_template('register_attendance.html')

        pttrn_not_usr_nm = r'(-)+'
        is_not_usr_nm = re.fullmatch(
            pttrn_not_usr_nm, request.form['register-user-name'])

        if is_not_usr_nm is not None:
            flash('ユーザー名を「 - 」のみにすることはできません.')

            return render_template('register_attendance.html')

        rgstr_bgn_dttm1 = datetime.datetime.strptime(
            request.form['register-begin-datetime'], '%Y-%m-%dT%H:%M')
        rgstr_end_dttm1 = datetime.datetime.strptime(
            request.form['register-end-datetime'], '%Y-%m-%dT%H:%M')

        if rgstr_bgn_dttm1 > rgstr_end_dttm1:
            flash('出勤日時と退勤日時を前後させることはできません.')
            return render_template('register_attendance.html')

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('register_attendance.html')
        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL , bgn_dttm TEXT NOT NULL , end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        rgstr_bgn_dttm2 = datetime.datetime.strftime(
            rgstr_bgn_dttm1, '%Y-%m-%dT%H:%M')
        rgstr_end_dttm2 = datetime.datetime.strftime(
            rgstr_bgn_dttm1, '%Y-%m-%dT%H:%M')

        rgstr_bgn_dttm3 = rgstr_bgn_dttm2.replace(
            'T', ' ')
        rgstr_end_dttm3 = rgstr_end_dttm2.replace(
            'T', ' ')
        rgstr_bgn_dttm4 = rgstr_bgn_dttm3.replace('-', '/')
        rgstr_end_dttm4 = rgstr_end_dttm3.replace('-', '/')

        sql = """SELECT * FROM attendance WHERE usr_nm=? AND bgn_dttm=? AND end_dttm=?;"""
        cur.execute(
            sql, (request.form['register-user-name'], rgstr_bgn_dttm4, rgstr_end_dttm4))

        for row in cur:
            hit_cnt += 1

        if hit_cnt > 0:
            flash('その勤怠情報は既に記録されています')
            return render_template('register_attendance.html')

        sql = """INSERT INTO attendance (usr_nm, bgn_dttm, end_dttm) VALUES (?, ?, ?);"""
        cur.execute(
            sql, (request.form['register-user-name'], rgstr_bgn_dttm4, rgstr_bgn_dttm4))
        conn.commit()

        cur.close()
        conn.close()

        flash('勤怠情報を記録しました')
        return render_template('register_attendance.html')


# 「erasure_attendance」のURLエンドポイントを定義する
@app.route('/erasure_attendance', methods=['GET', 'POST'])
def erasure_attendance():
    attndnc_id_shrt = ''
    hit_cnt = 0

    attndnc_id_lngth = len(str(session['erasure-item-id']))

    if attndnc_id_lngth > 4:
        attndnc_id_shrt = str(session['erasure-item-id'])[0:4] + '...'
    else:
        attndnc_id_shrt = str(session['erasure-item-id'])

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('erasure_attendance.html', attendance_id=attndnc_id_shrt)

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('erasure_attendance.html')
        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        sql = """SELECT * FROM attendance WHERE id=?;"""
        cur.execute(sql, [session['erasure-item-id']])

        for row in cur:
            if (row[1] == '----------------' and row[2] == '--/--/-- --:--' and row[3] == '--/--/-- --:--'):
                flash('その打刻は既に抹消されています')
                return render_template('erasure_attendance.html', attendance_idd=attndnc_id_shrt)

            hit_cnt = hit_cnt + 1

        if hit_cnt == 0:
            flash('その打刻は登録されていません')
            return render_template('erasure_attendance.html', attendance_id=attndnc_id_shrt)

        sql = """UPDATE attendance SET usr_nm='----------------', bgn_dttm='--/--/-- --:--', end_dttm='--/--/-- --:--' WHERE id=?;"""
        cur.execute(sql, [session['erasure-item-id']])
        conn.commit()

        cur.close()
        conn.close()

        flash('その打刻を抹消しました')
        return render_template('erasure_attendance.html', attendance_id=attndnc_id_shrt)


# 「import_from_csv」のURLエンドポイントを定義する
@app.route('/import_from_csv', methods=['GET', 'POST'])
def import_from_csv():
    rows1 = []
    rows2 = []

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('import_from_csv.html')

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('import_from_csv.html')
        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS attendance_csv (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        csv_file = request.files['upload-file']
        csv_file.save(os.path.join(IMPORT_PATH, csv_file.filename))

        open_csv = open(os.path.join(
            IMPORT_PATH, csv_file.filename), 'r', encoding='UTF-8')
        read_csv = csv.reader(open_csv)

        for row in read_csv:
            if len(row) != 4:
                continue

            if len(row[0]) > 16:
                continue

            if (' ' in row[0] or '　' in row[0]):
                continue

            if ('\'' in row[0] or '"' in row[0]):
                continue

            if (row[0] == '' or row[1] == '' or row[2] == '' or row[3] == ''):
                continue

            if (row[1] == '--/--/--' or row[2] == '--:--' or row[3] == '--:--'):
                continue

            bgn_dt_prt = row[1].split('-')
            bgn_yr = bgn_dt_prt[0]
            bgn_mnth = bgn_dt_prt[1]
            bgn_dy = bgn_dt_prt[2]
            bgn_tm_prt = row[2].split(':')
            end_tm_prt = row[3].split(':')
            bgn_hr = bgn_tm_prt[0]
            end_hr = end_tm_prt[0]
            bgn_mn = bgn_tm_prt[1]
            end_mn = end_tm_prt[1]

            if int(bgn_yr) < int('0001'):
                continue
            if int(bgn_yr) > int('9999'):
                continue
            if int(bgn_mnth) < 1:
                continue
            if int(bgn_mnth) > 12:
                continue
            if int(bgn_dy) < 1:
                continue
            if int(bgn_dy) > 31:
                continue
            if int(bgn_mnth) == 1:
                if calendar.monthrange(int(bgn_yr), 1)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 2:
                if calendar.monthrange(int(bgn_yr), 2)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 3:
                if calendar.monthrange(int(bgn_yr), 3)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 4:
                if calendar.monthrange(int(bgn_yr), 4)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 5:
                if calendar.monthrange(int(bgn_yr), 5)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 6:
                if calendar.monthrange(int(bgn_yr), 6)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 7:
                if calendar.monthrange(int(bgn_yr), 7)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 8:
                if calendar.monthrange(int(bgn_yr), 8)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 9:
                if calendar.monthrange(int(bgn_yr), 9)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 10:
                if calendar.monthrange(int(bgn_yr), 10)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 11:
                if calendar.monthrange(int(bgn_yr), 11)[1] < int(bgn_dy):
                    continue
            if int(bgn_mnth) == 12:
                if calendar.monthrange(int(bgn_yr), 12)[1] < int(bgn_dy):
                    continue
            if (int(bgn_hr) < 0 and int(end_hr) < 0):
                continue
            if (int(bgn_hr) > 23 and int(end_hr) > 23):
                continue
            if (int(bgn_mn) < 0 and int(end_mn) < 0):
                continue
            if (int(bgn_mn) > 59 and int(end_mn) > 59):
                continue

            rows1.append(row)

        for row in rows1:
            sql = """CREATE TABLE IF NOT EXISTS attendance_csv (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
            cur.execute(sql)
            conn.commit()

            sql = """INSERT INTO attendance_csv (usr_nm, bgn_dttm, end_dttm) VALUES (?, ?, ?);"""
            cur.execute(
                sql, (row[0], (row[1] + " " + row[2]), (row[1] + " " + row[3])))
            conn.commit()

        sql = """SELECT usr_nm, bgn_dttm, end_dttm FROM attendance
          WHERE usr_nm <> '----------------' AND bgn_dttm <> '--/--/-- --:--' AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--')
              UNION  SELECT usr_nm, bgn_dttm, end_dttm FROM attendance_csv
                WHERE usr_nm <> '----------------' AND bgn_dttm <> '--/--/-- --:--' AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--');"""
        cur.execute(sql)
        conn.commit()

        for row in cur:
            rows2.append(row)

        sql = """DROP TABLE attendance;"""
        cur.execute(sql)
        conn.commit()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        for row in rows2:
            sql = """INSERT INTO attendance (usr_nm, bgn_dttm, end_dttm) VALUES (?, ?, ?);"""
            cur.execute(sql, (row[0], row[1], row[2]))
            conn.commit()

        sql = """DROP TABLE attendance_csv;"""
        cur.execute(sql)
        conn.commit()

        cur.close()
        conn.close()

        open_csv.close()

        flash('CSVファイルをインポートしました.')
        return render_template('import_from_csv.html')


# 「export_to_csv」のURLエンドポイントを定義する
@app.route('/export_to_csv', methods=['GET', 'POST'])
def export_to_csv():
    rows = []

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('export_to_csv.html')

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            os.remove(EXPORT_PATH)
        except FileNotFoundError:
            pass

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('export_to_csv.html')
        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        sql = """SELECT usr_nm, bgn_dttm, end_dttm FROM attendance
                  WHERE usr_nm <> '----------------' OR bgn_dttm <> '--/--/-- --:--' OR end_dttm <> '--/--/-- --:--';"""
        cur.execute(sql)

        for row in cur:
            if row[2] == "--/--/-- --:--":
                continue

            usr_nm = row[0]

            bgn_dttm1 = row[1].split(" ")
            end_dttm1 = row[2].split(" ")

            bgn_dt1 = bgn_dttm1[0]
            bgn_dt2 = bgn_dt1.replace('/', '-')

            bgn_tm = bgn_dttm1[1]
            end_tm = end_dttm1[1]

            fl_buf = usr_nm + "," + bgn_dt2 + "," + bgn_tm + "," + end_tm + "\n"

            rows.append(fl_buf)

        cur.close()
        conn.close()

        fl = open(EXPORT_PATH, 'x', encoding='UTF-8')
        fl.writelines(rows)
        fl.close()

        return send_file(EXPORT_PATH, as_attachment=True)


# 「prompt」のURLエンドポイントを定義する
@app.route('/prompt', methods=['GET', 'POST'])
def prompt():
    hit_cnt = 0
    row_id = 0

    if request.method == 'GET':
        if 'is-logged-in' not in session:
            return redirect(url_for('index'))

        elif session['is-logged-in'] == False:
            return redirect(url_for('index'))

        else:
            return render_template('prompt.html', user_name=session['login-user-name'])

    if request.method == 'POST':
        if 'is-logged-in' not in session:
            return redirect(url_for('index'))

        elif session['is-logged-in'] == False:
            return redirect(url_for('index'))

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('prompt.html')

        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        if request.form['attendance'] == '出勤':
            sql = """SELECT * FROM attendance WHERE usr_nm=?;"""
            cur.execute(sql, [session['login-user-name']])

            for row in cur:
                if (row[2] != '--/--/-- --:--' and row[3] == '--/--/-- --:--'):
                    flash('出勤日時は既に記録されています')
                    return render_template('prompt.html', user_name=session['login-user-name'])

            crrnt_bgn_dttm = datetime.datetime.now(
                pytz.timezone('Asia/Tokyo'))

            crrnt_bgn_dttm_frmttd = datetime.datetime.strftime(
                crrnt_bgn_dttm, '%Y/%m/%d %H:%M')

            sql = """INSERT INTO attendance (usr_nm, bgn_dttm, end_dttm) VALUES (?, ?, ?);"""
            cur.execute(
                sql, (session['login-user-name'], crrnt_bgn_dttm_frmttd, '--/--/-- --:--'))
            conn.commit()

            cur.close()
            conn.close()

            flash('出勤日時を記録しました')
            return render_template('prompt.html', user_name=session['login-user-name'])

        if request.form['attendance'] == '退勤':
            sql = """SELECT * FROM attendance WHERE usr_nm=?;"""
            cur.execute(sql, [session['login-user-name']])

            for row in cur:
                if row[3] == '--/--/-- --:--':
                    hit_cnt = hit_cnt + 1
                    row_id = row[0]

            if hit_cnt == 0:
                flash('出勤日時が記録されていません')
                return render_template('prompt.html', user_name=session['login-user-name'])

            if hit_cnt != 0:
                crrnt_end_dttm = datetime.datetime.now(
                    pytz.timezone('Asia/Tokyo'))
                crrnt_end_dttm_frmttd = datetime.datetime.strftime(
                    crrnt_end_dttm, '%Y/%m/%d %H:%M')

                sql = """UPDATE attendance SET end_dttm=? WHERE id=?;"""
                cur.execute(
                    sql, (crrnt_end_dttm_frmttd, row_id))
                conn.commit()

                cur.close()
                conn.close()

                flash('退勤日時を記録しました')
                return render_template('prompt.html', user_name=session['login-user-name'])


# 「admin_prompt」のURLエンドポイントを定義する
@app.route('/admin_prompt', methods=['GET'])
def admin_prompt():

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('admin_prompt.html')


# 「search_users」のURLエンドポイントを定義する
@app.route('/search_users', methods=['GET', 'POST'])
def search_users():

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('search_users.html')

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        if (request.form['search-user-ids'] != '' and request.form['search-user-names'] != ''):
            flash('ユーザーIDとユーザー名の両方を同時に指定することはできません.')
            return render_template('search_users.html')

        if request.form['search-user-ids'] != '':
            srch_usr_ids = str(request.form['search-user-ids']).split(' ')

            for srch_usr_id in srch_usr_ids:
                if ('\'' in srch_usr_id or '"' in srch_usr_id):
                    flash('ユーザーIDにクオーテーションは使えません.')
                    return render_template('search_users.html')

                if (' ' in srch_usr_id or '　' in srch_usr_id):
                    flash('ユーザーIDにスペースは使えません.')
                    return render_template('search_users.html')

        if request.form['search-user-names'] != '':
            srch_usr_nms = str(request.form['search-user-names']).split(' ')

            for srch_usr_nm in srch_usr_nms:
                if ('\'' in srch_usr_nm[0] or '"' in srch_usr_nm[0]):
                    flash('ユーザー名にクオーテーションは使えません.')
                    return render_template('search_users.html')

                if (' ' in srch_usr_nm[0] or '　' in srch_usr_nm[0]):
                    flash('ユーザー名にスペースは使えません.')
                    return render_template('search_users.html')

        if (request.form['search-user-ids'] != '' and request.form['search-user-names'] == ''):
            session['search-user-ids'] = request.form['search-user-ids']
            session['search-user-names'] = ''
            session['sort-conditions'] = request.form['sort-conditions']
            session['extract-conditions'] = request.form['extract-conditions']
            return redirect(url_for('search_users_results'))

        if (request.form['search-user-ids'] == '' and request.form['search-user-names'] != ''):
            session['search-user-ids'] = ''
            session['search-user-names'] = request.form['search-user-names']
            session['sort-conditions'] = request.form['sort-conditions']
            session['extract-conditions'] = request.form['extract-conditions']
            return redirect(url_for('search_users_results'))

    session['search-user-ids'] = ''
    session['search-user-names'] = ''
    session['sort-conditions'] = request.form['sort-conditions']
    session['extract-conditions'] = request.form['extract-conditions']

    return redirect(url_for('search_users_results'))


# 「search_users_results」のURLエンドポイントを定義する
@app.route('/search_users_results', methods=['GET', 'POST'])
def search_users_results():
    dmmy = []
    srch_usrs = []
    ids_tmp1 = ''
    ids_tmp2 = ''
    nms_tmp = ''

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(USERS_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('search_users_results.html')

        cur = conn.cursor()
        sql = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        if session['search-user-ids'] != '' and session['search-user-names'] == '':
            srch_usr_ids = str(session['search-user-ids']).split(' ')
            ids_tmp1 = srch_usr_ids.copy()

            for srch_usr_id in srch_usr_ids:
                ids_tmp2 = ids_tmp2 + str(srch_usr_id) + ' '

            if session['sort-conditions'] == 'sort-conditions1':
                if session['extract-conditions'] == 'extract-conditions1':
                    ids_tmp1.sort(key=None, reverse=False)
                    for id_tmp1 in ids_tmp1:
                        sql = """SELECT * FROM users WHERE id=?;"""
                        cur.execute(sql, [id_tmp1])

                        for row in cur:
                            srch_usrs.append(row)

                if session['extract-conditions'] == 'extract-conditions2':
                    ids_tmp1.sort(key=None, reverse=False)
                    for id_tmp1 in ids_tmp1:
                        sql = """SELECT * FROM users WHERE id <> ?;"""
                        cur.execute(sql, [id_tmp1])

                        for row in cur:
                            if str(row[0]) in ids_tmp2:
                                continue
                            else:
                                srch_usrs.append(row)

            if session['sort-conditions'] == 'sort-conditions2':
                if session['extract-conditions'] == 'extract-conditions1':
                    ids_tmp1.sort(key=None, reverse=True)
                    for id_tmp1 in ids_tmp1:
                        sql = """SELECT * FROM users WHERE id=?;"""
                        cur.execute(sql, [id_tmp1])

                        for row in cur:
                            srch_usrs.append(row)

                if session['extract-conditions'] == 'extract-conditions2':
                    ids_tmp1.sort(key=None, reverse=True)
                    for id_tmp1 in ids_tmp1:
                        sql = """SELECT * FROM users WHERE id <> ?;"""
                        cur.execute(sql, [id_tmp1])

                        for row in cur:
                            if str(row[0]) in ids_tmp2:
                                continue
                            else:
                                srch_usrs.append(row)

            cur.close()
            conn.close()

            per_pg = ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = srch_usrs[(pg - 1) * per_pg: pg * per_pg]
            pgntn = Pagination(page=pg, total=len(
                srch_usrs), per_page=per_pg, css_framework='bootstrap4')

            flash('ユーザーを検索しました.')
            return render_template('search_users_results.html', page_data=pg_dat, pagination=pgntn)

        if session['search-user-ids'] == '' and session['search-user-names'] != '':
            srch_usr_nms = str(session['search-user-names']).split(' ')

            for srch_usr_nm in srch_usr_nms:
                nms_tmp = nms_tmp + str(srch_usr_nm) + ' '

            if session['sort-conditions'] == 'sort-conditions1':
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        sql = """SELECT * FROM users WHERE usr_nm=?;"""
                        cur.execute(sql, [srch_usr_nm])

                        for row in cur:
                            srch_usrs.append(row)
                            srch_usrs.sort(
                                key=lambda x: x[0], reverse=False)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        sql = """SELECT * FROM users WHERE usr_nm <> ?;"""
                        cur.execute(sql, [srch_usr_nm])

                        for row in cur:
                            if str(row[1]) in nms_tmp:
                                continue
                            else:
                                srch_usrs.append(row)
                                srch_usrs.sort(
                                    key=lambda x: x[0], reverse=False)

            if session['sort-conditions'] == 'sort-conditions2':
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        sql = """SELECT * FROM users WHERE usr_nm=?;"""
                        cur.execute(sql, [srch_usr_nm])

                        for row in cur:
                            srch_usrs.append(row)
                            srch_usrs.sort(
                                key=lambda x: x[0], reverse=True)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        sql = """SELECT * FROM users WHERE usr_nm <> ?;"""
                        cur.execute(sql, [srch_usr_nm])

                        for row in cur:
                            if str(row[1]) in nms_tmp:
                                continue
                            else:
                                srch_usrs.append(row)
                                srch_usrs.sort(
                                    key=lambda x: x[0], reverse=True)

            cur.close()
            conn.close()

            per_pg = ITEM_PER_PAGE
            pg = request.args.get(get_page_parameter(), type=int, default=1)
            pg_dat = srch_usrs[(pg - 1) * per_pg: pg * per_pg]
            pgntn = Pagination(page=pg, total=len(
                srch_usrs), per_page=per_pg, css_framework='bootstrap4')

            flash('ユーザーを検索しました.')
            return render_template('search_users_results.html', page_data=pg_dat, pagination=pgntn)

        if session['search-user-ids'] == '' and session['search-user-names'] == '':
            if session['sort-conditions'] == 'sort-conditions1':
                if session['extract-conditions'] == 'extract-conditions1':
                    cur.close()
                    conn.close()

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = dmmy[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        dmmy), per_page=per_pg, css_framework='bootstrap4')

                    flash('ユーザーを検索しました.')
                    return render_template('search_users_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    sql = """SELECT * FROM users ORDER BY id ASC;"""
                    cur.execute(sql)

                    for row in cur:
                        srch_usrs.append(row)

                    cur.close()
                    conn.close()

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_usrs[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_usrs), per_page=per_pg, css_framework='bootstrap4')

                    flash('ユーザーを検索しました.')
                    return render_template('search_users_results.html', page_data=pg_dat, pagination=pgntn)

            if session['sort-conditions'] == 'sort-conditions2':
                if session['extract-conditions'] == 'extract-conditions1':
                    cur.close()
                    conn.close()

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = dmmy[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        dmmy), per_page=per_pg, css_framework='bootstrap4')

                    flash('ユーザーを検索しました.')
                    return render_template('search_users_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    sql = """SELECT * FROM users ORDER BY id DESC;"""
                    cur.execute(sql)

                    for row in cur:
                        srch_usrs.append(row)

                    cur.close()
                    conn.close()

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_usrs[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_usrs), per_page=per_pg, css_framework='bootstrap4')

                    flash('ユーザーを検索しました.')
                    return render_template('search_users_results.html', page_data=pg_dat, pagination=pgntn)

        cur.close()
        conn.close()

        per_pg = ITEM_PER_PAGE
        pg = request.args.get(get_page_parameter(), type=int, default=1)
        pg_dat = dmmy[(pg - 1) * per_pg: pg * per_pg]
        pgntn = Pagination(page=pg, total=len(
            dmmy), per_page=per_pg, css_framework='bootstrap4')

        flash('ユーザーの検索に失敗しました.')
        return render_template('search_users_results.html', page_data=pg_dat, pagination=pgntn)

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        if ('hidden-modify-item-id' in request.form and 'hidden-erasure-item-id' in request.form):
            session['modify-item-id'] = request.form['hidden-modify-item-id']
            session['erasure-item-id'] = request.form['hidden-erasure-item-id']

        if ('modify-item-id' in session and 'erasure-item-id' in session):
            if session['modify-item-id'] != 'none':
                return redirect(url_for('modify_user'))
            if session['erasure-item-id'] != 'none':
                return redirect(url_for('erasure_user'))

        else:
            return redirect(url_for('search_users_results'))


# 「search_attendance」のURLエンドポイントを定義する
@app.route('/search_attendance', methods=['GET', 'POST'])
def search_attendance():
    srch_bgn_dttm2 = None
    srch_end_dttm2 = None
    srch_bgn_dttm3 = None
    srch_end_dttm3 = None
    srch_usr_nms = []

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('search_attendance.html')

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        if (request.form['search-user-ids'] != '' and request.form['search-user-names'] != ''):
            flash('ユーザーIDとユーザー名の両方を同時に指定することはできません.')
            return render_template('search_attendance.html')

        if request.form['search-user-ids'] != '':
            srch_usr_ids = str(request.form['search-user-ids']).split(' ')

            for srch_usr_id in srch_usr_ids:
                if ('\'' in srch_usr_id[0] or '"' in srch_usr_id[0]):
                    flash('ユーザーIDにクオーテーションは使えません.')
                    return render_template('search_attendance.html')

                if (' ' in srch_usr_id[0] or '　' in srch_usr_id[0]):
                    flash('ユーザーIDにスペースは使えません.')
                    return render_template('search_attendance.html')

        if request.form['search-user-names'] != '':
            srch_usr_nms = str(request.form['search-user-names']).split(' ')

            for srch_usr_nm in srch_usr_nms:
                if ('\'' in srch_usr_nm[0] or '"' in srch_usr_nm[0]):
                    flash('ユーザー名にクオーテーションは使えません.')
                    return render_template('search_attendance.html')

                if (' ' in srch_usr_nm[0] or '　' in srch_usr_nm[0]):
                    flash('ユーザー名にスペースは使えません.')
                    return render_template('search_attendance.html')

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('serach_attendance.html')

        cur = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        if request.form['search-begin-datetime'] != '':
            srch_bgn_dttm1 = request.form['search-begin-datetime'].replace(
                'T', ' ')
            srch_bgn_dttm2 = srch_bgn_dttm1.replace('-', '/')
            srch_bgn_dttm3 = datetime.datetime.strptime(
                srch_bgn_dttm2, '%Y/%m/%d %H:%M')
        else:
            srch_bgn_dttm2 = ''

        if request.form['search-end-datetime'] != '':
            srch_end_dttm1 = request.form['search-end-datetime'].replace(
                'T', ' ')
            srch_end_dttm2 = srch_end_dttm1.replace('-', '/')
            srch_end_dttm3 = datetime.datetime.strptime(
                srch_end_dttm2, '%Y/%m/%d %H:%M')
        else:
            srch_end_dttm2 = ''

        if (srch_bgn_dttm3 is not None and srch_end_dttm3 is not None):
            if srch_bgn_dttm3 > srch_end_dttm3:
                flash('出勤日時と退勤日時を前後させることはできません.')
                return render_template('search_attendance.html')

        if (request.form['search-user-ids'] != '' and request.form['search-user-names'] == ''):
            session['search-user-ids'] = request.form['search-user-ids']
            session['search-user-names'] = ''
            session['search-begin-datetime'] = srch_bgn_dttm2
            session['search-end-datetime'] = srch_end_dttm2
            session["sort-conditions"] = request.form["sort-conditions"]
            session['extract-conditions'] = request.form['extract-conditions']
            session["handling-of-non-attendance"] = request.form["handling-of-non-attendance"]
            return redirect(url_for('search_attendance_results'))

        if (request.form['search-user-ids'] == '' and request.form['search-user-names'] != ''):
            session['search-user-ids'] = ''
            session['search-user-names'] = request.form['search-user-names']
            session['search-begin-datetime'] = srch_bgn_dttm2
            session['search-end-datetime'] = srch_end_dttm2
            session["sort-conditions"] = request.form["sort-conditions"]
            session['extract-conditions'] = request.form['extract-conditions']
            session["handling-of-non-attendance"] = request.form["handling-of-non-attendance"]
            return redirect(url_for('search_attendance_results'))

        if (request.form['search-user-ids'] == '' and request.form['search-user-names'] == ''):
            session['search-user-ids'] = ''
            session['search-user-names'] = ''
            session['search-begin-datetime'] = srch_bgn_dttm2
            session['search-end-datetime'] = srch_end_dttm2
            session["sort-conditions"] = request.form["sort-conditions"]
            session['extract-conditions'] = request.form['extract-conditions']
            session["handling-of-non-attendance"] = request.form["handling-of-non-attendance"]
            return redirect(url_for('search_attendance_results'))


# 「search_attendance_results」のURLエンドポイントを定義する
@app.route('/search_attendance_results', methods=['GET', 'POST'])
def search_attendance_results():
    bgn_dttm = None
    srch_bgn_dttm = None
    srch_end_dttm = None
    dmmy = []
    srch_usr_nms = []
    srch_attndncs1 = []
    srch_attndncs2 = []
    nms_tmp = ''

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        if session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn1 = sqlite3.connect(USERS_DATABASE)
            cur1 = conn1.cursor()
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('serach_attendance.html')

        try:
            conn2 = sqlite3.connect(ATTENDANCE_DATABASE)
            cur2 = conn2.cursor()
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('search_attendance_results.html')

        sql = """CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                usr_nm TEXT NOT NULL, psswrd TEXT NOT NULL);"""
        cur1.execute(sql)
        conn1.commit()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        usr_nm TEXT NOT NULL , bgn_dttm TEXT NOT NULL , end_dttm TEXT NOT NULL);"""
        cur2.execute(sql)
        conn2.commit()

        if (session['search-user-ids'] != '' and session['search-user-names'] == '' and session['search-begin-datetime'] == '' and session['search-end-datetime'] == ''):
            srch_usr_ids = str(session['search-user-ids']).split(' ')

            for srch_usr_id in srch_usr_ids:
                sql = """SELECT usr_nm FROM users WHERE id=?;"""
                cur1.execute(sql, [srch_usr_id])

                for row in cur1:
                    srch_usr_nms.append(row[0])

            for srch_usr_nm in srch_usr_nms:
                nms_tmp = nms_tmp + srch_usr_nm + ' '

            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

        if (session['search-user-ids'] != '' and session['search-user-names'] == '' and session['search-begin-datetime'] != '' and session['search-end-datetime'] == ''):
            srch_usr_ids = str(session['search-user-ids']).split(' ')

            for srch_usr_id in srch_usr_ids:
                sql = """SELECT usr_nm FROM users WHERE id=?;"""
                cur1.execute(sql, [srch_usr_id])

                for row in cur1:
                    srch_usr_nms.append(row[0])

            for srch_usr_nm in srch_usr_nms:
                nms_tmp = nms_tmp + srch_usr_nm + ' '

            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')

                            if srch_bgn_dttm <= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')

                            if srch_bgn_dttm <= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')

                            if srch_bgn_dttm <= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')

                            if srch_bgn_dttm <= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

        if (session['search-user-ids'] != '' and session['search-user-names'] == '' and session['search-begin-datetime'] == '' and session['search-end-datetime'] != ''):
            srch_usr_ids = str(session['search-user-ids']).split(' ')

            for srch_usr_id in srch_usr_ids:
                sql = """SELECT usr_nm FROM users WHERE id=?;"""
                cur1.execute(sql, [srch_usr_id])

                for row in cur1:
                    srch_usr_nms.append(row[0])

            for srch_usr_nm in srch_usr_nms:
                nms_tmp = nms_tmp + srch_usr_nm + ' '

            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if srch_end_dttm >= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if srch_end_dttm >= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if srch_end_dttm >= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if srch_end_dttm >= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

        if (session['search-user-ids'] != '' and session['search-user-names'] == '' and session['search-begin-datetime'] != '' and session['search-end-datetime'] != ''):
            srch_usr_ids = str(session['search-user-ids']).split(' ')

            for srch_usr_id in srch_usr_ids:
                sql = """SELECT usr_nm FROM users WHERE id=?;"""
                cur1.execute(sql, [srch_usr_id])

                for row in cur1:
                    srch_usr_nms.append(row[0])

            for srch_usr_nm in srch_usr_nms:
                nms_tmp = nms_tmp + srch_usr_nm + ' '

            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if (srch_bgn_dttm <= bgn_dttm
                                    and srch_end_dttm >= bgn_dttm):
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if (srch_bgn_dttm <= bgn_dttm
                                    and srch_end_dttm >= bgn_dttm):
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if (srch_bgn_dttm <= bgn_dttm
                                    and srch_end_dttm >= bgn_dttm):
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if (srch_bgn_dttm <= bgn_dttm
                                    and srch_end_dttm >= bgn_dttm):
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

        if (session['search-user-ids'] == '' and session['search-user-names'] != '' and session['search-begin-datetime'] == '' and session['search-end-datetime'] == ''):
            srch_usr_nms = str(session['search-user-names']).split(' ')

            for srch_usr_nm in srch_usr_nms:
                nms_tmp = nms_tmp + srch_usr_nm + ' '

            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

        if (session['search-user-ids'] == '' and session['search-user-names'] != '' and session['search-begin-datetime'] != '' and session['search-end-datetime'] == ''):
            srch_usr_nms = str(session['search-user-names']).split(' ')

            for srch_usr_nm in srch_usr_nms:
                nms_tmp = nms_tmp + srch_usr_nm + ' '

            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')

                            if srch_bgn_dttm <= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')

                            if srch_bgn_dttm <= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')

                            if srch_bgn_dttm <= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')

                            if srch_bgn_dttm <= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

        if (session['search-user-ids'] == '' and session['search-user-names'] != '' and session['search-begin-datetime'] == '' and session['search-end-datetime'] != ''):
            srch_usr_nms = str(session['search-user-names']).split(' ')

            for srch_usr_nm in srch_usr_nms:
                nms_tmp = nms_tmp + srch_usr_nm + ' '

            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if srch_end_dttm >= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if srch_end_dttm >= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if srch_end_dttm >= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if srch_end_dttm >= bgn_dttm:
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

        if (session['search-user-ids'] == '' and session['search-user-names'] != '' and session['search-begin-datetime'] != '' and session['search-end-datetime'] != ''):
            srch_usr_nms = str(session['search-user-names']).split(' ')

            for srch_usr_nm in srch_usr_nms:
                nms_tmp = nms_tmp + srch_usr_nm + ' '

            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if (srch_bgn_dttm <= bgn_dttm
                                    and srch_end_dttm >= bgn_dttm):
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm ASC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if (srch_bgn_dttm <= bgn_dttm
                                    and srch_end_dttm >= bgn_dttm):
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions1':
                    for srch_usr_nm in srch_usr_nms:
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])
                        if session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                            sql = """SELECT * FROM attendance WHERE usr_nm=? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                            cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if (srch_bgn_dttm <= bgn_dttm
                                    and srch_end_dttm >= bgn_dttm):
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

                if session['extract-conditions'] == 'extract-conditions2':
                    for srch_usr_nm in srch_usr_nms:
                        if srch_usr_nm in nms_tmp:
                            if session["handling-of-non-attendance"] == "handling-of-non-attendance1":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])
                            elif session["handling-of-non-attendance"] == "handling-of-non-attendance2":
                                sql = """SELECT * FROM attendance WHERE usr_nm <> ? AND (bgn_dttm <> '--/--/-- --:--' AND end_dttm <> '--/--/-- --:--') ORDER BY bgn_dttm DESC;"""
                                cur2.execute(sql, [srch_usr_nm])

                        for row in cur2:
                            if row[1] in nms_tmp:
                                continue
                            else:
                                srch_attndncs1.append(row)

                    for srch_attndnc1 in srch_attndncs1:
                        if srch_attndnc1[2] != '--/--/-- --:--':
                            bgn_dttm = datetime.datetime.strptime(
                                srch_attndnc1[2], '%Y/%m/%d %H:%M')
                            srch_bgn_dttm = datetime.datetime.strptime(
                                session['search-begin-datetime'], '%Y/%m/%d %H:%M')
                            srch_end_dttm = datetime.datetime.strptime(
                                session['search-end-datetime'], '%Y/%m/%d %H:%M')

                            if (srch_bgn_dttm <= bgn_dttm
                                    and srch_end_dttm >= bgn_dttm):
                                srch_attndncs2.append(srch_attndnc1)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs2[(pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs2), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

        if (session['search-user-ids'] == '' and session['search-user-names'] == ''):
            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions1':

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = dmmy[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        dmmy), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions1":
                if session['extract-conditions'] == 'extract-conditions2':
                    sql = """SELECT * FROM attendance ORDER BY bgn_dttm ASC;"""
                    cur2.execute(sql)

                    for row in cur2:
                        srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions1':

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = dmmy[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        dmmy), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

            if session["sort-conditions"] == "sort-conditions2":
                if session['extract-conditions'] == 'extract-conditions2':
                    sql = """SELECT * FROM attendance ORDER BY bgn_dttm DESC;"""
                    cur2.execute(sql)

                    for row in cur2:
                        srch_attndncs1.append(row)

                    per_pg = ITEM_PER_PAGE
                    pg = request.args.get(
                        get_page_parameter(), type=int, default=1)
                    pg_dat = srch_attndncs1[(
                        pg - 1) * per_pg: pg * per_pg]
                    pgntn = Pagination(page=pg, total=len(
                        srch_attndncs1), per_page=per_pg, css_framework='bootstrap4')

                    cur1.close()
                    cur2.close()
                    conn1.close()
                    conn2.close()

                    flash('打刻を検索しました.')
                    return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

        per_pg = ITEM_PER_PAGE
        pg = request.args.get(
            get_page_parameter(), type=int, default=1)
        pg_dat = dmmy[(pg - 1) * per_pg: pg * per_pg]
        pgntn = Pagination(page=pg, total=len(
            dmmy), per_page=per_pg, css_framework='bootstrap4')

        cur1.close()
        cur2.close()
        conn1.close()
        conn2.close()

        flash('打刻の検索に失敗しました.')
        return render_template('search_attendance_results.html', page_data=pg_dat, pagination=pgntn)

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        if ('hidden-modify-item-id' in request.form and 'hidden-erasure-item-id' in request.form):
            session['modify-item-id'] = request.form['hidden-modify-item-id']
            session['erasure-item-id'] = request.form['hidden-erasure-item-id']

            if ('modify-item-id' in session and 'erasure-item-id' in session):
                if session['modify-item-id'] != 'none':
                    return redirect(url_for('modify_attendance'))
                if session['erasure-item-id'] != 'none':
                    return redirect(url_for('erasure_attendance'))
        else:
            return redirect(url_for('search_attendance_results'))


# 「reset_db」のURLエンドポイントを定義する
@app.route('/reset_db', methods=['GET', 'POST'])
def reset_db():

    if request.method == 'GET':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        return render_template('reset_db.html')

    if request.method == 'POST':
        if 'is-admin' not in session:
            return redirect(url_for('admin_login'))

        elif session['is-admin'] == False:
            return redirect(url_for('admin_login'))

        try:
            conn = sqlite3.connect(ATTENDANCE_DATABASE)
        except sqlite3.OperationalError:
            flash('DBファイルにアクセスできません, プログラムファイルを新規のプロジェクトフォルダに移してください.')
            return render_template('reset_db.html')
        cur = conn.cursor()

        sql = """DROP TABLE attendance;"""
        cur.execute(sql)
        conn.commit()

        sql = """VACUUM;"""
        cur.execute(sql)
        conn.commit()

        sql = """CREATE TABLE IF NOT EXISTS attendance (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                     usr_nm TEXT NOT NULL, bgn_dttm TEXT NOT NULL, end_dttm TEXT NOT NULL);"""
        cur.execute(sql)
        conn.commit()

        cur.close()
        conn.close()

        flash('データベースをリセットしました.')
        return render_template('reset_db.html')


# 当該モジュールが実行起点かどうかを確認した上でFlask本体を起動する
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
