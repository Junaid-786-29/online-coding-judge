class User:

    def __init__(self, user_id:int, username:str, email:str, password_hash:str):

        self.user_id=user_id
        self.username=username
        self.email=email
        self.password_hash=password_hash