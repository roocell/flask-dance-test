# this is a demo for social login
# provides a github login button when clicked will login
# then (if logged in) will provide a logout button
# users are stored in a db

# https://testdriven.io/blog/flask-social-auth/

# ==== REPLIT ======
# could not get replit to work - so had to move to local server
# a replit to test social login using python flask.
# users stored into a db

# use replit 'secrets' tool to create environment variables
# if using http:// server then you need this env variable
# OAUTHLIB_INSECURE_TRANSPORT=1
# replit runs https - so don't need it
# ========================

# need to run https so that github oauth2 works

# needed to "sudo pip3 install pyopenssl"
# sudo pip3 install Flask Flask-Dance
# sudo pip3 install blinker
# sudo pip3 install Flask-Login Flask-SQLAlchemy SQLAlchemy-Utils

from flask import Flask, jsonify, render_template, flash, redirect, url_for, request
from flask_dance.contrib.github import github
from flask_login import logout_user, login_required, current_user

from models import db, login_manager, User
from oauth import github_blueprint

app = Flask(
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)
app.secret_key = "supersecretkey"
app.register_blueprint(github_blueprint, url_prefix="/login")
app.config['OAUTHLIB_INSECURE_TRANSPORT'] = 1
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./users.db"

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/ping")
def ping():
  return jsonify(ping="pong")


@app.route("/github")
def login():
  if not github.authorized:
    redirect_url = url_for("github.login")
    redirect_url = "https://www.roocell.com:5001/login/github/authorized" # TODO: shouldn't hardcode this
    print(f"{redirect_url}")
    return redirect(redirect_url)

  res = github.get("/user")
  query = User.query.filter_by(username=res.json()['login'])
  try:
    user = query.one()
    print(f"user.service {user.service}")
  except:
    pass

  return f"You are @{res.json()['login']} on GitHub"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_page"))


@app.route('/')
def home_page():
  return render_template('index.html')


# replit must use 0.0.0.0
# http://REPL-NAME.USERNAME.repl.co
# http://flask-dance.michaelrussell5.repl.co
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5001, debug=True, ssl_context = 'adhoc')