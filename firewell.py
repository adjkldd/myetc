#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# required software:
# 
#   * sslocal
#
# for installing sslocal command:
#
#   $ sudo apt install python-pip
#   $ sudo pip install shadowsocks
#
# Thanks to the free ss providers:
#
#  http://en.ss8.fun
#  http://global.ishadowsocks.net
#  http://en.ishadowx.net
#
#

import re
import requests
from bs4 import BeautifulSoup
import os
import sys
import time
import signal
import subprocess


SECRET_URL='http://en.ishadowx.net'


class Account:
  def __init__(self, host, port, password, method):
    self._host = host
    self._port = port
    self._password = password
    self._method = method

  def __str__(self):
    return "{:<12} {:<6} {:<10} {:<13}".format( \
           self._host, self._port, self._password, self._method)

  def host(self):
    return self._host

  def port(self):
    return self._port

  def password(self):
    return self._password

  def method(self):
    return self._method

  def makeParam(self):
    return "-s " + self._host + " -p " + self._port + \
           " -k " + self._password + " -m " + self._method 

class ShadowSocksAccounts:
  def __init__(self, url):
    self._url = url
    self._accounts = []
    self._soup = None
    self.update()

  def prettify(self):
    print(self._soup.prettify())

  def update(self):
    self._accounts = []
    page = requests.get(self._url)
    self._soup = BeautifulSoup(page.content, 'html.parser')
    self._parse()

  def _parse(self):
    for ht in self._soup.select('div.hover-text'):
      h4 = ht.select('h4')
      host_soup, port_soup, passwd_soup, method_soup = h4[0], h4[1], h4[2], h4[3]
      host = host_soup.select('span')[0].text.strip()
      port = port_soup.select('span')[0].text.strip()
      # port = re.search(r'[0-9]+', port_soup.text).group(0) # 冒号不是英文字符
      passwd = passwd_soup.select('span')[0].text.strip()
      method = method_soup.text.split(':')[1]
      
      if len(host) > 0 and len(port) > 0 and len(passwd) > 0 and len(method) > 0:
        self._accounts.append(Account(host, port, passwd, method)) 

  def accounts(self):
    return self._accounts


def test_speed(account):
  if not isinstance(account, Account):
    return

  pid = os.fork()

  if pid: # parent process
    time.sleep(0.8) # 800 ms

    command = 'curl --socks5-hostname 127.0.0.1:1080 -# -Lo /dev/null -w "time_total:%{time_total}" www.google.com'
    try:
      out = subprocess.check_output(command.split(' '))
      wanted = re.search(r'time_total:.*', out.decode().strip("\"")).group(0)
      time_cost = wanted.split(':')[1]
    except subprocess.CalledProcessError as e:
      os.kill(pid, signal.SIGTERM)
      os.wait()
      return 1000 # unavilable

    print("==> using server {}".format(account))
    try:
      os.wait()
    except KeyboardInterrupt as e:
      os.kill(pid, signal.SIGTERM)
      os.wait()
     
    return time_cost
  else: # child process
    os.execlp('sslocal', 'sslocal', "-qq", \
              '-s', account.host(), \
              '-p', account.port(), \
              '-k', account.password(), \
              '-m', account.method())
              # '>/dev/null', '2>&1')

def HasCommand(command):
  def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

  fpath, fname = os.path.split(command)
  if fpath:
    return is_exe(command)
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      path = path.strip('"')
      exe_file = os.path.join(path, command)
      if is_exe(exe_file):
        return True

  return False
      

if __name__ == '__main__':

  if not HasCommand('sslocal'):
    sys.stderr.write("you need install sslocal command first!\n");
    sys.stdout.write("\n\tsudo apt install python-pip\n")
    sys.stdout.write("\n\tsudo pip install shadowsocks\n")
    sys.exit(127)

  # accounts = ShadowSocksAccounts('https://go.ishadowx.net')
  accounts = ShadowSocksAccounts(SECRET_URL)

  while True:
    # prompt
    i = 0
    print("\n========== select your configuration ==========")
    print("{:<3} {:<12} {:<6} {:<10} {:<13}".format( \
          "", "server", "port", "password", "method"))
    for a in accounts.accounts():
      print("{:>2}) {}".format(i, a))
      i=i+1

    try:
      option = input(">>> ").strip()
    except EOFError as e:
      print('bye bye!')
      break
    if option == '':
      break

    # help command
    if option == "help" or option == "?":
      print("\n\thelp    - show help information\n" + \
              "\tupdate  - update the above configuration\n" + \
              "\t:number - select the above :number configuration")
      continue

    # update command
    if option == "update":
      accounts.update()
      continue

    try:
      option = int(option)
    except:
      print("number allowd only")
      continue

    cost = test_speed(accounts.accounts()[option])
    print("it costs {} s".format(cost))
  
