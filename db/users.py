class User:
    users = dict()

    def __init__(self, user_id):
        self.user_id = user_id
        User.add_user(user_id=user_id,
                      user=self)
        self.city = None
        self.check_in = None
        self.check_out = None
        self.command = None
        self.time_of_use = None
        self.hotel_count = None
        self.need_photo = None
        self.num_photo = None
        self.hotels_res = []
        self.price_min = None
        self.price_max = None
        self.distance_min = None
        self.distance_max = None

    @classmethod
    def add_user(cls, user_id, user):
        cls.users[user_id] = user

    @classmethod
    def get_user(cls, user_id):
        if user_id in cls.users:
            return cls.users[user_id]
        User(user_id=user_id)
        return cls.users[user_id]

