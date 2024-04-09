from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Regexp, Email

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Kgaines092106!@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    summary = db.Column(db.Text)

    def __repr__(self):
        return f'<Partner {self.name}>'

class UserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Regexp(r'^[a-zA-Z]+$')])
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Submit')

@app.route('/')
def index():
    query = request.args.get('query')
    if query:
        filtered_partners = Partner.query.filter(Partner.name.ilike(f'%{query}%') | Partner.company.ilike(f'%{query}%')).all()
    else:
        filtered_partners = Partner.query.all()
    return render_template('index.html', partners=filtered_partners)

@app.route('/add', methods=['POST'])
def add_partner():
    new_partner = Partner(
        name=request.form['name'],
        company=request.form['company'],
        position=request.form['position'],
        contact=request.form['contact'],
        summary=request.form['summary']
    )
    db.session.add(new_partner)
    db.session.commit()
    return redirect('/')

@app.route('/remove/<int:id>', methods=['POST'])
def remove_partner(id):
    partner_to_remove = Partner.query.get_or_404(id)
    db.session.delete(partner_to_remove)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_partner(id):
    partner_to_edit = Partner.query.get_or_404(id)
    if request.method == 'POST':
        partner_to_edit.name = request.form['name']
        partner_to_edit.company = request.form['company']
        partner_to_edit.position = request.form['position']
        partner_to_edit.contact = request.form['contact']
        partner_to_edit.summary = request.form['summary']
        db.session.commit()
        return redirect('/')
    return render_template('edit.html', partner=partner_to_edit)

@app.route("/users")
def user_list():
    users = User.query.order_by(User.username).all()
    return render_template("user/list.html", users=users)

@app.route("/users/create", methods=["GET", "POST"])
def user_create():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("user_detail", id=user.id))

    return render_template("user/create.html", form=form)

@app.route("/user/<int:id>")
def user_detail(id):
    user = User.query.get_or_404(id)
    return render_template("user/detail.html", user=user)

# Initialize the database and create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
