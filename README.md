# Block countries with iptables and ipset

This python script will help you in blocking incoming/outgoing connections from/to
specific countries without GEOIP iptables module.
It downloads the subnet list from ipdeny.com


# Requirements

- iptables
- ipset
- python2.7
- python-bs4


# Introduction

This script will manage to create sets (#NO IPTABLES RULES ARE ADDED) that you will use
to block access from/to specific countries.
It does not use iptables GEOIP module.

# How it works

A set of type "list" called "countries",is created and all blacklisted countries
are added to it.This will let you create a single iptables rule to drop all
blacklisted countries.
All settings are placed under /opt/geoip folder
All python libraries are placed in the python path
Binary is placed in /usr/local/bin folder
The above settings could be changed,see `settings.json` file

### show the help
```
luca@debian:~$ sudo geosetbl.py -h
usage: geosetbl.py [-h] [-a A | -d D | -da | -s S | -l | -lb | -li | -u | -b]

optional arguments:
  -h, --help  show this help message and exit
  -a A        Add country ccTLD to blacklist
  -d D        Delete country ccTLD from blacklist
  -da         Delete ALL countries ccTLD from blacklist
  -s S        Search a ccTLD
  -l          List all available countries
  -lb         List blacklisted countries
  -li         List blacklisted countries IP networks
  -u          Update subnet list
  -b          Use this on boot
```

### Inizialize everything
```
luca@debian:~$ sudo python setup.py
Done! All settings copied in /opt/geoip/
Python libraries copied in /usr/lib/python2.7/geoip_libs
geosetbl.py copied in /usr/local/bin
```

### update blacklist on a daily basis

```
sudo touch /etc/cron.d/update_subnets
```
edit this file and add
```
00 22 * * * root /usr/local/bin/geosetbl.py -u
```
save the file and restart cron service
```
sudo systemctl restart cron
```

### search a ccTLD
```
luca@debian:~$ sudo geosetbl.py -s au
COUNTRY                                                ccTLD
----------------------------------------------------------------
AUSTRALIA                                              au
AUSTRIA                                                at
```

### blacklist a country
```
luca@debian:~$ sudo geosetbl.py -a it
```

### list blacklisted countries
```
luca@debian:~$ sudo geosetbl.py -lb
COUNTRY                                                ccTLD
----------------------------------------------------------------
ITALY                                                  it
```

you can check the sets with
```
luca@debian:~$ sudo geosetbl.py -li
Name: it_set
Type: hash:net
Revision: 6
Header: family inet hashsize 1024 maxelem 65536
Size in memory: 2264
References: 1
Number of entries: 31
Members:
1.2.3.0/24
```

### remove a country from blacklist
```
luca@debian:~$ sudo geosetbl.py -d it
```

### block incoming connections from blacklisted countries
```
sudo iptables -I INPUT -m set --match-set countries src -m limit --limit 10/min -j NFLOG --nflog-prefix  "[COUNTRIES-IN BLOCK] :"
sudo iptables -I INPUT 2 -m set --match-set countries src -j DROP
```

### block outgoing connections from blacklisted countries
```
sudo iptables -I OUTPUT -m set --match-set countries dst -m limit --limit 10/min -j NFLOG --nflog-prefix  "[COUNTRIES-OUT BLOCK] :"
sudo iptables -I OUTPUT 2 -m set --match-set countries dst -j DROP
```

### block connections to/from blacklisted countries (if this is a gateway)
```
sudo iptables -I FORWARD -m set --match-set countries dst -m limit --limit 10/min -j NFLOG --nflog-prefix  "[COUNTRIES-OUT BLOCK] :"
sudo iptables -I FORWARD 2 -m set --match-set countries dst -j DROP
sudo iptables -I FORWARD 3 -m set --match-set countries src -m limit --limit 10/min -j NFLOG --nflog-prefix  "[COUNTRIES-IN BLOCK] :"
sudo iptables -I FORWARD 4 -m set --match-set countries src -j DROP
```

### Apply configuration on boot
You need to run `block-geoip.py -b` as root.
You can place that command in rc.local or you may create a systemd unit that runs on boot
Create the unit file
```
sudo vim /etc/systemd/system/geosetbl.service
```
and add
```
[Unit]
Description=Restore Countries set


[Service]
Type=idle
ExecStart=/usr/local/bin/geosetbl.py -b
User=root

[Install]
WantedBy=multi-user.target
```
create the link and reload systemd

```
sudo ln -sf /etc/systemd/system/geosetbl.service /etc/systemd/system/multi-user.target.wants/geosetbl.service

sudo systemctl daemon-reload
```
