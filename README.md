# Flask_app_7

Flaskで認証・セキュリティ周りを練習したリポジトリ。3つの独立したアプリが入っている。

## 構成

```
Flask_app_7/
├── mfa_google/      # Google OAuth 2.0 認証
├── mfa_mail/        # メールOTP二段階認証
└── security_csrf/   # CSRF対策
```

---

## 各アプリの概要

### mfa_google — Google OAuth 2.0

Authlibを使ってGoogleアカウントでログインする実装。

| ルート | 説明 |
|--------|------|
| `/` | トップ（未ログインならloginへリダイレクト） |
| `/login` | GoogleのOAuth認証ページへリダイレクト |
| `/auth/callback` | Google認証後のコールバック処理 |

**注意:** リダイレクトURIがGitHub Codespace向けにハードコードされているため、別環境では要修正。

---

### mfa_mail — メール二段階認証

メールアドレス＋パスワードでログイン後、TOTPワンタイムパスワードをメールで送って検証する実装。

| ルート | 説明 |
|--------|------|
| `/register` | ユーザー登録 |
| `/` | ログイン |
| `/verify` | OTP検証 |
| `/proctected` | 認証済みユーザーのみアクセス可（typoあり） |

**未完成箇所:**
- メール送信が `#mail.send(msg)` でコメントアウトされたまま
- OTPはコンソールの `print()` で確認する状態
- Gmailの認証情報がソースに直書きされているため、使う場合は環境変数に移すこと

**依存ライブラリ:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail, PyOTP, Werkzeug

---

### security_csrf — CSRF対策

Flask-WTFを使ったCSRFトークンの生成・検証の実装。おまけでHTTP→HTTPSリダイレクトも入っている。

| ルート | 説明 |
|--------|------|
| `/` | フォーム（CSRFトークン付き） |
| `/success` | 送信成功ページ |

---

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-sqlalchemy flask-login flask-mail flask-wtf pyotp werkzeug
```

### 起動例（mfa_mail）

```bash
python mfa_mail/app.py
# → http://127.0.0.1:5000
```
