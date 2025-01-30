import os
import redis
import pickle
from utils import globalconstants
import logging
import threading

redis_config = {
    "local": {
        "REDISHOST": "localhost",
        "REDISPORT": 6379
    },
    "dev": {
        "REDISHOST": "10.207.156.179",
        "REDISPORT": 6379
    },
    "prod": {
        "REDISHOST": "localhost",
        "REDISPORT": 6379
    }
}
redis_host, redis_port, redis_client = None, None, None

redis_host = redis_config[os.environ['ENV']]["REDISHOST"]
redis_port = redis_config[os.environ['ENV']]["REDISPORT"]

if "SMARTQ_LOCAL_DEV" in os.environ:
    if os.environ['SMARTQ_LOCAL_DEV'] == "true":
        redis_host = 'localhost'
        redis_port = 6379


def init_redis(host, port):
    global redis_client
    global redis_connection
    try:
        print("redis init connect")
        redis_client = redis.Redis(host=host, port=port)
        redis_connection = redis_client.ping()
        print("redis connection status: " + str(redis_connection))
    except Exception as error:
        print("redis failed to connect")
        redis_connection = False


if redis_host and redis_port:
    x = threading.Thread(target=init_redis, args=(redis_host, redis_port))
    x.start()
redis_connection = False
print("skipped")


def redis_error_handler(value=None):
    def decorator(f):
        def applicator(*args, **kwargs):
            if not redis_connection:
                return value
            return f(*args, **kwargs)
            # try:
            #     return f(*args,**kwargs)
            # except redis.exceptions.ConnectionError:
            #     print("error")
            #     return value

        return applicator

    return decorator


redis_none_handler = redis_error_handler(None)


class Memcache():
    @staticmethod
    @redis_none_handler
    def all_keys():
        keys = redis_client.keys()
        new_keys = []
        for key in keys:
            new_keys.append(key.decode())
        return new_keys

    @staticmethod
    @redis_none_handler
    def multiget(keyarray):
        result = []
        for eachvalue in redis_client.mget(keyarray):
            if eachvalue is not None:
                result.append(pickle.load(eachvalue))
            else:
                result.append(eachvalue)
        return result

    @staticmethod
    @redis_none_handler
    def get(key, raw=False):
        value = redis_client.get(key)
        if raw:
            if value is None:
                return value
            else:
                return value.decode()
        if value is not None:
            value = pickle.loads(value)
        return value

    @staticmethod
    @redis_none_handler
    def set(key, value, raw=False, expire_time=None):
        if raw:
            return redis_client.set(key, value)
        if value is None:
            value = globalconstants.SPECIAL_NONE_VALUE
        result = redis_client.set(key, pickle.dumps(value))
        if expire_time is not None:
            Memcache.set_expiry(key, expire_time)
        return result

    @staticmethod
    @redis_none_handler
    def increment(key, increment_by=1):
        return redis_client.incr(key, increment_by)

    @staticmethod
    @redis_none_handler
    def decrement(key, decrement_by=1):
        return redis_client.decr(key, decrement_by)

    @staticmethod
    @redis_none_handler
    def delete(key):
        return redis_client.delete(key)

    @staticmethod
    @redis_none_handler
    def multidelete(keys):
        result = []
        for key in keys:
            result.append(Memcache.delete(key))
        return result

    @staticmethod
    @redis_none_handler
    def sample(patterns):
        keys = []
        for pattern in patterns:
            keys += list(redis_client.scan_iter(pattern))
        logging.warning(keys)

    @staticmethod
    @redis_none_handler
    def delete_by_wild_character(patterns):
        keys = []
        for pattern in patterns:
            keys += list(redis_client.scan_iter(pattern))
        return Memcache.multidelete(keys)

    @staticmethod
    @redis_none_handler
    def set_expiry(key, time):
        return redis_client.expire(key, time)

    @staticmethod
    @redis_none_handler
    def flush():
        return redis_client.flushall()
    
    @staticmethod
    @redis_none_handler
    def ttl(key):
        return redis_client.ttl(key)
