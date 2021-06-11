# dict_modifier
Functions to modify dictionaries easily


## CSV to JSON Converter


Starting with the most "atomic" function, The `create_dict(keys, field_value)` function recieves two arguments. The first one `key` is a list, each item of this list will be the dictionary key inside the previous key, the value is what will be placed as the last key value. For example if I want one level dictionary:

``
>>> create_dict(['OneLevel'], 'A')

{'OneLevel': 'A'}
``

and 

``
>>> create_dict(['OneLevel', 'TwoLevels'], 'A')

{'OneLevel': {'TwoLevels': 'A'}}
``

The next level is the `update_dict(d_, keys, field_value, add = True)` function that takes in a dictionary, list of keys and a value, all three first arguments are mandatory. The function will update the dictionary that was given according to the keys. If add is true, it will add the value to dictionary even if path does not exists.
If, for example I have the following dictionary `my_dict = {'LevelOne':{'LevelTwo':'A'}}` and I want to add the `{'LevelTwo_2':'B'}` inside `LevelOne` key I can use the function as follows:

``
update_dict(my_dict, ['LevelOne','LevelTwo_2'], 'B')
``

my new updated dictionary will be `{'LevelOne':{'LevelTwo':'A','LevelTwo_2':'B'}}`

next there is the `write_line(headers, values)` function. It takes in two lists. Headers and values. In order to create a nested dict use comma between each key, ie. `LevelOne.LevelTwo` will be come a two nested dictionaries, `LevelTwo` inside `LevelOne`. Can also use squrare brackets `[i]` for creating a list where `i` is the index. Values can be anything (lists, dict, string). Length of headers and values must be the same. 

Example:

``
>>> write_line(['LevelOne[0].LevelThree','SecondKey.SecondKeyTwo', 'LevelOne[1].LevelTwo'], ['A','B','C'])

{'LevelOne': [{'LevelThree': 'A'}, {'LevelTwo': 'C'}],
 'SecondKey': {'SecondKeyTwo': 'B'}}
``

## Additional helpful functions:

`clean_dict` takes in a dictionary and values. It will remove any keys with None values or any other values given.

`flatten_dict` will normalize a dictionary. will return a non nested dictionary.
Example:

`>>> dict_obj = {
   'orderNo': '00000001',
   'totals': [{'merchandizeTotal': {'tax': '0.00',
      'netPrice': '90.00',
      'grossPrice': '90.00'}},
    {'adjustedMerchandizeTotal': {'tax': '0.00',
      'netPrice': '90.00',
      'grossPrice': '90.00'}},
    {'shippingTotal': {'tax': '0.00', 'netPrice': '6.00', 'grossPrice': '6.00'}},
    {'adjustedShippingTotal': {'tax': '0.00',
      'netPrice': '0.00',
      'grossPrice': '0.00'}},
    {'orderTotal': {'tax': '0.00', 'netPrice': '90.00', 'grossPrice': '90.00'}}]
  }
  
  >>> flatten_dict(dict_obj)
 {
   'orderNo': '00000001',
   'totals[0].merchandizeTotal.tax': '0.00',
   'totals[0].merchandizeTotal.netPrice': '90.00',
   'totals[0].merchandizeTotal.grossPrice': '90.00',
   'totals[1].adjustedMerchandizeTotal.tax': '0.00',
   'totals[1].adjustedMerchandizeTotal.netPrice': '90.00',
   'totals[1].adjustedMerchandizeTotal.grossPrice': '90.00',
   'totals[2].shippingTotal.tax': '0.00',
   'totals[2].shippingTotal.netPrice': '6.00',
   'totals[2].shippingTotal.grossPrice': '6.00',
   'totals[3].adjustedShippingTotal.tax': '0.00',
   'totals[3].adjustedShippingTotal.netPrice': '0.00',
   'totals[3].adjustedShippingTotal.grossPrice': '0.00',
   'totals[4].orderTotal.tax': '0.00',
   'totals[4].orderTotal.netPrice': '90.00',
   'totals[4].orderTotal.grossPrice': '90.00'
  }
  `


`apply_func` will apply a function given on the value of some key in a nested dictionary.
