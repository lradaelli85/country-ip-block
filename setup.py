#!/usr/bin/python
# -*- coding: utf-8 -*-.

from json import load , dump
from sys import exit
from sys import path as syspath
from os import path , mkdir ,listdir , remove
import shutil


def load_json(json_file):
    try:
        with open(json_file, 'r') as json_f:
            data = load(json_f)
    except IOError as e:
        print e
        exit(1)
    return data


def run_setup():
    geoip_libs = '/geoip_libs'
    geoip_bin = 'geosetbl.py'
    geoip_settings_folder = load_json('settings.json')['settings']['geoip_settings_folder']
    py_lib = syspath[1]+geoip_libs
    if not path.isdir(geoip_settings_folder):
        try:
            mkdir(geoip_settings_folder)
        except OSError as e:
            print e
    else:
        for f in listdir(geoip_settings_folder):
            try:
                remove(path.join(geoip_settings_folder, f))
            except OSError as e:
                print e
    bl_json = {"bl_countries" : []}
    try:
        geoip_blacklist = load_json('settings.json')['settings']['geoip_blacklist']
        with open(geoip_blacklist, 'w+') as json_file:
            dump(bl_json, json_file)
    except IOError as e:
        print e
    try:
        shutil.copy2('countries.json', geoip_settings_folder)
        shutil.copy2('settings.json', geoip_settings_folder)
    except shutil.Error as e:
        print e
    except IOError as e:
        print e
    try:
        mkdir(py_lib)
        for f in listdir('libs/'):
            shutil.copy2('libs/'+f,py_lib)
    except shutil.Error as e:
        print e
        exit(1)
    except IOError as e:
        print e
        exit(1)
    except OSError as e:
        print e
        exit(1)
    try:
        shutil.copy2(geoip_bin,'/usr/local/bin')
    except shutil.Error as e:
        print e
        exit(1)
    except IOError as e:
        print e
        exit(1)
    print 'Done! All settings copied in {}'.format(geoip_settings_folder)
    print 'Python libraries copied in {}'.format(py_lib)
    print '{} copied in /usr/local/bin'.format(geoip_bin)

if __name__ == "__main__":
    run_setup()
