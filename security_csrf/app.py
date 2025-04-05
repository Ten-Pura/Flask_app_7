from flask import Flask, render_template_string, redirect, url_for, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import CSRFProtect

app: Flask = Flask(__name__)

#CSRFトークンの生成に使用する秘密鍵を設定
app.config['SECRET_KEY'] = "secretkey"

#CSRF保護を有効化
csrf = CSRFProtect(app)

#WTFormsを使用してフォームを定義
class MyForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.before_request
def before_request():
    if request.is_secure:
        return
    else:
        return redirect(request.url.replace("http://", "https://"))

@app.route("/", methods=["GET", "POST"])
def index():
    form = MyForm()
    if form.validate_on_submit():
        #トークンを検証し、フォームが有効な場合の処理
        return redirect(url_for('success'))

    return render_template("index.html", form=form)

@app.route("/success")
def success():
    return "Form submitted successfully"

if __name__ == "__main__":
    app.run(debug=True)