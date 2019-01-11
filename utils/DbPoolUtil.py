from DBUtils.PooledDB import PooledDB
import importlib


class DbPoolUtil(object):
    def __init__(self, config):
        db_creator = importlib.import_module("pymysql")
        self.__pool = PooledDB(db_creator, maxcached=50, maxconnections=1000, maxusage=1000, **config)

    def execute_query(self, sql, args=()):
        """
        执行查询语句，获取结果
        :param sql:sql语句，注意防注入
        :param args:传入参数
        :return:结果集
        """
        result = ()
        conn = self.__pool.connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args)
            result = cur.fetchall()
        except Exception as e:
            print('异常信息:' + str(e))
        cur.close()
        conn.close()
        return result

    def execute_query_single(self, sql, args=()):
        """
        执行查询语句，获取单行结果
        :param sql:sql语句，注意防注入
        :param args:传入参数
        :return:结果集
        """
        result = ()
        conn = self.__pool.connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args)
            result = cur.fetchone()
        except Exception as e:
            print('异常信息:' + str(e))
        cur.close()
        conn.close()
        return result

    def execute_iud(self, sql, args=()):
        """
        执行增删改语句
        :param sql:sql语句，注意防注入
        :param args:传入参数
        :return:影响行数,mysql和sqlite有返回值
        """
        conn = self.__pool.connection()
        cur = conn.cursor()
        count = 0
        try:
            result = cur.execute(sql, args)
            conn.commit()
            count = result
        except Exception as e:
            print('异常信息:' + str(e))
            conn.rollback()
        cur.close()
        conn.close()
        return count

    def execute_many_iud(self, sql, args):
        """
        批量执行增删改语句
        :param sql:sql语句，注意防注入
        :param args:参数,内部元组或列表大小与sql语句中参数数量一致
        :return:影响行数，mysql和sqlite有返回值
        """
        conn = self.__pool.connection()
        cur = conn.cursor()
        count = 0
        try:
            result = cur.executemany(sql, args)
            conn.commit()
            count = result
        except Exception as e:
            print('异常信息:' + str(e))
            conn.rollback()
        cur.close()
        conn.close()
        return count
