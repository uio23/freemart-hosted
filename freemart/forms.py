# Importing 3rd party components
from flask_wtf import FlaskForm

from sqlalchemy import func

from wtforms import  StringField, PasswordField, SubmitField, FileField, TextAreaField, DecimalField, RadioField, validators, ValidationError, EmailField

from passlib.hash import pbkdf2_sha256

# Importing freemart components
from .models import Product, User

from .helperFunc import isFloat


# ----- Form template definition ----- #

class RegisterForm(FlaskForm):
    username = StringField('username_label', validators=[validators.InputRequired(message="Username required"), validators.Length(min=4, max=12, message="Username must be between 4 and 12 charecters")])
    email = EmailField('email_label', validators=[validators.InputRequired(message="Email required"), validators.Email('Enter valid email')])
    password = PasswordField('password_label', validators=[validators.InputRequired(message="Password required"), validators.Length(min=4, max=24, message="Password must be between 4 and 24 charecters")])
    submit_button = SubmitField('Sign up')

    def validate_username(self, username):
        username = username.data.strip()
        user = User.query.filter(func.lower(User.username)==func.lower(username)).first()

        if user:
            raise ValidationError("Username already exists (case insensitive)")

    def validate_email(self, email):
        email = email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            raise ValidationError("Account with this email already exists")



def invalid_credentials(form, feild):
    username = form.username.data.strip()
    user = User.query.filter(func.lower(User.username)==func.lower(username)).first()

    if not user:
        raise ValidationError("Incorrect username of password")
    elif not pbkdf2_sha256.verify(form.password.data, user.password):
        raise ValidationError("Incorrect username of password")
class LoginForm(FlaskForm):
    username = StringField("username_label", validators=[validators.InputRequired(message="Username required")])
    password = PasswordField("password_label", validators=[validators.InputRequired(message="Password required"), invalid_credentials])
    submit_button = SubmitField('Login')



class PostForm(FlaskForm):
    productName = StringField("product_name_label", validators=[validators.InputRequired(message="Name required"), validators.Length(min=0, max=50, message="Name too long (50char max)")])
    productDescription = TextAreaField("product_description_label", validators= [validators.Length(min=0, max=140, message="Description too long (140char max)")])
    productPrice = DecimalField("product_price_label", places=2, validators=[validators.InputRequired(message="Price required"), validators.NumberRange(min=0.00, message="Price cannot be negative")])
    productImage = FileField("product_image_label", validators=[validators.InputRequired(message="Image required")])
    submit_button = SubmitField('Post!')

    def validate_productName(self, productName):
        productName = productName.data

        if not productName.replace(' ','').isalpha():
            raise ValidationError("Name must only contain letters")
        product = Product.query.filter(func.lower(Product.name)==func.lower(productName)).first()

        if product:
            raise ValidationError("A product with this name already exists (case insensitive)")

    def validate_productPrice(self, productPrice):
        productPrice = productPrice.data
        if not isFloat(productPrice):
            raise ValidationError("Price must be a number")

    def validate_productImage(self, productImage):
        productImage = productImage.data

        if productImage.filename.split('.')[-1] not in ('jpg', 'png', 'jpeg'):
            raise ValidationError('Only jpg, jpeg or png supported')



class QuizForm(FlaskForm):
    qOne = RadioField("", choices=[("True", "True"), ("False", "False")], validators=[validators.InputRequired(message="Please answer this question")])
    qTwo = RadioField("", choices=[("True", "True"), ("False", "False")], validators=[validators.InputRequired(message="Please answer this question")])
    qThree = RadioField("", choices=[("True", "True"), ("False", "False")], validators=[validators.InputRequired(message="Please answer this question")])
    submit_button = SubmitField('Submit')

    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.qOne.label = questions[0][0]
        self.qTwo.label = questions[1][0]
        self.qThree.label = questions[2][0]

        self.questions = questions
