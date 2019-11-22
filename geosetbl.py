#!/usr/bin/python
# -*- coding: utf-8 -*-.

import argparse
from geoip_libs.run import command
from geoip_libs.geoip_utils import utils
from geoip_libs.geoip_func import geoip


def CheckArgs():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', type=str, help='Add country ccTLD to blacklist')
    group.add_argument('-d', type=str, help='Delete country ccTLD from blacklist')
    group.add_argument('-da', action="store_true", help='Delete ALL countries ccTLD from blacklist')
    group.add_argument('-s', type=str, help='Search a ccTLD')
    group.add_argument('-l', action="store_true", help='List all available countries')
    group.add_argument('-lb', action="store_true", help='List blacklisted countries')
    group.add_argument('-li', action="store_true", help='List blacklisted countries networks')
    group.add_argument('-u', action="store_true", help='Update subnet list')
    group.add_argument('-b', action="store_true", help='Use this on boot')
    args = parser.parse_args()
    if args.a :
        command('/sbin/ipset create countries list:set').run()
        geoip().add_countries_subnet(args.a)
    if args.d:
        geoip().del_countries_subnet(args.d)
    if args.da:
        blocked_country = geoip().list_blocked(to_print=False)
        if len(blocked_country) > 0:
            for country in blocked_country:
                geoip().del_countries_subnet(country)
        else:
            print 'No blacklisted country.Nothing to remove!'
    if args.s:
        geoip().find_country(args.s)
    if args.l:
        setting = utils().settings['geoip_cctld_list']
        data = geoip().list_countries(setting)
        c1_size , c2_size = utils().find_max_lenght()
        utils().print_table('COUNTRY','ccTLD',c1_size ,c2_size)
        utils().print_headers()
        for country in sorted(data):
           utils().print_table(country.upper(),data[country],c1_size ,c2_size)
    if args.lb:
        c1_size , c2_size = utils().find_max_lenght()
        utils().print_table('COUNTRY','ccTLD',c1_size ,c2_size)
        utils().print_headers()
        geoip().list_blocked(True)
    if args.li:
        geoip().list_blacklist_ip()
    if args.u:
        geoip().update_subnets()
    if args.b:
        geoip().startup()


if __name__ == "__main__":
    if utils().am_i_root():
        CheckArgs()
        utils().clean_temp()
    else:
        print 'Only root can run this utils'
