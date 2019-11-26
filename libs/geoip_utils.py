#!/usr/bin/python
# -*- coding: utf-8 -*-.

from os import getuid , listdir , remove , path
from re import search
from json import load , dump
from sys import exit
from run import command
from urllib2 import urlopen, URLError, HTTPError
#from bs4 import BeautifulSoup

class utils:
        def __init__(self):
            self.settings_file = '/opt/geoip/settings.json'
            self.settings = {}
            try:
                self.settings = self.load_json(self.settings_file)['settings']
            except IOError as e:
                print e

        def print_table(self,value1,value2,column1_size,column2_size):
            print '{0:<{h1}s}{1:<{h2}s}'.format(value1,value2,h1=column1_size+3,h2=column2_size)


        def ipset_bin(self):
            return command('which ipset').print_output()


        def print_headers(self):
            column1_size , column2_size = self.find_max_lenght()
            listof = []
            for i in range(int(column1_size)+int(column2_size)+6):
                listof.append('-')
            print ''.join(listof)


        def find_max_lenght(self):
            countries = self.load_json(self.settings['geoip_cctld_list'])
            return max(len(k) for k in countries['countries'].keys()) , max(len(k) for k in countries['countries'].values())


        def am_i_root(self):
            if getuid() != 0:
                return False
            else:
                return True


        def clean_temp(self):
            for f in listdir('/tmp/'):
                if search('[a-z]-aggregated.zone$', f):
                    try:
                        remove(path.join('/tmp/', f))
                    except OSError as e:
                        print e


        def load_json(self,json_file):
            try:
                with open(json_file, 'r') as json_f:
                    data = load(json_f)
            except IOError as e:
                print e
                exit(1)
            return data


        def get_settings(self,setting):
            data = self.load_json(self.settings_file)
            return data['settings'][setting]


        def download_file(self,country_file):
            zone_file = country_file+'-aggregated.zone'
            url = self.settings['geoip_update_url']
            url = url+zone_file
            try:
                f = urlopen(url,timeout = 15)
                with open('/tmp/'+path.basename(url) , 'wb') as country_file:
                    country_file.write(f.read())
            except HTTPError, e:
                print 'HTTP Error:', e.code, url
                exit(1)
            except URLError, e:
                print 'URL Error:', e.reason, url
                exit(1)


        def strip_str(self,s,first,last):
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]


        def generate_cctld_list(self):
            try:
                url = urlopen(self.settings['geoip_cctld_url']).read()
            except HTTPError, e:
                print 'HTTP Error:', e.code, url
                exit(1)
            except URLError, e:
                print 'URL Error:', e.reason, url
                exit(1)
            soup = BeautifulSoup(url,features="lxml")
            cctld_table = soup.findAll('table', attrs={'border' : '1'})
            cctld_dict = {}
            cctld_dict['countries'] = {}
            for line in cctld_table:
                for parag in line.text.splitlines():
                    cctld_dict['countries'][parag.split('(')[0].lower()] = self.strip_str(parag,'(',')').lower()
            try:
                with open(self.settings['geoip_cctld_list'], 'w+') as json_file:
                    dump(cctld_dict, json_file)
            except IOError as e:
                print e


        def get_country_tmp_file(self,country):
            country = country.lower()
            countries = self.settings['geoip_cctld_list']
            data = self.load_json(countries)['countries']
            if country in data.values():
                self.download_file(country)
                self.add_json_country(country)
                country_net_tmp = '/tmp/{}-aggregated.zone'.format(country)
            else:
                print 'Country not found'
                country_net_tmp = 'NotFound'
            return country_net_tmp


        def add_json_country(self,country):
            bl_countries = self.load_json(self.settings['geoip_blacklist'])
            if country not in bl_countries['bl_countries']:
                bl_countries['bl_countries'].append(country)
                try:
                    with open(self.settings['geoip_blacklist'], 'w') as json_file:
                        dump(bl_countries, json_file)
                except IOError as e:
                    print e
            else:
                print 'Country already blacklisted'
                exit(1)


        def set_ipset_country(self,country_file,country):
            if country_file != 'NotFound':
                geoip_settings_folder = self.settings['geoip_settings_folder']
                with open(country_file,'r') as config_file:
                    set_file = geoip_settings_folder+path.basename(country_file)+'.set'
                    with open(set_file, 'w') as ipset_file:
                        ipset_file.write('-! create {}_set hash:net family inet\n'.format(country))
                        for line in config_file.readlines():
                            ipset_file.write('add {}_set {}'.format(country,line))
                        ipset_file.write('add countries {}_set'.format(country))
                command('{} restore -f {}'.format(self.ipset_bin(),set_file)).run()


        def del_json_country(self,country):
            bl_countries = self.load_json(self.settings['geoip_blacklist'])
            if country in bl_countries['bl_countries']:
                bl_countries['bl_countries'].remove(country)
                try:
                    with open(self.settings['geoip_blacklist'], 'w') as json_file:
                        dump(bl_countries, json_file)
                except IOError as e:
                    print e
            else:
                print 'Country not blacklisted'
                exit(1)
