from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy #导入扩展类
import os
import click

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'watchlist_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)




#############################################
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

#############################################

@app.cli.command() #注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')    #设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:    #判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    name = 'txm'

    movies = [
        {'title': 'My Neighbor Totoro', 'year':'1988'},
        {'title': 'Dead Poets Society', 'year':'1989'},
        {'title': 'A Perfect World', 'year':'1993'},
        {'title': 'Leon', 'year':'1994'},
        {'title': 'Mahjong', 'year':'1996'},
        {'title': 'Swallowtail Butterfly', 'year':'1996'},
        {'title': 'King of Comedy', 'year':'1999'},
        {'title': 'Devils on the Doorstep', 'year':'1999'},
        {'title': 'WALL-E', 'year':'2008'},
        {'title': 'The Pork of Music', 'year':'2012'},
    ]
    
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')



#######################################
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html')

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':    #判断是否是POST请求

        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')             # 显示错误提示
            return redirect(url_for('index'))   # 重定向回主页

        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)   # 创建记录
        db.session.add(movie)                   # 添加到数据库会话
        db.session.commit()                     # 提交数据库会话
        flash('Item created.')                  # 显示成功创建的提示
        return redirect(url_for('index'))       # 重定向回主页

    user = User.query.first()
    movies = Movie.query.all()

    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id = movie_id))
        
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item update.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

