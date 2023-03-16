import flask
import secrets
import main
from flask import Flask, render_template, request, redirect, url_for, session
# from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)



@app.route("/")
def index():
    print("in index")

    if "authorized" in session:
        print("authorized")

    else:
        try:
            authorization_response = flask.request.url
            main.flow.fetch_token(authorization_response=authorization_response)
            main.credentials = main.flow.credentials
            main.youtube = main.create_client(credentials=main.credentials)
            session["authorized"] = True
        except:
            return flask.redirect(main.authorization_url)

    return render_template("index.html")


@app.route('/results', methods=["GET", "POST"])
def down_trans_up():
    # captions = main.get_captions(request.form["video_id"])
    # new_captions = main.translate_captions(captions, request.form["lang_string"])
    # io_captions = main.back_2_bytes(new_captions)
    # main.upload_captions(io_captions, request.form["lang_string"], request.form["video_id"])
    return render_template("success.html")



