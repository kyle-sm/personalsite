from functools import cache

from flask import Flask, Markup, render_template, url_for
from google.cloud import firestore

app = Flask(__name__)
db = firestore.Client()


@app.route('/')
def homepage():
    return render_template('home.html',
                           links=get_links(),
                           title="Steven Kyle's Site")


@app.route('/about/')
def about():
    """That contains info about me and links to other places"""
    return render_template('about.html', links=get_links(), title="About")


@app.route('/posts/<string:post_url>')
def show_post(post_url):
    """ The page for any post """
    data = get_post(post_url)
    print(str(data['date']))
    return render_template(
        'post.html',
        links=get_links(),
        title=data['title'],
        date=data['date'].strftime('%A, %B %d, %Y at %I:%M%p'),
        post=Markup(data['content']))


@app.route('/posts/')
def post_home():
    return render_template('posthome.html',
                           links=get_links(),
                           title='Recent posts',
                           posts=get_recent())


@cache
def get_links() -> dict:
    """Organizes links for the sidebar"""
    links = dict()
    links['About'] = url_for('about')
    posts_ref = db.collection(u'posts')
    posts = posts_ref.stream()
    for post in posts:
        data = post.to_dict()
        links[data['title']] = url_for('show_post', post_url=post.id)
    return links


@cache
def get_post(url: str) -> dict:
    """Gets everything needed to display a post"""
    post_ref = db.collection(u'posts').document(url)
    return post_ref.get().to_dict()


@cache
def get_recent() -> list:
    """Gets five most recent posts"""
    posts = list()
    post_ref = db.collection(u'posts').order_by(u'date').limit(5)
    for post in post_ref.stream():
        postdata = post.to_dict()
        postdata['url'] = post.id
        postdata['date'] = postdata['date'].strftime(
            '%A, %B %d, %Y at %I:%M%p')
        postdata['content'] = Markup(postdata['content']).striptags()[:100]
        posts.append(postdata)
    return posts
