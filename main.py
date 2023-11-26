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
from flask_dance.contrib.google import google
from flask_dance.contrib.facebook import facebook
from flask_login import logout_user, login_required, current_user

from models import db, login_manager, User
from oauth import github_blueprint, google_blueprint, teamsnap_blueprint, facebook_blueprint
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

app = Flask(
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)
app.secret_key = "supersecretkey"
app.register_blueprint(github_blueprint, url_prefix="/login")
app.register_blueprint(google_blueprint, url_prefix="/login")
app.register_blueprint(facebook_blueprint, url_prefix="/login")
app.register_blueprint(teamsnap_blueprint, url_prefix="/login")
app.config['OAUTHLIB_INSECURE_TRANSPORT'] = 1
app.config['OAUTHLIB_RELAX_TOKEN_SCOPE'] = 1 # google changes scope on us
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./users.db"

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/github")
def github_login():
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

# https://github.com/singingwolfboy/flask-dance-google-sqla
# have to enable the "People API" in https://console.cloud.google.com/apis
@app.route("/google")
def google_login():
  if not google.authorized:
    redirect_url = url_for("google.login")
    redirect_url = "https://www.roocell.com:5001/login/google/authorized" # TODO: shouldn't hardcode this
    print(f"redirect_url {redirect_url}")
    return redirect(redirect_url)
  try:
    resp = google_blueprint.session.get("/oauth2/v1/userinfo")
  except TokenExpiredError:
    print("token is expired: logging out")
    logout_user()
    # this doens't work - had to remove database
    return redirect(url_for("home_page"))
  
  print(f"google auth")
  print(resp)
  if resp.ok:
    info = resp.json()
    user_id = info["id"]
    service = "google"

    print(f"google user_id {user_id}")
  return f"You are {user_id} on Google"

  # i think we can get an actual username/email from here.
  # resp = google.get("/plus/v1/people/me")
  # assert resp.ok, resp.text
  # return "You are {email} on Google".format(email=resp.json()["emails"][0]["value"])

@app.route("/teampsnap")
def teamsnap_login():
  if not teamsnap_blueprint.session.authorized:
    print("teamsnap not authorized")
    #redirect_url = url_for("teamsnap_blueprint.login")
    redirect_url = "https://www.roocell.com:5001/login/teamsnap/authorized" # TODO: shouldn't hardcode this
    return redirect(redirect_url)
  
  print(f"teamsnap auth")
  resp = teamsnap_blueprint.session.get("/user")
  print("Here's the content of my response: " + resp.content)
  if resp.ok:
    service = "teamsnap"

  return f"You are {user_id} on Teamsnap"

@app.route("/facebook")
def facebook_login():
  if not facebook.authorized:
    print("facebook not authorized")
    #redirect_url = url_for("facebook_blueprint.login")
    redirect_url = "https://www.roocell.com:5001/login/facebook/authorized" # TODO: shouldn't hardcode this
    return redirect(redirect_url)
  
  print(f"facebook auth")
  resp = facebook.get("/me")
  print("Here's the content of my response: " + resp.content)
  if resp.ok:
    service = "facebook"
  email = resp.json()["email"]
  return f"You are {email} on Facebook"

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
