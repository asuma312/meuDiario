import flask
from functools import wraps
from db.queries import verify_db


def verifylogged(route):
    @wraps(route)
    def decorated_function(*args, **kwargs):
        if flask.session.get("adup"):
            return route(*args, **kwargs)

        userhash = flask.session.get("uh")
        if not userhash:
            return flask.redirect(flask.url_for("login"))

        user = verify_db(userhash)
        if not user:
            return flask.redirect(flask.url_for("login"))

        return route(*args, **kwargs)

    return decorated_function
