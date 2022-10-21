from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import  datetime, timedelta
from sqlalchemy_serializer import  SerializerMixin
from  flask_httpauth import  HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
from tinydb import TinyDB, Query
import  random
app = Flask(__name__)

app.config['SECRET_KEY'] = 'makbhjfsjaaaaaaaaadadad'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

api_db = TinyDB('db.json')
def add_api_user():
    api_db.insert({'user': generate_password_hash('akoakndjhvhgcdgjadbkj')})




STATUS_SUCCESS = {'status': 200}
users = api_db.all()
all_api_users = {}
for i in range(len(users)):
    for key in users[i]:
        all_api_users[key] = users[i][key]
# print(all_api_users)

@auth.verify_password
def verify_password(username, password):
    if username in all_api_users and \
            check_password_hash(all_api_users.get(username), password):
        return username

class Families(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    family = db.Column(db.String(200), unique=True, nullable=False)
    users = db.relationship('User', backref='families')

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    #'id', 'email', 'country', 'first_name', 'last_name',
    serialize_only = ('id', 'email', 'country', 'posts', "profile_img", 'first_name', 'family_id', 'last_name', 'followers', 'dob', 'about', 'user_name', 'stories')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    country = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.Date(), nullable=True)
    about = db.Column(db.String(400), nullable=True, default='')
    user_name = db.Column(db.String(100), nullable=True,  default='')
    profile_img = db.Column(db.String(200), unique=True, nullable=True,  default='https://imgur.com/a/OUwvN8c')
    followers = db.relationship('Followers', backref='users')
    posts = db.relationship('Posts', backref='users')
    post_likes = db.relationship('PostLikes', backref='users')
    post_comments = db.relationship('PostComments', backref='users')
    stories = db.relationship('Story', backref='users')
    messages = db.relationship('Messages', backref='users')
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), default=random.randint(1, 5))


class Followers(db.Model, SerializerMixin):
    __tablename__ = 'followers'
    serialize_only = ('id', 'type', 'follower_id', 'following_id')
    id = db.Column(db.Integer, primary_key=True,  nullable=False)
    type = db.Column(db.String(200), nullable=False)
    #id of the follower
    follower_id = db.Column(db.Integer, nullable=False)
    #id of the person being followed
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'))


#post types
#keys for post types all appear in lowercase
'''
Moods
Selfie
SVlog
Memes
Tags
'''

tag_connect = db.Table('tag_connect',
                    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                    db.Column('tag_id', db.Integer, db.ForeignKey('poststags.id'))
                    )

tag_users = db.Table('tag_users',
                    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
                    )


class PostTags(db.Model, SerializerMixin):
    __tablename__ = 'poststags'

    serialize_only = ('tag', 'id')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    # post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    tag = db.Column(db.String(200), nullable=False)



class Posts(db.Model, SerializerMixin):
    __tablename__ = 'posts'
    serialize_only = ('id', 'user_id', 'text', 'media', 'mood', 'type', 'country', 'created_at', 'post_likes', 'post_comments', 'post_tags', 'reactions')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.String(2000), default='', nullable=True)
    media = db.Column(db.String(1000), nullable=True)
    mood = db.Column(db.String(200), default='m1', nullable=True)
    type = db.Column(db.String(30), nullable=False)
    country = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.Date, default=datetime.now(), nullable=False)
    post_likes = db.relationship('PostLikes', backref='posts')
    post_comments = db.relationship('PostComments', backref='posts')
    post_tags = db.relationship('PostTags', secondary=tag_connect, backref='tags')
    user_tags = db.relationship('User', secondary=tag_users, backref='user_tags')
    reactions = db.relationship('Reactions', backref='posts')

    # def __repr__(self):
    #     return '<Posts %r %r %r>' % (self.id, self.setting_type, self.value)


class PostLikes(db.Model, SerializerMixin):
    serialize_only = ('id', 'user_id')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class PostComments(db.Model, SerializerMixin):
    __tablename__='comments'
    serialize_only = ('id', 'comment', 'media_gif', 'post_id', 'user_id', 'sub_comments', 'comment_likes')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    comment = db.Column(db.String(700), nullable=False)
    media_gif = db.Column(db.String(400), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_likes = db.relationship('CommentLikes', backref='comments_likes')
    sub_comments = db.relationship('SubComments', backref='sub_comments')

class CommentLikes(db.Model, SerializerMixin):
    __tablename__ = 'comments_likes'
#types
#lovely, warm,
    serialize_only = ('id', 'user_id')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    type = db.Column(db.String(20), default='lovely')
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class SubComments(db.Model, SerializerMixin):
    __tablename__ = 'sub_comments'
    serialize_only = ('id', 'comment', 'media_gif', 'comment_id', 'user_id')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    comment = db.Column(db.String(700), nullable=False)
    media_gif = db.Column(db.String(400), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))



class Reactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    reaction = db.Column(db.String(200), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


class Story(db.Model, SerializerMixin):

    serialize_only = ('text', 'background_color', 'media', 'created_at', 'users.id')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.String(200), nullable=True)
    background_color = db.Column(db.String(200), default='#0000ff', nullable=True)
    media = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.Date, default=datetime.now(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    isAd = db.Column(db.Boolean, default=False, nullable=False)


class Messages(db.Model, SerializerMixin):
    serialize_only = ('text', 'background_color', 'media', 'created_at', 'users.id')
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.String(200), nullable=True)
    background_color = db.Column(db.String(200), nullable=True)
    media = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.Date, default=datetime.now(), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, nullable=False)

# db.create_all()
@app.before_first_request
def create_tables():
    db.create_all()


#app routes
#----------------------------------------------------------------------------------------

@app.route('/')
@auth.login_required
def home():
    print(users)
    return jsonify({'status': 200})

#Families
@app.route('/add-family/<string:family>', methods=['POST'])
def add_family(family):
    family = Families(family=family)
    db.session.add(family)
    db.session.commit()

#user routes
@app.route('/post-user/<string:email>/<string:country>/<string:firstname>/<string:lastname>', methods=['POST'])
def post_user(email, country, firstname, lastname):
    user = User(email=email, country=country, first_name=firstname, last_name=lastname)
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': 200})

@app.route('/fetch-user/<int:id>')
def fetch_user(id):
    user = User.query.get(id)
    print(user.to_dict())
    return jsonify({'data': user.to_dict()})


@app.route('/fetch-user-em/<string:email>')
def fetch_user_em(email):
    user = User.query.filter_by(email=email).first()
    user_json=user.to_dict()

    posts = Posts.query.filter(Posts.type == 'mood', Posts.user_id == user.id).order_by(Posts.id.desc()).first()
    mood = posts.to_dict()
    tags = posts.post_tags
    tag_list = []
    for i in tags:
        tag_list.append(i.tag)
    mood['post_tags'] = tag_list

    for i in user_json['posts']:
        print(i)
        post = Posts.query.get(i['id'])
        tags = post.post_tags
        tags_vals = []
        for u in tags:
            tags_vals.append(str(u.tag))
        i['post_tags'] = tags_vals
    if(mood):
        user_json['mood'] = mood
    # compartmentalize posts
    moods = get_by_type(user_json['posts'], 'mood')
    selfie = get_by_type(user_json['posts'], 'selfie')
    svlog = get_by_type(user_json['posts'], 'svlog')
    memes = get_by_type(user_json['posts'], 'memes')

    user_json['moods'] = moods
    user_json['selfie'] = selfie
    user_json['svlog'] = svlog
    user_json['memes'] = memes
    return jsonify({'data': user_json})

def get_by_type(posts, type):
    posts_list = []
    for i in posts:
        if(i['type'] == type):
            posts_list.append(i)
    return posts_list


@app.route('/fetch-users')
def fetch_users():
    user = User.query.all()
    users = [i.to_dict() for i in user]
    return jsonify({'data': users})


@app.route('/edit-user/<string:email>', methods=['POST'])
def edit_user(email):
    user = User.query.filter_by(email=email).first()
    data = request.json
    # keys must match db fields
    res_data = {
        'about': data['about'] if data['about'].length  > 0 else user.about,
        'user_name':  data['user_name'] if data['user_name'].length  > 0 else user.user_name,
        'country': data['user_name'] if data['country'].length > 0 else user.country,
    }
    keys = list(res_data.keys())
    print(user.id)
    user.about =  res_data['about']
    user.user_name = res_data['user_name']
    user.country = res_data['country']
    db.session.commit()


    return (jsonify(STATUS_SUCCESS))


@app.route('/edit-user/change-family/<string:email>/<int:id>', methods=['POST'])
def edit_user_family(email, id):
    user = User.query.filter_by(email=email).first()
    res_data = request.json
    # keys must match db fields
    user.family_id = res_data['family_id']
    db.session.commit()

    return (jsonify(STATUS_SUCCESS))

@app.route('/edit-user/change-profile-image/<string:email>', methods=['POST'])
def edit_user_profile_image(email):
    user = User.query.filter_by(email=email).first()
    res_data = request.json
    user.profile_img = res_data['profile_image']
    db.session.commit()

    return (jsonify(STATUS_SUCCESS))


#Follower routes
@app.route('/follow/<int:follower_id>/<int:followed_id>/<string:type>')
def follow(follower_id,followed_id, type):
    #can folllow as a friend, lover family etc
    isFollowing = Followers.query.filter_by(following_id=followed_id, follower_id=follower_id).first()
    if not isFollowing:
        follow = Followers(follower_id=follower_id, type=type, following_id=followed_id)
        db.session.add(follow)
        db.session.commit()
        return jsonify({'status': 200})
    return jsonify({'status': 200})

@app.route('/unfollow/<int:following_id>/<int:follower_id>')
def unfollow(following_id, follower_id):
    follow = Followers.query.filter_by(following_id=following_id, follower_id=follower_id)[0]
    db.session.delete(follow)
    db.session.commit()


#post routes-----------------------------------------
@app.route('/post-post', methods=['POST'])
def post_post():
    data = request.get_json()
    user_id = User.query.filter_by(email=data['email']).first()
    text = data['text']
    media = data['media']
    mood = data['mood']
    type = data['type']
    country = data['country']
    post_tags = data['postTags']
    users_tags = data['userTags']

    post = Posts(
        user_id=user_id.id,
        text=text,
        media=media,
        mood=mood,
        type=type,
        country=country,
    )

    db.session.add(post)
    db.session.flush()
    post_id = post.id
    db.session.commit()

    for i in post_tags:
        tag = PostTags.query.filter_by(tag=i).first()
        if (tag):
            post.post_tags.append(tag)
            db.session.commit()
        else:
            new_tag = PostTags(tag=i)
            db.session.add(new_tag)
            post.post_tags.append(new_tag)
            db.session.commit()
    #takes userIds.
    for i in users_tags:
        new_tag = User.query.get(i)
        db.session.add(new_tag)
        post.user_tags.append(new_tag)
        db.session.commit()



    # for tag in users_tags:
    #     a_tag = PostTags(tag=tag['tag'])
    #     db.session.add(a_tag)
    #     post.posts.append(a_tag)
    #     db.session.commit()


    return jsonify({'status': 200})

@app.route('/like-post/<int:id>/<string:email>', methods=['POST'])
def like_post(id, email):
    user = User.query.filter_by(email=email).first()
    query = PostLikes.query.filter(PostLikes.post_id==id, PostLikes.user_id==user.id).first()
    if query:
        db.session.delete(query)
        db.session.commit()
    else:
        post_like = PostLikes(post_id=id, user_id=user.id)
        db.session.add(post_like)
        db.session.commit()
    return jsonify(STATUS_SUCCESS)


@app.route('/like-comment/<int:id>/<int:user_id>/<string:type>', methods=['POST'])
def like_comment(id, user_id, type):
    query = CommentLikes.query.filter(CommentLikes.comment_id==id, CommentLikes.user_id==user_id).first()
    if query:
        db.session.delete(query)
        db.session.commit()
    else:
        comment_like = CommentLikes(comment_id=id, user_id=user_id, type=type)
        db.session.add(comment_like)
        db.session.commit()
    return jsonify(STATUS_SUCCESS)

@app.route('/post-mood', methods=['POST'])
def post_mood():
    res = request.json
    email = res['email']
    print(email)
    user = User.query.filter_by(email=email).first()
    new_mood = Posts(
        user_id=user.id,
        text=res['text'],
        type='mood',
        mood=res['mood']
    )

    db.session.add(new_mood)
    db.session.commit()

    tags = res['tags']
    print(tags)
    for i in tags:
        tag = PostTags.query.filter_by(tag=i).first()
        if(tag):
            new_mood.post_tags.append(tag)
            db.session.commit()
        else:
            new_tag = PostTags(tag=i)
            db.session.add(new_tag)
            new_mood.post_tags.append(new_tag)
            db.session.commit()
    db.session.commit()
    return jsonify(STATUS_SUCCESS)

@app.route('/get-mood/<string:email>', methods=['GET'])
def get_mood(email):
    user = User.query.filter_by(email=email).first()
    posts = Posts.query.filter(Posts.type=='mood', Posts.user_id==user.id).order_by(Posts.id.desc()).first()
    mood = posts.to_dict()
    tags = posts.post_tags
    tag_list = []
    for i in tags:
        tag_list.append(i.tag)
    mood['post_tags'] = tag_list

    return ({'data': mood})

@app.route('/get-posts')
def get_posts():
    posts = Posts.query.all()
    posts_data = []
    for i in posts:
        posts_data.append(
            i.to_dict()
        )

    for i in posts_data:
        user = User.query.get(i['user_id'])
        i['user'] = {
            'username':user.user_name,
            'country':user.country,
            'img':user.profile_img
        }

    for post in posts_data:
        for comment in post['post_comments']:
            user = User.query.get(comment['user_id'])
            comment['user'] = {
                'username': user.user_name,
                'country': user.country,
                'img': user.profile_img
            }

    return jsonify({'data':posts_data})

@app.route('/get-comments/<int:post_id>')
def get_comments(post_id):
    comments = PostComments.query.filter_by(post_id=post_id).all()
    empty_list = []
    for i in comments:
        empty_list.append(i.to_dict())
    return jsonify({'data': empty_list})

#gets a list of a specific type of post
@app.route('/get-post-types/<string:type>')
def get_post_types(type):
    posts = Posts.query.filter_by(type=type)
    post_types = []
    for row in posts:
        post_types.append(row.to_dict())
    return jsonify({'data':post_types})

@app.route('/edit-post/<int:id>')
def edit(id):
    post = Posts.query.get(id)
    payload = request.get_json()
    text = payload['text'] != '' if payload['text'] else post.text
    media = payload['media'] != '' if payload['media'] else post.media
    mood = payload['mood'] != '' if payload['mood'] else post.mood
    tags = payload['tags'] != '' if payload['tags'] else post.tags

    post.text = text
    post.media = media
    post.mood = mood
    post.tags = tags

    db.session.commit()
    return (jsonify(STATUS_SUCCESS))

@app.route('/delete-post/<int:id>/<int:user_id>')
def delete(id, user_id):
    post = Posts.query.get(id)
    serzalized_post = post.to_dict()
    if(serzalized_post.user_id == user_id):
        db.session.delete(post)
        db.session.commit()
        return jsonify(STATUS_SUCCESS)

@app.route('/delete-post-admin/<int:id>/<int:user_id>')
def delete_post_admin(id):
    post = Posts.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return jsonify(STATUS_SUCCESS)


#post likes and comments
@app.route('/create-comment/<int:post_id>/<int:user_id>', methods=['POST'])
def create_comment(post_id, user_id):
    res = request.get_json()
    media = ''
    if(res['media']):
        media = res['media']
    comment = PostComments(comment=res['text'], media_gif=media, post_id=post_id, user_id=user_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify(STATUS_SUCCESS)

#edit comments
@app.route('/edit-comment/<int:comment_id>/<int:user_id>')
def edit_comment(comment_id, user_id):
    comment = PostComments.query.filter(PostComments.id==comment_id, PostComments.user_id==user_id)
    data = request.get_json()
    res_data = data['data']
    keys = list(res_data.keys())
    for i in keys:
        if(len(data[i]) > 0):
            comment.i = data[i]
    db.session.commit()
    return (jsonify(STATUS_SUCCESS))

#delete comments
@app.route('/delete-comment/<int:comment_id>/<int:user_id>')
def delete_comment(comment_id, user_id):
    comment = PostComments.query.filter(id==comment_id, PostComments.user_id==user_id)
    sub_comments = comment.to_dict()['sub_comments']
    for sub in sub_comments:
        sub_ce = SubComments.query.get(sub['id'])
        db.session.delete(sub_ce)
        db.session.commit()
    db.session.delete(comment)
    db.session.commit()

#sub comments
@app.route('/create-sub-comment/<int:comment_id>/<int:user_id>')
def create_sub_comment(comment_id, user_id):
    res = request.get_json()
    data = res['data']
    comment = SubComments(comment=res['comment'], media_gif=res['media_gif'], comment_id=comment_id, user_id=user_id)
    db.session.add(comment)
    db.session.commit()
#edit comments
@app.route('/edit-sub-comment/<int:comment_id>/<int:user_id>')
def edit_sub_comment(comment_id, user_id):
    comment = SubComments.query.filter(PostComments.id==comment_id, PostComments.user_id==user_id)
    data = request.get_json()
    res_data = data['data']
    keys = list(res_data.keys())
    for i in keys:
        if(len(data[i]) > 0):
            comment.i = data[i]
    db.session.commit()
    return (jsonify(STATUS_SUCCESS))

#delete comments
@app.route('/delete-comment/<int:comment_id>/<int:user_id>')
def delete_sub_comment(comment_id, user_id):
    comment = SubComments.query.filter(id==comment_id, PostComments.user_id==user_id)
    db.session.delete(comment)
    db.session.commit()


#Reaction(react, unreact)
@app.route('/create-reaction/<int:post_id>/<int:user_id>/<string:type>')
def create_reaction(_post_id, _user_id, _type):
    reaction = PostLikes(post_id=_post_id, user_id=_user_id, type=_type)
    db.session.add(reaction)
    db.session.commit()

@app.route('/create-reaction/<int:comment_id>/<int:user_id>')
def remove_reaction(_comment_id, _user_id):
    reaction = PostLikes.query.get(_comment_id)
    db.session.delete(reaction)
    db.session.commit()


#stories
@app.route('/create-story/<string:email>')
def create_story(email):
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    color = data['backgroundColor'] if len(data['backgroundColor']) > 0 else '#0000ff'
    story = Story(text=data['text'],
                  background_color=color,
                  media=data['media'],
                  user_id=user.id
                  )
    db.session.add(story)
    db.session.commit()

@app.route('/get-story/<int:user_id>')
def get_story(user_id):
    next_24_hours = datetime.now() + timedelta(hours=24)
    user = User.query.get(user_id)
    following = user.to_dict()
    following = following['followers']
    followed_stories = []
    my_stories = []
    my_stories_objs = Story.query.filter(user_id==user_id).all()
    for my_story in my_stories_objs:
        my_stories.append(my_story.to_dict())
    for followed_id in following:
        followed_stories_objs = Story.query.filter(user_id==followed_id, Story.isAd==False).all()
        for followed_story in followed_stories_objs:
            followed_stories.append(followed_story.to_dict())

    return jsonify({'my_stories': my_stories, 'followed_stories': followed_stories})



if '__main__' == __name__:
    app.run(debug=True)
