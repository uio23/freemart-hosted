# Importing 3rd party components
from flask import Blueprint, flash, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user

from datetime import datetime

from decimal import Decimal

import urllib

import requests

import json

# Importing freemart component
from . import db

from .models import User

from .forms import QuizForm

from .helperFunc import confirmed_required


# Income branch blueprint definition
income = Blueprint('income', __name__, url_prefix="/income")


# ----- Routes definition ----- #

@income.route("/quiz", methods=["GET", "POST"])
@login_required
@confirmed_required
def quiz_page():
    '''
        Let user attempt quiz once a day.
        Redirect to result page on submit.
        Reward 10 coins per correct answer.
    '''

    currentTime = datetime.utcnow()
    lastTime = datetime.strptime(current_user.lastquiz, '%Y-%m-%d %H:%M:%S.%f')
    difference = currentTime - lastTime

    if difference.days >= 1: 
        if (not current_user.quizQuestions):
            response = requests.get("https://opentdb.com/api.php?amount=3&category=9&difficulty=medium&type=boolean&encode=url3986")
            raw = response.json()
            
            if (raw["response_code"] != 0):
                flash("Unable to fetch quiz questions", category='error')
                return redirect(url_for("user.profile_page", username=current_user.username))

            questions = [[urllib.parse.unquote(question["question"]), question["correct_answer"]] for question in raw['results']]

            current_user.quizQuestions = json.dumps(questions)
            db.session.commit()
        else:
            questions = json.loads(current_user.quizQuestions)

        questionForm = QuizForm(questions)

        if questionForm.validate_on_submit():
            current_user.lastquiz = currentTime
            answers = [questionForm.qOne.data, questionForm.qTwo.data, questionForm.qThree.data]
            numOfCorrect = 0
            checked = []
            outcome = []
            for index, answer in enumerate(answers):
                if answer == "True":
                    checked.append("checked")
                    checked.append("")
                else:
                    checked.append("")
                    checked.append("checked")

                if answer == questionForm.questions[index][1]:
                    numOfCorrect += 1
                    outcome.append("valid")
                else:
                    outcome.append("invalid")
            current_user.balance += numOfCorrect*10
            db.session.commit()

            return render_template("income/quizResult.html", user=current_user, outcome=outcome, checked=checked, form=questionForm)
        return render_template("income/quiz.html", user=current_user, allow=True, form=questionForm)
    else:
        return render_template("income/quiz.html", user=current_user, allow=False)
