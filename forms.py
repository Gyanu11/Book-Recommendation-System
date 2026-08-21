from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional, ValidationError, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="Email is required"), Email(message="Please enter a valid email address")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required")])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"), 
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"), 
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=8, message="Password must be at least 8 characters long"),
        Regexp(r'^(?=.*[A-Z])(?=.*[@$!%*?&])', 
               message="Password must include at least one uppercase letter and one special character")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"), 
        EqualTo('password', message="Passwords must match")
    ])
    admin_code = StringField('Admin Code (Optional)', validators=[Optional()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data.strip()).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')

    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data.strip()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    cover_url = StringField('Cover Image URL', validators=[DataRequired(), URL()])
    price = FloatField('Price ($)', validators=[DataRequired()])
    pdf_url = StringField('PDF Download URL', validators=[Optional(), URL()])
    is_featured = BooleanField('Feature this book on homepage')
    submit = SubmitField('Save Book')

class ResetAdminForm(FlaskForm):
    admin_code = StringField('Enter Admin Code to Confirm Reset', validators=[DataRequired()])
    submit = SubmitField('Delete Current Admin')


class ReviewForm(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    content = TextAreaField('Review', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Submit Review')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"), 
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"), 
        Email(message="Please enter a valid email address")
    ])
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data.strip()).first()
        if user and user.id != self._user_id:
            raise ValidationError('Username already taken. Please choose another one.')

    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data.strip()).first()
        if user and user.id != self._user_id:
            raise ValidationError('Email already registered. Please use a different email.')
