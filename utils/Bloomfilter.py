import redis


class SimpleHash:
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(value.__len__()):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter:
    def __init__(self, host, port, password, db):
        self.key = 'uidlist'
        self.redis = redis.Redis(host=host, port=port, password=password, db=db)

    def is_contains(self, str_input):
        if str_input is None:
            return False
        if str_input.__len__() == 0:
            return False
        ret = False
        if self.redis.sadd(self.key, str_input) == 0:
            return True
        return ret

    def insert(self, str_input):
        self.redis.sadd(self.key, str_input)
