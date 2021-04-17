from flask import Blueprint
from flask import Flask, render_template, url_for, request, redirect, session, jsonify, flash
from .database import DataBase

view = Blueprint("views", __name__)

# GLOBAL CONSTANTS
NAME_KEY = 'name'
MSG_LIMIT = 20

# VIEWS


@view.route("/login", methods=["POST", "GET"])
def login():
    """
    Displays the main login page and handles saving name in session
    :return: None
    """

    if request.method == "POST":
        name = request.form["inputName"]
        if len(name) >= 2:
            session[NAME_KEY] = name
            flash(f'Congrats! You are successfully logged in as {name}.')
            return redirect(url_for("views.home"))
        else:
            flash("Sorry, your name has to be more than 1 character.")

    return render_template("login.html", **{"session": session})


@view.route("/logout")
def logout():
    """
    logs the user out by popping name from the session
    :return: None
    """

    session.pop(NAME_KEY, None)
    flash("You were logged out...")
    return redirect(url_for("views.login"))


@view.route('/')
@view.route("/home")
def home():
    """
    displays the home page if user is logged in
    :return: None
    """

    if NAME_KEY not in session:
        return redirect(url_for("views.login"))

    return render_template("index.html", **{"session": session})


@view.route("/history")
def history():
    if NAME_KEY not in session:
        flash("Please login before viewing message history.")
        return redirect(url_for("views.login"))

    json_messages = get_history(session[NAME_KEY])
    print(json_messages)
    return render_template("history.html", **{"history": json_messages})


@view.route("/get_name")
def get_name():
    """
    :return: a json object storing name of logged in user
    """

    data = {"name": ""}
    if NAME_KEY not in session:
        data = {"name": session[NAME_KEY]}

    return jsonify(data)


@view.route("/get_messages")
def get_messages():
    """
    :return: all the messages stored in the database
    """

    db = DataBase()
    msgs = db.get_all_messages(MSG_LIMIT)
    messages = remove_seconds_from_messages(msgs)

    return jsonify(messages)


@view.route("/get_history")
def get_history(name):
    """
    :param name: str
    :return: all messages by name of the user
    """

    db = DataBase()
    msgs = db.get_messages_by_name(name)
    messages = remove_seconds_from_messages(msgs)

    return jsonify(messages)


# UTILITIES


def remove_seconds_from_messages(msgs):
    """
    removes the seconds from all the messages
    :param msgs: list
    :return: list
    """

    messages = []
    for msg in msgs:
        message = msg
        message["time"] = remove_seconds(message["time"])
        messages.append(message)

    return messages


def remove_seconds(msg):
    """
    removes the seconds of a datetime string
    """
    return msg.split(".")[0][:-3]