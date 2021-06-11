import re
import csv
import json
import numpy as np
import sys
    
    
def csv_to_json(filename, outfile_name, headers = None ,**patterns):
    '''
    Convert CSV file into jsonlines files
    
    Parameters
    ----------
    filename: file to convert
    outfile_name: name of the new file to be saved
    headers: list of keys. Use '.' to create nested dictionary object and [i] to indicate a list where i is the index.
    **patterns: used for validation. Can be done only to first level keys.
    
    Returns
    ----------
    create new txt file. each line is a json object
    

    '''
    with open(filename, 'r') as infile:
        data = csv.reader(infile)

        if not headers:
            headers = next(data)
            headers = parse_headers(headers)
        else:
            headers = parse_headers(headers)
            next(data)
            
        with open(outfile_name,'w') as outfile, open('error_lines.jsonlines','w') as error_file:
            row_counter, error_counter = 0, 0
            error_writer = csv.writer(error_file)
            for line in data:
                tx = write_line(headers, line)
                if validate(tx, **patterns):
                    outfile.write(json.dumps(tx) + '\n')
                    row_counter += 1
                else:
                    error_writer.writerow(line)
                    error_counter += 1
        outfile.close(), error_file.close()
        print('Successful rows: {}, failed: {}'.format(row_counter, error_counter))
    infile.close()


def write_line(parsed_headers, values):
    '''
    Create a nested dictionary
    
    Parameters
    ----------
    parsed_headers: list of lists as produced by 'parse_headers' function. Each of the lists in the bigger list will be turned into nested keys of dictionary
    values: values for the keys.
    
    Returns
    ----------
    dictionary object
    
    Example:
    >>> write_line([["key_1","key_2"],["new_key_1","new_key_2"]],["value_1","value_2"])
    
    {'key_1': {'key_2': 'value_1'}, 'new_key_1': {'new_key_2': 'value_2'}}
    '''
    assert len(parsed_headers) == len(values), 'Headers length does not match values length; {}, {}'.format(len(parsed_headers), len(values))
    assert contains(parsed_headers, list), 'Headers error'

    local_dict = {}
    for fieldname,value in zip(parsed_headers, values):
        update_dict(local_dict, fieldname ,value)
    return local_dict


def update_dict(d_, keys, field_value, add = True):
    '''
    Update a nested dictionary.
    
    Parameters
    ----------
    d_: dictionary object to be updated
    keys: list of keys. Each key will be placed inside the preceding key in the list.
    field_value: value to be given to the last key in the list
    add: True / False, if false, only if the path does exists, it new field_value will be placed.
    
    Example:
    
    >>> example_dictionary = {"firstKey":{"secondKey":"value"}}
    >>> update_dict(example_dictionary, ["firstKey", "secondKey"], "new_value")
    >>> example_dictionary
    
    {"firstKey":{"secondKey":"new_value"}}
    
    '''
    if keys[0] == 'drop' or not field_value or field_value in ['', ' ']:
        return
    elif keys[0] in d_ and len(keys) == 1:
        d_.pop(keys[0])
        d_[keys[0]] = field_value
    elif keys[0] not in d_ and len(keys) == 1 and add:
        d_[keys[0]] = field_value
    elif isinstance(keys[0], tuple):
        key, idx = keys[0][0], int(keys[0][1])
        update_list(d_, [key] + keys[1:], field_value, idx, add)
    elif keys[0] not in d_ and add:
        d_[keys[0]] = create_dict(keys[1:], field_value)
    elif keys[0] not in d_ and not add:
        return
    else:
        update_dict(d_[keys[0]], keys[1:], field_value, add)

        
def parse_headers(headers):
    '''
    Will parse headers into list of lists that can be later used with 'write_line' function.
    
    Parameters
    ----------
    headers: list of strings
    
    Returns
    ----------
    list of lists
    
    Example:
    >>> parse_headers(["key_1.key_1.2","key_2.items[0].key2.2","key_3"])
    
    [['key_1', 'key_1', '2'], ['key_2', ('items', 0), 'key2', '2'], ['key_3']]
    '''
    headers = [h.split('.') for h in headers]
    for fieldnames in headers:
        for i,name in enumerate(fieldnames):
            fieldnames[i] = islist(name)
    return headers


def create_dict(keys, field_value):
    '''
    Create a nested dictionary with field_value given
    
    Parameters
    ----------
    keys: list of of strings. Each item in list will create a new dictionary inside the previous one. Use tuple to create list as the key value
    field_value: value of the last item in keys. Can be anything (string, numerical, list or another dictionary)
    
    Returns
    ----------
    dictionary object
    
    Example:
    >>> create_dict(["first_key",("nest_list",0),"second_key"], "some value")
    
    {'first_key': {'nest_list': [{'second_key': 'some value'}]}}
    
    '''
    assert isinstance(keys, list), 'Keys for dictionary must be list'
    if not keys:
        return field_value
    if isinstance(keys[0], tuple):
        return {keys[0][0]:[create_dict(keys[1:], field_value)]}
    return {keys[0]:create_dict(keys[1:], field_value)}


def update_list(d_, keys, field_value, idx, add = True):
    if keys[0] not in d_ and add:
        d_[keys[0]] = [create_dict(keys[1:], field_value)]
    elif int(idx) < len(d_[keys[0]]):
        update_dict(d_[keys[0]][idx], keys[1:], field_value, add)
    else:
        d_[keys[0]].append(create_dict(keys[1:], field_value))

        
def islist(string):
    digits = re.findall('\[\d+\]', string)
    if not digits:
        return string

    clean_string = re.sub('\[\d+\]' ,'', string)
    digits = digits[0]
    digits = int(digits[1:-1])
    return clean_string, digits


def validate(tx, **patterns):
    if not patterns:
        return True
    for key, value in patterns.items():
        if re.match(value, str(tx.get(key))):
            return True
        return False

    
def contains(v, typ):
    return all(isinstance(x, typ) for x in v)


def clean_dict(d_, *values):
    '''
    Function recieves a dictionary object and removes any keys without values or keys with given *values parameters
    
    Parameters
    ----------
    d_: a dictionary object
    *values: keys with values given will be removed from the dictionary as well
    
    Returns
    ----------
    transformation is made on the object given
    '''
    if not isinstance(d_, dict):
        return None
    keys = list(d_.keys())
    for key in keys:
        if not d_.get(key) or d_.get(key) in values:
            d_.pop(key)
        elif isinstance(d_.get(key), dict):
            temp = clean_dict(d_[key], *values)
            if temp:
                d_[key] = temp
            else:
                d_.pop(key)
        elif isinstance(d_[key], list):
            n_list = [clean_dict(x, *values) for x in d_[key]]
            d_[key] = [k for k in n_list if k]
            if not d_[key]:
                d_.pop(key)
    return d_


def flatten_dict(dict_obj):
    '''
    Function receives a dictionary object and will normalize it into a flat dictionary (non nested dictionary)
    
    Parameters
    ----------
    dict_obj: a dictionary object
    
    '''
    temp_dict = {}
    for key, value in dict_obj.items():
        if isinstance(value, dict):
            temp_dict.update(flatten_dict(create_new_dict(value, key)))
        elif isinstance(value, list):
            for i in range(len(value)):
                temp_dict.update(flatten_dict(create_new_dict(value[i], key + "[{}]".format(i))))
        else:
            temp_dict[key] = value
    return temp_dict


def create_new_dict(dict_obj, prefix = None):
    prefix = prefix or ""
    return {prefix + "." + key:value for key, value in dict_obj.items()}


def apply_func(dict_obj, keys, func, **kwargs):
    '''
    apply a function on a value in a nested dictionary. Function will be applied on the dict_obj given.
    
    Paramters
    ---------
    dict_obj: a dictionary object to apply the function in
    keys: list of keys
    func: function to apply on the value of the last key in the keys list
    
    **kwargs: parameters that the func takes in
    '''
    if not keys:
        return
    elif isinstance(keys[0], tuple):
        key, idx = keys[0][0], keys[0][1]
        if idx == "i":
            for item in dict_obj[key]:
                apply_func(item, keys[1:], func, **kwargs)
        elif not isinstance(dict_obj[key], list) or idx > len(dict_obj[key])-1:
            return
        else:
            apply_func(dict_obj[key][idx], keys[1:], func, **kwargs)
    elif keys[0] not in dict_obj:
        return
    elif len(keys) == 1:
        dict_obj[keys[0]] = func(dict_obj.get(keys[0]), **kwargs)
    else:
        apply_func(dict_obj[keys[0]], keys[1:], func, **kwargs)
        
        
def swap_keys(dict_obj, mapping_dict, drop_keys = False):
    '''
    Modify dictionary keys based on mapping_dict given. dictionary must not be nested. Use flatten dict
    
    Parameters
    ----------
    dict_obj: dictionary object to map
    mapping_dict: dictionary of original keys, values of the keys will be the new keys.
    drop_keys: False if wanted to drop values that does not exist in mapping_dict. True if just keep those as they are
    '''
    keys = dict_obj.keys()
    values = dict_obj.values()
    if drop_keys:
        headers = [mapping_dict.get(key) if key in mapping_dict else "drop" for key in keys]
    else:
        headers = [mapping_dict.get(key) if key in mapping_dict else key for key in keys]
    parsed_headers = parse_headers(headers)
    return write_line(parsed_headers, values)