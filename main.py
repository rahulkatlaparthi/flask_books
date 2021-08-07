from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import random
# New

# Init app
from sqlalchemy import and_, null
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///relationship.db'
# app.config['SQLALCHEMY_BINDS'] = {'two' : 'sqlite:///two.db'}


# Init database
db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    confirm_password = db.Column(db.String(100))
    posts = db.relationship('Post', backref='user')

    def __init__(self, name, email, password, confirm_password):
        self.name = name
        self.email = email
        self.password = password
        self.confirm_password = confirm_password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'password', 'confirm_password')


user_schema = UserSchema()
user_schema = UserSchema(many=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.String(80))
    author = db.Column(db.String(80))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))

    def __init__(self, title, description, author, quantity, price, user_id, image_id):
        self.title = title
        self.description = description
        self.author = author
        self.quantity = quantity
        self.price = price
        self.user_id = user_id
        self.image_id = image_id


class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'author', 'quantity', 'price', 'user_id', 'image_id')


post_schema = PostSchema()
post_schema = PostSchema(many=True)


def getextension(mimeType):
    a = "image/"
    if len(mimeType) == 0:
        return null
    if a in mimeType:
        return "." + mimeType.replace("image/", "")
    return null


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(80))
    mimeType = db.Column(db.String(90))
    posts = db.relationship('Post', backref='image')

    def __init__(self, file_path, mimeType):
        self.file_path = file_path
        self.mimeType = mimeType


class ImageSchema(ma.Schema):
    class Meta:
        fields = ('id', 'file_path', 'mimeType')


image_schema = ImageSchema()
image_schema = ImageSchema(many=True)


@app.route('/image', methods=['POST'])
def upload_file():
    file = request.files['file']
    file_path = request.form['file_path']
    f = random.random()
    type(f)
    s = str(f)
    p = file.content_type
    g = getextension(p)
    print(g)
    s = s + g
    file.save(os.path.join(file_path, s))
    image = Image(file_path, p)
    db.session.add(image)
    # db.session.add(user)
    db.session.commit()

    return jsonify(isError=False, message="Successfully created")


@app.route('/image', methods=['GET'])
def getimage():
    all_drink = Image.query.all()
    result = image_schema.dump(all_drink)
    return jsonify(result)


@app.route("/post", methods=['GET'])
def getpost():
    all_drink = Post.query.all()
    result = post_schema.dump(all_drink)
    return jsonify(result)


@app.route('/post', methods=['POST'])
def createpost():
    title = request.json['title']
    description = request.json['description']
    author = request.json['author']
    quantity = request.json['quantity']
    price = request.json['price']
    userid = request.json['userid']
    user = User.query.filter_by(id=userid)
    lib = user_schema.dump(user)
    if len(lib)==0:
        return jsonify(isError=True, message="Please add user id")
    users=lib[0]
    user_id=users['id']
    imageid = request.json['imageid']
    if imageid !=None:
       image = Image.query.filter_by(id=imageid)
       lib = image_schema.dump(image)
       if len(lib)==0:
          return jsonify(isError=True, message="Image id Not exist")
       else:
         images=lib[0]
         image_id=images['id']
    else:
        image_id=0
    # user = users[0]

    # lib = user_schema.dump(user_id)
    print(user_id)
    # user_id=lib[0]

    post = Post(title, description, author, quantity, price, user_id, image_id)
    db.session.add(post)
    # db.session.add(user)
    db.session.commit()
    return jsonify(isError=False, message="Successfully created")


@app.route('/register', methods=['POST'])
def createuser():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    confirm_password = request.json['confirm_password']
    user = User.query.filter_by(email=email)
    lib = user_schema.dump(user)
    print(len(lib))
    if len(lib) == 0:
        if password == confirm_password:
            user = User(name, email, password, confirm_password)
            db.session.add(user)
            db.session.commit()
            return jsonify(isError=False, message="Successfully created")
        return jsonify(isError=True, message="Password and Confirm_Password should be same")
    return jsonify(isError=True, message="Please give new email")


@app.route('/getallusers', methods=['GET'])
def get_nonv():
    all_drink = User.query.all()
    result = user_schema.dump(all_drink)
    return jsonify(result)


@app.route('/login', methods=['POST'])
def createlogin():
    email = request.json['email']
    password = request.json['password']
    user = User.query.filter_by(email=email, password=password)

    lib1 = user_schema.dump(user)
    print(lib1)

    if (len(lib1) > 0):
        return jsonify(isError=False, message="Login Success", list=lib1)
    return jsonify(isError=True, message="Please check email and password", list=lib1)


# lib1 = user_schema.dump(user)
# print(lib2)
# if (len(lib1)>0):
#     if(len(lib2)>0):
#        return jsonify(isError=False, message="Login Success")
#     return jsonify(isError=False, message="Please check Password")
# return jsonify(isError=True, message="Please check email and password",list=lib2)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=33660, debug=True)
