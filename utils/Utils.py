import configparser

import redis

from utils.Bloomfilter import BloomFilter
from utils.DbPoolUtil import DbPoolUtil


class Redis:
    client = None

    @staticmethod
    def connect():
        Redis.client = redis.Redis(Conf.redis_ip, Conf.redis_port, password=Conf.redis_password,
                                   db=Conf.redis_db_name)

    @staticmethod
    def push_url(url):
        if Utils.get_bloomfilter_instance().isContains(str(url)):
            return
        else:
            Utils.get_bloomfilter_instance().insert(str(url))
        Redis.client.lpush('music_url', url)

    @staticmethod
    def pop_url():
        return Redis.client.rpop('music_url')


class Utils:
    bloomfilter_redis_instance = None

    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        config.read("spider.conf")

        Conf.sql_ip = config.get("base_info", "sql_ip")
        Conf.sql_port = config.getint("base_info", "sql_port")
        Conf.sql_user = config.get("base_info", "sql_user")
        Conf.sql_pwd = config.get("base_info", "sql_pwd")
        Conf.sql_db_name = config.get("base_info", "sql_db_name")

        Conf.redis_ip = config.get("base_info", "redis_ip")
        Conf.redis_port = config.getint("base_info", "redis_port")
        Conf.redis_password = config.get("base_info", "redis_password")
        Conf.redis_db_name = config.getint("base_info", "redis_db_name")
        Conf.bloomfilter_redis_db_name = config.getint("base_info", "bloomfilter_redis_db_name")

        Conf.log_path = config.get("base_info", "log_path")
        Conf.driver_path = config.get("base_info", "driver_path")

    @staticmethod
    def get_bloomfilter_instance():
        if not Utils.bloomfilter_redis_instance:
            Utils.bloomfilter_redis_instance = BloomFilter(host=Conf.redis_ip, port=Conf.redis_port,
                                                           password=Conf.redis_password,
                                                           db=Conf.bloomfilter_redis_db_name)
        return Utils.bloomfilter_redis_instance


class Conf:
    sql_ip = ""
    sql_port = 0
    sql_user = ""
    sql_pwd = ""
    sql_db_name = ""

    redis_ip = ""
    redis_port = 0
    redis_password = ""
    redis_db_name = 0
    bloomfilter_redis_db_name = 0

    log_path = ""
    driver_path = ""


class DbUtils:
    dbpool_util = None

    @staticmethod
    def connect():
        config = {
            'host': Conf.sql_ip,
            'port': Conf.sql_port,
            'database': Conf.sql_db_name,
            'user': Conf.sql_user,
            'password': Conf.sql_pwd,
            'charset': "utf8mb4"
        }
        DbUtils.dbpool_util = DbPoolUtil(config)

    @staticmethod
    def insert_music(music):
        sql = 'insert into music (song_id, title, author, album, comment_count, url) values (%s, %s, %s, %s, %s, %s)'
        DbUtils.dbpool_util.execute_iud(sql, music)
