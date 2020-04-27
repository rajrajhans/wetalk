from datetime import *
from peewee import *
from flask_login import UserMixin, AnonymousUserMixin, login_user
from flask_bcrypt import generate_password_hash
from hashlib import md5
import os

DATABASE_proxy = Proxy()

if 'HEROKU' in os.environ:
    import urllib.parse, psycopg2

    urllib.parse.uses_netloc.append('postgres')
    url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
    DATABASE = PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname,
                                  port=url.port)
    DATABASE_proxy.initialize(DATABASE)
else:
    DATABASE = SqliteDatabase('social1.db')
    DATABASE_proxy.initialize(DATABASE)


# UserMixin goes first, and then Model since User is essentially a Model class, and UserMixin just enhances it's functionality

class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'


class User(UserMixin, Model):
    username = CharField(unique=True)
    name = CharField(max_length=30)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE_proxy
        order_by = ('-joined_at',)

    def get_posts(self):
        return Post.select().where(Post.user == self).order_by(Post.timestamp.desc())

    def get_stream(self):
        return Post.select().where(
            (Post.user << self.following()) |  # all posts from people Im following
            (Post.user == self)  # OR my own posts
        ).order_by(Post.timestamp.desc())

    # a join on to_user removes the users who are not following any users from the result table
    # a join on from_user removes the users who are not following anyone from the list

    def following(self):
        """The users that we are following."""
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )

    def followers(self):
        """Get users following the current user"""
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
        )

    def gravatar_url(self, size=80):
        return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
               (md5(self.email.strip().lower().encode('utf-8')).hexdigest(), size)

    def display(self):
        if self.is_admin == True:
            return 'inline-block'
        else:
            return 'none'

    def hasUserLiked(self, post_id):
        query = Post.select().join(
            Likes, on=Likes.post_id
        ).where(
            Likes.user_id == self,
            Likes.post_id == post_id
        )
        try:
            ret = query[0].id
            return 1
        except:
            return 0

    @classmethod
    def create_user(cls, username, name, email, password, admin=False):
        try:
            with DATABASE.transaction():
                user = cls.create(
                    username=username,
                    email=email,
                    name=name,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")
        else:
            login_user(user)


# Related name is what the rel model would call this model
class Post(Model):
    timestamp = DateTimeField(default=datetime.now)
    user = ForeignKeyField(
        model=User,
        related_name='posts'
    )
    content = TextField()
    image = BlobField(null=True)
    imageThere = BooleanField(default=0)
    numLikes = IntegerField(default=0)
    numComments = IntegerField(default=0)

    def getLikes(self):
        """returns list of users who liked the post"""
        return (
            Post.select().join(
                Likes, on=Likes.post_id
            ).where(
                Likes.post_id == self
            )
        )

    class Meta:
        database = DATABASE_proxy
        order_by = ('-timestamp',)


class Relationship(Model):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DATABASE_proxy
        indexes = (
            ((('from_user', 'to_user'), True),)
        )


class Likes(Model):
    user_id = ForeignKeyField(User, related_name='user_likes', null=True)
    post_id = ForeignKeyField(Post, related_name='post_likes', null=True)

    class Meta:
        database = DATABASE_proxy


class Comments(Model):
    user_id = ForeignKeyField(User, related_name='user_likes', null=True)
    post_id = ForeignKeyField(Post, related_name='post_likes', null=True)
    comment = TextField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        database = DATABASE_proxy


def initialize():
    DATABASE_proxy.connection()
    DATABASE_proxy.create_tables([User, Post, Relationship, Likes, Comments], safe=True)
    DATABASE_proxy.close()
