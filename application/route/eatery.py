import os, secrets, cloudinary.uploader, cloudinary.api, cloudinary
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from application import db, bcrypt, allowed_file, app
from application.model.eatery import User
from application.model.menus import Menus
from werkzeug.utils import secure_filename
from PIL import Image

eat = Blueprint('eat',__name__)

@eat.route('/eat')
def eatery():
    return 'hi'

@eat.route('/lifeat')
@login_required
def lifeat():
    all_menu = Menus.query.all()
    all_user = User.query.all()
    all_menu.reverse()
    return render_template('chatting.html', all_menu=all_menu, all_user=all_user)

@eat.route('/register', methods=['GET'])
def register_get():
    auth = '/'
    button = 'how_to_reg'
    return render_template('register.html', auth=auth)

@eat.route('/register', methods=['POST'])
def register_post():
    email  = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username')
    profile_px = request.files['profile_px']
    
    check_user = User.query.filter_by(email=email).first()
    if check_user and check_user.username == username:
        return redirect('/')
    
    filename = secrets.token_hex(16)+'.jpg'
    # profile_px__path = '/home/yashuayaweh/Documents/PROGRAMMING/lifeat/application/static/imgs/profile_px'
    upload_img = cloudinary.uploader.upload(
        profile_px,
        folder = "lifeat/profile_pix/",
        public_id=filename,
        overwrite = True,
        resource_type = "image"
        )
    img = upload_img['url']
    new_user = User(username=username, email=email, profile_px=img, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    # profile_px.save(os.path.join(profile_px__path, filename))
    # picture = Image.open(os.path.join(profile_px__path, filename))
    # picture.save(os.path.join(profile_px__path  , filename), quality=20, optimize=True)
    #this was the previous obsolete code.
    flash('Your account have been created')
    return redirect('/')


@eat.route('/', methods=['GET'])
def login_get():
    auth = '/register'
    return render_template('login.html', current_user=current_user, auth=auth)

@eat.route('/loginpost', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    search_user = User.query.filter_by(email=email).first()
    if search_user and bcrypt.check_password_hash(search_user.password, password):
        login_user(search_user)
        return redirect('/lifeat')
    
    return redirect('/register')

@eat.route('/makemenu', methods=['GET'])
@login_required
def makemenu_get():
    return render_template('makemenu.html')

@eat.route('/makemenu', methods=['POST'])
@login_required
def makemenu_post():
    image = request.files['image']
    title = request.form.get('title')
    description = request.form.get('description')
    price = request.form.get('price')
    if allowed_file(image.filename):
        filename = secrets.token_hex(16)+'.jpg'
        upload_img = cloudinary.uploader.upload(
            image,
            folder = "lifeat/menu/",
            public_id=filename,
            overwrite = True,
            resource_type = "image"
            )
        img = upload_img['url']
        newMenu = Menus(title=title, description=description, picture=img, price=price, user_id=current_user.id)
        db.session.add(newMenu)
        db.session.commit()
        # image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # picture = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename), quality=20, optimize=True)
        # os.rename(os.path.join(app.config['UPLOAD_FOLDER'], filename), os.path.join(app.config['UPLOAD_FOLDER'], new_name+'.jpg'))
        return redirect('/lifeat')

@eat.route('/user/<user_id>' , methods=['GET'])
def user(user_id):
    user = User.query.get(user_id)
    return render_template('user.html', current_user=current_user, user=user)

@eat.route('/view_menu/<id>', methods=['GET'])
def view_menu(id):
    menu = Menus.query.get(id)
    return render_template('view_menu.html', current_user=current_user, menu=menu)

@eat.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    
    return redirect('/')