from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, validate
from marshmallow.validate import Length, Range, Regexp
from flask_json import FlaskJSON, JsonError, json_response, as_json
import logging
from logging.config import fileConfig


app = Flask(__name__)
#logging.basicConfig(filename='record.log', level=logging.DEBUG,
                       format="%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)s - %(message)s")
app.secret_key = "Secret key"
json = FlaskJSON(app)




app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:walkover@localhost/grocery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db=SQLAlchemy(app)



class Data(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    item = db.Column(db.String(10))
    price = db.Column(db.Integer())

    def __init__(self, id, item, price):
        self.id = id
        self.item = item
        self.price = price

class CreateSchema(Schema):
    id = fields.Int(required=True, Unique=True)
    item = fields.Str(required=True, validate=[Length(min=1,max=10), validate.Regexp(r"[A-Za-z]")])
    price=fields.Int(required=True, validate=validate.Range(min=1))

input_data={}

# @app.route("/")
# def main():
#     app.logger.debug("debug")
#     app.logger.info("info")
#     app.logger.warning("warning")
#     app.logger.error("error")
#     app.logger.critical("critical")
#     return ""


@app.route("/")
def Index():
    app.logger.info('Processing default request')
    page = request.args.get('page', 1, type=int)
    groceries = Data.query.order_by(Data.id).paginate(
        page, per_page=2)
    #all_data=Data.query.all()
    return render_template("index.html", groceries=groceries)



ROWS_PER_PAGE=5
@app.route("/insert", methods=['GET', 'POST'])
def insert():
    if request.method=='POST':
        id=request.form['id']
        item=request.form['item']
        price=request.form['price']
        my_data=Data(id, item, price)
        input_data['id']=id
        input_data['item']=item
        input_data['price']=price
    try:
        schema = CreateSchema()
        schema.load(input_data)
        db.session.add(my_data)
        try:
            db.session.commit()
            flash('Item added successfully')
            return redirect(url_for('Index'))
        except Exception as e:
            #logger.debug("Already exists")
            flash('grocery item already exists')
            return redirect(url_for('Index'))
    except ValidationError as err:
        flash(err)
        all_data=Data.query.all()
        return render_template("index.html",groceries=all_data)

    else:
         flash('Item Inserted Successfully')
         return redirect(url_for('Index'))



@app.route("/update", methods=['GET', 'POST'])
def update():
    update_data = {}
    if request.method=='POST':
        my_data=Data.query.get(request.form.get('id'))
        update_data['id']=request.form.get('id')
        update_data['item']=request.form['item']
        update_data['price']=request.form['price']
        try:
            schema=CreateSchema()
            schema.load(update_data)
        except ValidationError as err:
            flash(err)
            logger.log(err)
            all_data=Data.query.all()
            return render_template("index.html", groceries=all_data)
        else:
            my_data.item = request.form['item']
            my_data.price = request.form['price']
            db.session.commit()
            flash('Item Updated Successfully')
            return redirect(url_for('Index'))

@app.route("/delete/<id>/", methods=['GET', 'POST'])
def delete(id):
    my_data=Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash('Deleted')
    return redirect(url_for('Index'))

if __name__=="__main__":
    app.run(debug=True)

