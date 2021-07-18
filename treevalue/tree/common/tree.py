from typing import Dict, Any, Union


def _to_tree_func(data):
    return Tree()


class Tree:
    def __init__(self, mapping: Dict[str, Union['Tree', Any]]):
        self.__dict = mapping

    def __check_key_exist(self, key):
        if key not in self.__dict.keys():
            raise KeyError("Key {key} not found.".format(key=repr(key)))

    def __getitem__(self, key):
        self.__check_key_exist(key)
        return self.__dict[key]

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        self.__check_key_exist(key)
        del self.__dict[key]
