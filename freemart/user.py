from flask import Blueprint, render_template, flash, request
from flask_login import login_required, current_user

import re

import random

from . import db

from .imageFunc import loadImgs

from .models import Product, User, Message


user = Blueprint('user', __name__, url_prefix="/user")

def not_float(variable):
    try:
        float(variable)
        return False
    except:
        return True

@user.route("/profile/<username>", methods=["GET", "POST"])
@user.route("/<username>", methods=["GET", "POST"])
@login_required
def profile_page(username):
    if request.method == "POST":
        productName = request.form.get("productName")
        product = Product.query.filter_by(name=productName).first()

        if product.username == current_user.username:
            modalType = request.form.get("modalType")
            newProductPrice = request.form.get("newProductPrice")

            try:
                # Ignore those try-hards who write out ...FMC in their input, smh
                insensitive_fmc = re.compile(re.escape('fmc'), re.IGNORECASE)
                newProductPrice = insensitive_fmc.sub('', newProductPrice)
                newProductPrice = round(float(newProductPrice), 2) < 0
            except TypeError:
                pass


                if modalType == "editProductPrice":
                    if not_float(newProductPrice):
                        flash("Price must be a number", category="error")
                    elif newProductPrice < 0:
                        flash("Cannot set negative price", category="error")
                    else:
                        product.price = newProductPrice
                        db.session.commit()
                elif modalType == "removeProduct":
                    product.listed = False
                    db.session.commit()
                elif modalType == "resellProduct":
                    product.listed = True
                    product.price = newProductPrice
                    db.session.commit()
                elif modalType == "purchaseProduct":
                    seller = User.query.filter_by(username=product.username).first()
                    if current_user.balance < product.price:
                        flash("Not enough FMC", category="error")
                    else:
                        current_user.balance -= product.price
                        seller.balance += product.price

                        product.listed = False
                        product.username = current_user.username

                        db.session.commit()
        else:
            flash("You do not own the product!", category="error")

    user = User.query.filter_by(username=username).first()

    loadImgs(user.posts)

    userSelling = [product for product in user.posts if product.listed == True]
    random.shuffle(userSelling)
    groupedUserSelling = []

    for i in range(0, len(userSelling), 6):
        groupedUserSelling.append(userSelling[i:i+6])
    singleSelling = False
    if len(userSelling) == 1:
        singleSelling = True

    userOwned = [product for product in user.posts if product.listed == False]
    random.shuffle(userOwned)
    groupedUserOwned = []

    for i in range(0, len(userOwned), 6):
        groupedUserOwned.append(userOwned[i:i+6])
    singleOwned = False
    if len(userOwned) == 1:
        singleOwned = True


    return render_template("user/profile.html", user=user, userSelling=groupedUserSelling, userOwned=groupedUserOwned, singleOwned=singleOwned, singleSelling=singleSelling, userOwnedLen=len(userOwned), userSellingLen=len(userSelling), current_user=current_user)


@user.route('/chatroom')
@login_required
def chatroom_page():
    messages = Message.query.all()

    return render_template('user/chatroom.html', user=current_user, messages=messages)
