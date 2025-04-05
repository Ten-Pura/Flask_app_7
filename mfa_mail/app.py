from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyotp
import os

app: Flask = Flask(__name__)
app.secret_key = 'secretkey'

#メールサーバーの設定
app.config["MAIL_SERVER"]   = "smtp.gmail.com"
app.config["MAIL_PORT"]     = 587
app.config["MAIL_USE_TLS"]  = True
app.config["MAIL_USERNAME"] = os.environ.get('GMAIL_ID', None)
app.config["MAIL_PASSWORD"] = os.environ.get('GMAIL_PASSWORD', None)
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get('GMAIL_ID', None)
mail = Mail(app)

#データベースの設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

#ユーザー認証の設定
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#ワンタイムパスワードをメールで送信する関数
def send_otp(email):
    #シークレットキーとワンタイムパスワード生成器を生成
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret, interval=60)
    
    #ワンタイムパスワードを生成し、メール送信
    otp_code = totp.now()
    msg = Message("ワンタイムパスワード（OTP）", recipients=[email])
    msg.body = f"あなたのワンタイムパスワードは{otp_code}です。60秒間有効です。"
    mail.send(msg)

    return secret

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email    = request.form.get("email", None)
        password = request.form.get("password", None)

        if email and password:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return "すでに登録されているメールアドレスです。"
            
            #新しいユーザーをデータベースに追加
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

        else:
            return "error"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]

        #ユーザー認証
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            #ワンタイムパスワードを送信
            secret = send_otp(email)

            #セッションにシークレットキーを保存
            session["otp_secret"] = secret
            session["email"]      = email

            return redirect(url_for('verify'))
        
    return render_template("login.html")

#ログイン成功後のワンタイムパスワード検証
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        otp_code = request.form['otp']

        #セッションからシークレットキーを取得
        secret = session.get("otp_secret")

        #保存しておいたシークレットキーを取得
        totp = pyotp.TOTP(secret)
        if totp.verify(otp_code):
            #ユーザーをログイン状態にする
            email = session.get("email")
            user  = User.query.filter_by(email=email).first()
            if user:
                login_user(user)
                return redirect(url_for('proctected'))
        
        return "無効なOTPです。"
    
    return render_template("verify.html")

@app.route("/proctected")
@login_required
def proctected():
    return "2段階認証に成功しました。"

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)