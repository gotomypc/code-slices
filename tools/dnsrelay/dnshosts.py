#!/usr/bin/env python
#
# Copyright 2010 pen9u1n
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from dns import DNS
from dns import Host
from dns import CANT_RESOLVE
from dnscache import DNSCacheManager
from StringIO import StringIO

import httplib 
import logging

class DNSHosts(DNS):
    def __init__(self):
        self.server = "8.8.8.8"
        self.cm = DNSCacheManager()

    def do_hosts_lookup(self, domain):
        hosts = db.GqlQuery("SELECT * FROM Host WHERE domain = :1 LIMIT 1", domain)
        
        for host in hosts:
            if host.ip:
                return host.ip

        return CANT_RESOLVE

    def lookup(self, domain):
        address = CANT_RESOLVE
        if (len(domain) > 0):
            address = self.do_hosts_lookup(domain)

        self.cm.update(domain, address, address != CANT_RESOLVE)
        
        return address

class DNSHostsManager(object):
    def get_all(self):
        hosts = []
        return hosts

    def add_host(self, ip, domain):
        if (len(ip) == 0 or len(domain) == 0):
            return

        updated = False
        hosts = db.GqlQuery("SELECT * FROM Host WHERE domain = :1 LIMIT 1", domain)
        for host in hosts:
            host.ip = ip
            try:
                db.put(host)
                updated = True
            except CapabilityDisabledError:
                return

        if (not updated):
            host = Host(ip = ip, domain = domain)
            try:
                host.put()
            except CapabilityDisabledError:
                pass

        return

    def del_host(self, domain):
        if (len(domain) == 0):
            return

        hosts = db.GqlQuery("SELECT * FROM Host WHERE domain = :1 LIMIT 1", domain)
        for host in hosts:
            host.delete()

    def del_all(self):
        hosts = Host.all()
        for host in hosts:
            host.delete()

    def _parse_hosts(self, data):
        hosts = []
        f = StringIO(data)

        for line in f:
            line = line.strip(" \n")

            if (len(line) == 0):
                #print "empty line %s" % line
                continue

            c = line[0]
            if (c == '{' or c == '#' or c == '}'):
                #print "comment line %s" % line
                continue

            strs = line.split()
            if (len(strs) < 2):
                #print "incomplete line %s" % line
                continue

            #print "Hosts line %s" % line
            ip = strs[0]

            # Ignore localhost
            if (ip == "127.0.0.1"):
                continue

            doms = strs[1:]
            for dom in doms:
                host = Host(ip = ip, domain = dom)
                hosts.append(host)

        f.close()

        return hosts

    def load_hosts(self, host, target):
        data = ""

        try:
            logging.debug("Query: %s%s" % (host, target))

            httpconn = httplib.HTTPConnection(host, 80)
            httpconn.request('GET', target)
            response = httpconn.getresponse()
            data = response.read()
        except urlfetch.DownloadError:
            logging.error("Failed to query: %s%s" % (host, target))
            return

        hosts = self._parse_hosts(data)

        for host in hosts:
            self.add_host(host.ip, host.domain)
            #print "%s, %s" % (host.ip, host.domain)

    def count(self):
        count = 0
        hosts = Host.all()
        count = hosts.count()

        return count

    def all(self):
        ret = []
        hosts = Host.all()
        for host in hosts:
            ret.append(host)

        return ret

    def find(self, query):
        ret = []
        if (len(query) == 0):
            return ret

        #hosts = db.GqlQuery("SELECT * FROM Host WHERE domain = :1", query)
        hosts = []

        for host in hosts:
            ret.append(host)

        return ret

def main():
    print "Do some test here."

if __name__ == '__main__':
    main()
