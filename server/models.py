from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    # created_at = db.Column(db.DateTime, server_default=db.func.now())
    # updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    recipes = db.relationship("Recipe", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, username=None, password=None, **kwargs):
        super().__init__(username=username, **kwargs)
        if password:
            self.password_hash = password 
        
    serialize_rules = ("-recipes", "-password_hash")
    
    
    @hybrid_property
    def password_hash(self):
        raise AttributeError("you cannot see passwords!")

        
    @password_hash.setter
    def password_hash(self, new_password):
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        self._password_hash = hashed_password 
    
    def authenticate(self, password_to_check):
        return bcrypt.check_password_hash(self._password_hash, password_to_check)

    def __repr__(self):
        return f"User {self.username}, ID {self.id}"
class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # created_at = db.Column(db.DateTime, server_default=db.func.now())
    # updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    user = db.relationship("User", back_populates="recipes")
    
    serialize_rules = ("-user",)
    
    @validates("instructions")
    def validate_instructions(self, key, instructions):
        if len(instructions) <= 50:
            raise ValueError("Instructions must be at least 50 chars long.")
        return instructions 
    
    def __repr__(self):
        return f"Recipe {self.title}, ID {self.id}"
    