import os
import redis
import pickle
from utils import globalconstants
import logging
import threading

redis_config = {
    "smartqprd-nz": {
        "REDISHOST": "10.242.77.155",
        "REDISPORT": 6379
    },
    "smartqprd-uk": {
        "REDISHOST": "10.96.159.115",
        "REDISPORT": 6379
    },
    "smartqdemo-uk": {
        "REDISHOST": "10.250.225.147",
        "REDISPORT": 6379
    },
    "smartqdemo-de": {
        "REDISHOST": "10.199.103.220",
        "REDISPORT": 6379
    },
    "sqpreprod-uk": {
        "REDISHOST": "10.58.119.243",
        "REDISPORT": 6379
    },
    "smartqdemo-nz": {
        "REDISHOST": "10.31.216.243",
        "REDISPORT": 6379
    },
    "smartqdemo": {
        "REDISHOST": "10.161.190.179",
        "REDISPORT": 6379
    },
    "smartqprd-india": {
        "REDISHOST": "10.47.22.171",
        "REDISPORT": 6379
    },
    "letsfeedtogether-prd": {
        "REDISHOST": "localhost1",
        "REDISPORT": 6379
    },
    "smartqprd-au": {
        "REDISHOST": "10.20.173.51",
        "REDISPORT": 6379
    },
    "sqpentest": {
        "REDISHOST": "10.63.44.115",
        "REDISPORT": 6379
    },
    "smartqprd-de": {
        "REDISHOST": "10.107.101.243",
        "REDISPORT": 6379
    },
    "smartqprd-us": {
        "REDISHOST": "10.79.180.139",
        "REDISPORT": 6379
    },
    "smartqprd-jp": {
        "REDISHOST": "10.138.240.131",
        "REDISPORT": 6379
    },
    "smartqprd-mex": {
        "REDISHOST": "10.245.0.11",
        "REDISPORT": 6379
    },
    "smartqprd-chi": {
        "REDISHOST": "10.160.170.99",
        "REDISPORT": 6379
    },
    "smartqprd-spain": {
        "REDISHOST": "10.2.249.227",
        "REDISPORT": 6379
    },
    "smartqprd-fi": {
        "REDISHOST": "10.165.53.99",
        "REDISPORT": 6379
    },
    "smartqdemo-au": {
        "REDISHOST": "localhost1",
        "REDISPORT": 6379
    },
    "smartqdemo-us": {
        "REDISHOST": "10.65.21.243",
        "REDISPORT": 6379
    },
    "smartqprd-uae": {
        "REDISHOST": "10.204.69.131",
        "REDISPORT": 6379
    },
    "smartqprd-ie": {
        "REDISHOST": "10.4.40.67",
        "REDISPORT": 6379
    },
    "smartqprd-sng": {
        "REDISHOST": "10.13.35.28",
        "REDISPORT": 6379
    },
    "smartqprd-hk": {
        "REDISHOST": "10.141.156.227",
        "REDISPORT": 6379
    },
    "smartqprd-nl": {
        "REDISHOST": "10.106.155.251",
        "REDISPORT": 6379
    },
    "smartquat-india": {
        "REDISHOST": "10.173.15.99",
        "REDISPORT": 6379
    },
    "smartqdemo-hk": {
        "REDISHOST": "10.60.145.3",
        "REDISPORT": 6379
    },
    "smartqprd-cn": {
        "REDISHOST": "10.6.0.11",
        "REDISPORT": 6379
    },
    "smartqprd-it": {
        "REDISHOST": "10.45.81.219",
        "REDISPORT": 6379
    },
    "smartqprd-be": {
        "REDISHOST": "10.239.44.75",
        "REDISPORT": 6379
    },
    "sqpreprod-us": {
        "REDISHOST": "10.80.127.203",
        "REDISPORT": 6379
    },
    "sqpreprod-india": {
        "REDISHOST": "10.77.135.227",
        "REDISPORT": 6379
    },
        "sqpreprod-spain": {
        "REDISHOST": "10.2.165.203",
        "REDISPORT": 6379
    },
    "sqpreprod-de": {
        "REDISHOST": "10.218.212.147",
        "REDISPORT":6379
    },
    "sqpreprod-au": {
        "REDISHOST": "10.194.25.75",
        "REDISPORT":6379
    },
    "sqpreprod-hk":{
        "REDISHOST": "10.68.230.227",
        "REDISPORT":6379
    },
    "sqpreprod-jp":{
        "REDISHOST": "10.163.147.67",
        "REDISPORT":6379
    },
    "sqpreprod-sng":{
        "REDISHOST": "10.228.130.3",
        "REDISPORT":6379
    },
    "sqpreprod-nz":{
        "REDISHOST": "10.86.191.219",
        "REDISPORT":6379
    },
    "smartqprd-se":{
        "REDISHOST": "10.36.50.123",
        "REDISPORT":6379
    },
    "sqpreprod-ie":{
        "REDISHOST": "10.30.34.171",
        "REDISPORT":6379
    },
    "smartqprd-ph":{
        "REDISHOST": "10.105.236.27",
        "REDISPORT":6379
    },
}

redis_host, redis_port, redis_client = None, None, None
if serverflavorconfig.serverflavour in redis_config:
    redis_host = redis_config[serverflavorconfig.serverflavour]["REDISHOST"]
    redis_port = redis_config[serverflavorconfig.serverflavour]["REDISPORT"]

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
