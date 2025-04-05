from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os

app: Flask = Flask(__name__)
app.secret_key = "secretkey_01"

#OAuth設定
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", None),
    client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", None),
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration",
    redirect_uri = "https://animated-space-barnacle-7vvvjqvr9r2pp9q-5000.app.github.dev/auth/callback",
    client_kwargs = {"scope": "openid profile email"}
)

@app.route("/")
def index():
    #ログイン済みかどうかを確認
    email = dict(session).get("email", None)
    print(email)
    if email is None:
        return redirect(url_for("login"))
    return f"ログインに成功しました！<br/>ログイン中のアカウント：python@sample.com"

#ログインする際はGoogle認証へリダイレクト
@app.route("/login")
def login():
    return google.authorize_redirect("https://animated-space-barnacle-7vvvjqvr9r2pp9q-5000.app.github.dev/auth/callback")

#Google認証後のコールバック
@app.route("/auth/callback")
def auth_callback():
    token = google.authorize_access_token()
    resp  = google.get("https://www.googleapis.com/oauth2/v1/userinfo")
    user_info = resp.json()
    session["email"] = user_info["email"]
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)