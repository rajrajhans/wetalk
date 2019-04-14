from datetime import *
from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE=SqliteDatabase('social.db')

#UserMixin goes first, and then Model since User is essentially a Model class, and UserMixin just enhances it's functionality

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user << self.following())
            (Post.user == self)

        )

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
    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

#Related name is what the rel model would call this model
class Post(Model):
    timestamp = DateTimeField(default=datetime.now)
    user = ForeignKeyField(
        model=User,
        related_name='posts'
    )
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)

class Relationship(Model):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DATABASE
        indexes = (
            ((('from_user', 'to_user'), True),)
        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()