import json
import logging
import traceback
from copy import deepcopy
from google.cloud import datastore
from datetime import datetime
from utils.memcache import Memcache
from utils import globalconstants
# from utils.db_schemas import order_list, user_credentials, end_users,orders
from utils.exceptionlogging import ExceptionLogging

datastore_client = datastore.Client()
logging.info("Initializing data store client")


def measuredb_latency(function_to_decorate):
    def a_wrapper_accepting_arbitrary_arguments(*args, **kwargs):
        starttime = datetime.utcnow()
        result = function_to_decorate(*args, **kwargs)
        try:
            logging.info(f'time {((datetime.utcnow() - starttime).total_seconds() * 1000):.2f} ms for {args[0]} - {args[1]}')
        except:
            logging.info(f'time {((datetime.utcnow() - starttime).total_seconds() * 1000):.2f} ms for {args[0]} ')
        return result

    return a_wrapper_accepting_arbitrary_arguments


class EntityClass:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def dict_to_datastore(data, json_fields, other_fields={}):
    new_data = deepcopy(data)
    if new_data is None:
        return None

    for key in json_fields:
        if key in new_data and new_data[key] is not None:
            try:
                new_data[key] = json.dumps(new_data[key])
            except Exception as error:
                logging.info("json parse failed")

    # for key, value in other_fields.items():
    #     if key in new_data and new_data[key] is not None:
    #         try:
    #             new_data[key] = str(json.dumps(new_data[key]), "utf-8")
    #         except Exception as error:
    #             pass
    return new_data


def datastore_to_dict(data, json_fields, other_fields={}):
    if data is None:
        return None

    data = dict(data)
    for key in json_fields:
        if key in data and data[key] is not None:
            try:
                data[key] = json.loads(data[key])
            except Exception as error:
                pass
    return data


def transform_list(list, transformer, json_fields, other_fields={}):
    if list is None:
        return None

    new_list = []
    for item in list:
        new_list.append(transformer(item, json_fields, other_fields={}))
    return new_list


def transform_list_with_id(list, transformer, json_fields, other_fields={}):
    if list is None:
        return None

    new_list = []
    for item in list:
        new_list.append(transformer(item, json_fields, other_fields={}))
        new_list[-1]["id"] = item.key.id_or_name
    return new_list

def OR_filter(filters=[]):
    constructed_filter = None
    if filters:
        or_filters = []
        for filter_condition in filters:
            if not filter_condition:
                continue
            if isinstance(filter_condition, list):
                q_filter = datastore.query.PropertyFilter(*filter_condition)
                or_filters.append(q_filter)
            else:
                or_filters.append(filter_condition)
        constructed_filter = datastore.query.Or(or_filters)
    return constructed_filter

def AND_filter(filters=[]):
    constructed_filter = None
    if filters:
        and_filters = []
        for filter_condition in filters:
            if not filter_condition:
                continue
            if isinstance(filter_condition, list):
                q_filter = datastore.query.PropertyFilter(*filter_condition)
                and_filters.append(q_filter)
            else:
                and_filters.append(filter_condition)
        constructed_filter = datastore.query.And(and_filters)
    return constructed_filter

@measuredb_latency
def get_all(table_name, json_fields, other_fields={}, order=[], limit=None):
    query = datastore_client.query(kind=table_name)
    query.order = order
    if limit is None:
        data = list(query.fetch())
    else:
        data = list(query.fetch(limit=limit))
    new_data = []
    for datum in data:
        new_data.append(datastore_to_dict(datum, json_fields, other_fields))
    return new_data

@measuredb_latency
def get_all_with_key_hash(table_name, json_fields, other_fields={}, order=[], limit=None , key_hash = None):
    """
        make sure key_hash is a unique field in the table
    """

    query = datastore_client.query(kind=table_name)
    query.order = order
    if limit is None:
        data = list(query.fetch())
    else:
        data = list(query.fetch(limit=limit))

    get_hash_key = lambda datum : datum.get(key_hash,"") if key_hash else datum.key.name
    new_data = {get_hash_key(datum):datastore_to_dict(datum, json_fields, other_fields)  for datum in data}
    return new_data

@measuredb_latency
def get_all_with_cursor(table_name, json_fields, other_fields={}, order=[], limit=200, cursor = None):
    query = datastore_client.query(kind=table_name)
    query.order = order
    query_iter = query.fetch(start_cursor=cursor, limit=limit)
    page = next(query_iter.pages)
    data = list(page)
    next_cursor = query_iter.next_page_token
    new_data = []
    for datum in data:
        new_data.append(datastore_to_dict(datum, json_fields, other_fields))
    return new_data, next_cursor

@measuredb_latency
def get_all_with_id(table_name, json_fields, other_fields={}, order=[]):
    limit = 250 
    all_data = []
    
    while True:
        cursor = None
        query = datastore_client.query(kind=table_name)
        query.order = order
        query_iter = query.fetch(start_cursor=cursor, limit=limit)
        page = next(query_iter.pages)
        data = list(page)
    
        for item in data:
            all_data.append(datastore_to_dict(item, json_fields, other_fields={}))
            all_data[-1]["id"] = item.key.id_or_name

        next_cursor = query_iter.next_page_token
        cursor = next_cursor

        if cursor is None:
            break 

    return all_data

@measuredb_latency
def get_all_with_filter_and_cursor(table_name, json_fields,filters = [],other_fields={}, order=[], limit=200, cursor = None, composed_filter = None):
    query = datastore_client.query(kind=table_name)
    if composed_filter:
        query.add_filter(filter=composed_filter)
    else:
        for filter in filters:
            query.add_filter(filter[0], filter[1], filter[2])
    query.order = order
    query_iter = query.fetch(start_cursor=cursor, limit=limit)
    page = next(query_iter.pages)
    data = list(page)
    next_cursor = query_iter.next_page_token
    new_data = []
    for datum in data:
        new_data.append(datastore_to_dict(datum, json_fields, other_fields))
    return new_data, next_cursor


@measuredb_latency
def get_all_raw(table_name):
    query = datastore_client.query(kind=table_name)
    return list(query.fetch())


@measuredb_latency
def get_memcached(table_name, key_name, json_fields):
    datum = Memcache.get(f"db_{table_name}_{key_name}")
    if datum == globalconstants.SPECIAL_NONE_VALUE:
        return None
    if datum is None:
        key = datastore_client.key(table_name, key_name)
        datum = datastore_client.get(key)
        Memcache.set(f"db_{table_name}_{key_name}", datum)
    return datastore_to_dict(datum, json_fields)


@measuredb_latency
def get(table_name, key_name, json_fields):
    key = datastore_client.key(table_name, key_name)
    datum = datastore_client.get(key)
    return datastore_to_dict(datum, json_fields)


@measuredb_latency
def get_raw(table_name, key_name):
    key = datastore_client.key(table_name, key_name)
    return datastore_client.get(key)


@measuredb_latency
def get_multi_by_table_raw(table_names, key_names):
    keys = []
    length = len(table_names)
    for i in range(length):
        keys.append(datastore_client.key(table_names[i], key_names[i]))
    data = datastore_client.get_multi(keys)
    new_data = [None] * length
    for i in range(len(data)):
        if data[i] is None:
            continue
        index = table_names.index(data[i].kind)
        new_data[index] = data[i]
    return new_data


@measuredb_latency
def get_multi_by_key_raw(table_name, key_names, filter_none=True):
    keys = []
    for key_name in key_names:
        keys.append(datastore_client.key(table_name, key_name))
    data = datastore_client.get_multi(keys)
    new_data = [None] * len(key_names)
    for i in range(len(data)):
        if data[i] is None:
            continue
        index = key_names.index(data[i].key.id_or_name)
        new_data[index] = data[i]

    if filter_none:
        new_data = list(filter(None, new_data))

    return new_data


# @measuredb_latency
# def get_multi_by_key(table_name, key_names, json_fields, filter_none=True):
#     keys = []
#     for key_name in key_names:
#         keys.append(datastore_client.key(table_name, key_name))
#     data = datastore_client.get_multi(keys)
#     new_data = [None] * len(key_names)
#     for i in range(len(data)):
#         if data[i] is None:
#             continue
#         index = key_names.index(data[i].key.id_or_name)
#         new_data[index] = data[i]
#
#     if filter_none:
#         new_data = list(filter(None, new_data))
#
#     new_data = transform_list(new_data, datastore_to_dict, json_fields)
#
#     return new_data

@measuredb_latency
def get_multi_by_key(table_name, key_names, json_fields, filter_none=True, chunk_size=1000):
    new_data = []
    for i in range(0, len(key_names), chunk_size):
        chunk_keys = key_names[i:i + chunk_size]
        keys = [datastore_client.key(table_name, key_name) for key_name in chunk_keys]
        data = datastore_client.get_multi(keys)

        chunk_data = [None] * len(chunk_keys)
        for j in range(len(data)):
            if data[j] is None:
                continue
            index = chunk_keys.index(data[j].key.id_or_name)
            chunk_data[index] = data[j]

        if filter_none:
            chunk_data = list(filter(None, chunk_data))

        chunk_data = transform_list(chunk_data, datastore_to_dict, json_fields)
        new_data.extend(chunk_data)

    return new_data

@measuredb_latency
def get_multi_by_key_with_key_hash(table_name, key_names, json_fields,other_fields={}, filter_none=True, key_hash = None):
    keys = []
    for key_name in key_names:
        keys.append(datastore_client.key(table_name, key_name))
    data = datastore_client.get_multi(keys)
    new_data = [None] * len(key_names)
    for i in range(len(data)):
        if data[i] is None:
            continue
        index = key_names.index(data[i].key.id_or_name)
        new_data[index] = data[i]

    if filter_none:
        new_data = list(filter(None, new_data))

    new_data = transform_list(new_data, datastore_to_dict, json_fields)
    get_hash_key = lambda datum : datum.get(key_hash,"") if key_hash else datum.key.name
    new_data = {get_hash_key(datum):datastore_to_dict(datum, json_fields, other_fields)  for datum in data}

    return new_data

@measuredb_latency
def get_multi_by_key_with_id(table_name, key_names, json_fields, filter_none=True):
    keys = []
    for key_name in key_names:
        keys.append(datastore_client.key(table_name, key_name))
    data = datastore_client.get_multi(keys)
    new_data = [None] * len(key_names)
    for i in range(len(data)):
        if data[i] is None:
            continue
        index = key_names.index(data[i].key.id_or_name)
        new_data[index] = data[i]

    if filter_none:
        new_data = list(filter(None, new_data))

    new_data = transform_list_with_id(new_data, datastore_to_dict, json_fields)

    return new_data


@measuredb_latency
def get_by_filter(table_name, filters, json_fields, other_fields={}, order=[], get_id=False, limit=None, composed_filter=None):
    query = datastore_client.query(kind=table_name)
    if composed_filter:
        query.add_filter(filter=composed_filter)
    else:
        for filter in filters:
            query.add_filter(filter[0], filter[1], filter[2])
    query.order = order
    results = list(query.fetch(limit=limit))
    return transform_list(results, datastore_to_dict, json_fields, other_fields)


@measuredb_latency
def get_with_id_by_filter(table_name, filters, json_fields, other_fields={}, order=[]):
    query = datastore_client.query(kind=table_name)
    for filter in filters:
        query.add_filter(filter[0], filter[1], filter[2])
    query.order = order
    results = list(query.fetch())
    return transform_list_with_id(results, datastore_to_dict, json_fields, other_fields)


@measuredb_latency
def get_by_filter_raw(table_name, filters, order=[], composed_filter=None):
    query = datastore_client.query(kind=table_name)
    if composed_filter:
        query.add_filter(filter=composed_filter)
    else:
        for filter in filters:
            query.add_filter(filter[0], filter[1], filter[2])
    query.order = order
    results = list(query.fetch())
    return results


@measuredb_latency
def create_memcached(table_name, key_name, obj, exclusions, json_fields):
    if key_name is None:
        db_key = datastore_client.key(table_name)
    else:
        db_key = datastore_client.key(table_name, key_name)
    db_obj = datastore.Entity(
        key=db_key,
        exclude_from_indexes=exclusions
    )
    db_obj.update(dict_to_datastore(obj, json_fields))
    datastore_client.put(db_obj)
    if key_name is not None:
        Memcache.set(f"db_{table_name}_{key_name}", db_obj)
    return db_obj


@measuredb_latency
def create(table_name, key_name, obj, exclusions, json_fields, other_fields={}, by_transaction=False):
    if table_name in [order_list.table_name, user_credentials.table_name, end_users.table_name,orders.table_name]:
        obj["modified_timestamp"] = datetime.utcnow()
    if key_name is None:
        db_key = datastore_client.key(table_name)
    else:
        db_key = datastore_client.key(table_name, key_name)
    db_obj = datastore.Entity(
        key=db_key,
        exclude_from_indexes=exclusions
    )
    db_obj.update(dict_to_datastore(obj, json_fields, other_fields))
    if by_transaction:
        datastore_transaction = datastore_client.transaction()
        with datastore_transaction:
            datastore_transaction.put(db_obj)
    else:
        datastore_client.put(db_obj)
    return db_obj


@measuredb_latency
def multi_save(table_name, key_name, objects_list, exclusions, json_fields, other_fields={}, by_transaction=False):
    new_objects_list = []
    for obj in objects_list:
        if table_name in [order_list.table_name, user_credentials.table_name, end_users.table_name,orders.table_name]:
            obj["modified_timestamp"] = datetime.utcnow()
        db_key = None
        if key_name:
            db_key = datastore_client.key(table_name, obj[key_name])
        else:
            db_key = datastore_client.key(table_name)
            
        db_obj = datastore.Entity(
            key=db_key,
            exclude_from_indexes=exclusions
        )
        db_obj.update(dict_to_datastore(obj, json_fields, other_fields))
        new_objects_list.append(db_obj)
    if by_transaction:
        datastore_transaction = datastore_client.transaction()
        with datastore_transaction:
            datastore_client.put_multi(new_objects_list)
    else:
        datastore_client.put_multi(new_objects_list)


@measuredb_latency
def multi_update_pasedvalue(table_name, key_name, objects_list, exclusions, json_fields, other_fields={}):
    new_objects_list = []
    keys= []

    for obj in objects_list:
        keys.append(obj[key_name])

        db_key = datastore_client.key(table_name, obj[key_name])
        # Fetch the raw row value


    for table_row in get_multi_by_key_raw(table_name, keys, keys):
        table_row.update(dict_to_datastore(obj, json_fields, other_fields))
        new_objects_list.append(table_row)

    datastore_client.put_multi(new_objects_list)


@measuredb_latency
def multi_save_raw(objects_list):
    for obj in objects_list:
        if obj.kind in [order_list.table_name, user_credentials.table_name, end_users.table_name,orders.table_name]:
            obj.update({"modified_timestamp": datetime.utcnow()})
    datastore_client.put_multi(objects_list)


@measuredb_latency
def save_raw(obj):
    if obj.kind in [order_list.table_name, user_credentials.table_name, end_users.table_name,orders.table_name]:
        obj.update({"modified_timestamp": datetime.utcnow()})
    datastore_client.put(obj)


@measuredb_latency
def delete(table_name, key_name):
    key = datastore_client.key(table_name, key_name)
    return datastore_client.delete(key)


@measuredb_latency
def multi_delete(table_name, key_names):
    keys = []
    for key_name in key_names:
        keys.append(datastore_client.key(table_name, key_name))
    return datastore_client.delete_multi(keys)


@measuredb_latency
def multi_delete_any(table_names, key_names):
    keys = []
    for index in range(len(table_names)):
        keys.append(datastore_client.key(table_names[index], key_names[index]))
    return datastore_client.delete_multi(keys)


@measuredb_latency
def multi_delete_raw(keys):
    return datastore_client.delete_multi(keys)


def get_all_keys(table_name):
    query = datastore_client.query(kind=table_name)
    query.keys_only()
    return list(query.fetch())


@measuredb_latency
def delete_memcached(table_name, key_name):
    key = datastore_client.key(table_name, key_name)
    Memcache.delete(f"db_{table_name}_{key_name}")
    return datastore_client.delete(key)


def sanitize_key():
    pass


@measuredb_latency
def get_by_filter_iter(table_name, filters, order=[], composed_filter=None):
    query = datastore_client.query(kind=table_name)
    if composed_filter:
        query.add_filter(filter=composed_filter)
    else:
        for filter in filters:
            query.add_filter(filter[0], filter[1], filter[2])
    query.order = order
    results = query.fetch()
    return results


@measuredb_latency
def get_by_filter_only_key(table_name, filters, composed_filter=None):
    query = datastore_client.query(kind=table_name)
    if composed_filter:
        query.add_filter(filter=composed_filter)
    else:
        for filter in filters:
            query.add_filter(filter[0], filter[1], filter[2])
    query.keys_only()
    results = list(query.fetch())
    return results


@measuredb_latency
def get_count_with_filters(table_name,filters=[], composed_filter=None):
    query = datastore_client.query(kind=table_name)
    if composed_filter:
        query.add_filter(filter=composed_filter)
    else:
        for filter in filters:
            query.add_filter(filter[0], filter[1], filter[2])
    query.keys_only()
    return len(list(query.fetch()))


@measuredb_latency
def get_paginated_rows(table_name,filters=[],rowcount=None,cursor=None,composed_filter=None, projection=None):
    query = datastore_client.query(kind=table_name)
    if composed_filter:
        query.add_filter(filter=composed_filter)
    else:
        for filter in filters:
            query.add_filter(filter[0], filter[1], filter[2])

    if projection:
        query.projection = projection
    query_iter = query.fetch(start_cursor=cursor, limit=rowcount)
    page = next(query_iter.pages)
    tasks = list(page)
    next_cursor = query_iter.next_page_token
    return tasks, next_cursor


@measuredb_latency
def get_count(table_name):
    query = datastore_client.query(kind=table_name)
    count = query.count()
    return count


@measuredb_latency
def deletepreviousfooditem(restaurantid):
    query = datastore_client.query(kind="FoodItem")
    query.add_filter("resturantid", "=", restaurantid)
    allkeys = list([entity.key for entity in query.fetch()])
    if len(allkeys)>0:
        all_batch = create_batches(allkeys)
        for allkeys_batch in all_batch:
            datastore_client.delete_multi(allkeys_batch)
    return allkeys

@measuredb_latency
def create_batches(batch_list):
    all_batches = []
    start = 0
    end = 0
    total_items = len(batch_list)
    if batch_list:
        while end < total_items:
            end += 400
            if end > total_items:
                end = total_items
            all_batches.append(batch_list[start:end])
            start = end
    return all_batches


@measuredb_latency
def multi_batch_save(data_obj, table_name, key_name, exclude_from_indexes, json_fields, by_transaction=False):
    try:
        previous = 0
        for x in range(400, len(data_obj), 400):
            multi_save(table_name, key_name, data_obj[previous: x],
                                                exclude_from_indexes,
                                                json_fields, by_transaction=by_transaction)
            previous = x
        multi_save(table_name, key_name, data_obj[previous:],
                                           exclude_from_indexes,
                                           json_fields, by_transaction=by_transaction)
    except Exception as error:
        logging.error(error)

@measuredb_latency
# fetch log details between two dates based on type of log and user id or location
def get_log(userid, typeoflog, start_date, end_date, location=None):
    logs = []
    st_date = start_date
    en_date = end_date
    if not isinstance(start_date, datetime):
        st_date = datetime.utcnow().strptime(str(start_date), '%Y-%m-%d %H:%M:%S')

    if not isinstance(end_date, datetime):
        en_date = datetime.utcnow().strptime(str(end_date), '%Y-%m-%d %H:%M:%S')

    q = datastore_client.query(kind="Logtable")
    q.add_filter('timestamp', '>=', st_date)
    q.add_filter('timestamp', '<=', en_date)

    if userid is not None:
        q.add_filter('userid', '=', userid)
    if typeoflog is not None:
        q.add_filter('typeoflog', '=', typeoflog)
    if location is not None:
        q.add_filter('location', '=', location)

    records = q.fetch()
    for record in records:
        try:
            logs.append(dict(
                userid=record.get("userid"),
                extras=record.get("extras"),
                timestamp=datetime.strftime(record.get("timestamp"), "%Y-%m-%d %H:%M:%S"),
                typeoflog=record.get("typeoflog"),
                location=record.get("location")
            ))
        except Exception as ex:
            logging.info(record)
            ExceptionLogging.LogException(traceback.format_exc(), str(ex))

    return logs

@measuredb_latency
def query_entities_by_batch(batch_size, kind, filters=None, start_cursor=None):
    query = datastore_client.query(kind=kind)

    if filters is not None:
        for fltr in filters:
            query.add_filter(fltr[0], fltr[1], fltr[2])

    query_iter = query.fetch(start_cursor=start_cursor, limit=batch_size)

    entities = list(query_iter)
    next_cursor = query_iter.next_page_token if query_iter.next_page_token else None

    yield entities, next_cursor

