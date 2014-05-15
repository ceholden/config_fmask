# -*- coding: utf-8 -*-

def mtl2dict(filename, to_float=True):
    """ Reads in filename and returns a dict with MTL metadata """

    mtl = {}

    # Open filename with context manager
    with open(filename, 'rb') as f:
        # Read all lines in file
        for line in f.readlines():
            # Split KEY = VALUE entries
            key_value = line.strip().split(' = ')

            # Ignore END lines
            if len(key_value) != 2:
                continue

            key = key_value[0].strip()
            value = key_value[1].strip('"')

            # Try to convert to float
            if to_float is True:
                try:
                    value = float(value)
                except:
                    pass

            # Trim and add to dict
            mtl[key] = value

    return mtl
