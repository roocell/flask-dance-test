import os

from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.contrib.google import google, make_google_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound

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
  print(f"google auth")
  print(resp)
  if resp.ok:
    info = resp.json()
    user_id = info["id"]
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

