import os

from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.contrib.google import google, make_google_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.consumer import OAuth2ConsumerBlueprint

from models import OAuth, db, User

import json

# load services
json_file_path = 'services.json'
with open(json_file_path, 'r') as file:
    services = json.load(file)

for service, service_data in services.items():
    print(f"service: {service}")
    for key, value in service_data.items():
        print(f"    {key}: {value}")

# GitHub
github_blueprint = make_github_blueprint(
    client_id=services['github']['client'],
    client_secret=services['github']['secret'],
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),
)

@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    info = github.get("/user")
    if info.ok:
        account_info = info.json()
        username = account_info["login"]
        service = "github"

        query = User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            user = User(username=username, service=service)
            db.session.add(user)
            db.session.commit()
        login_user(user)


# Google
google_blueprint = make_google_blueprint(
    client_id=services['google']['client'],
    client_secret=services['google']['secret'],
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),
)

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):

  resp = blueprint.session.get("/oauth2/v1/userinfo")
  print(f"google_logged_in")
  print(resp)
  if resp.ok:
    info = resp.json()
    user_id = info["id"]
    user_email = info["email"]
    service = "google"

    print(f"google user_id {user_id}")

    query = User.query.filter_by(username=user_id)
    try:
        user = query.one()
    except NoResultFound:
        print("adding user")
        user = User(username=user_id, service=service)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    login_user(user)  

# Teamsnap (custom blueprint)
teamsnap_blueprint = OAuth2ConsumerBlueprint(
    "teamsnap", __name__,
    client_id=services['teamsnap']['client'],
    client_secret=services['teamsnap']['secret'],
    base_url="https://auth.teamsnap.com/",
    token_url="https://auth.teamsnap.com/oauth/authorize",
    authorization_url="https://www.roocell.com:5001/login/teamsnap/authorized"
)


@oauth_authorized.connect_via(teamsnap_blueprint)
def teamsnap_logged_in(blueprint, token):
  print(f"teamsnap_logged_in")
  resp = blueprint.session.get("/user")
  print(resp)
  if resp.ok:
    info = resp.json()
    username = info["email"]
    service = "teamsnap"

    print(f"teamsnap username {username}")

    query = User.query.filter_by(username=username)
    try:
        user = query.one()
    except NoResultFound:
        print("adding user")
        user = User(username=username, service=service)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    login_user(user)  