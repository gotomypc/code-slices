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

from google.appengine.ext import db
from datetime import datetime
from dns import Host
from dns import CANT_RESOLVE

import logging

class HostCache(Host):
    hit = db.IntegerProperty()
    failed = db.IntegerProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now_add=True)

class DNSCacheManager(object):
    def __init__(self):
        self.cache_life_limit = 60 * 60 * 60 * 6 # default 6 hour

    def set_cache_life(self, limit):
        self.cache_life_limit = limit

    def update(self, domain, ip, hit = True):
        updated = False
        hosts = db.GqlQuery("SELECT * FROM HostCache WHERE domain = :1 LIMIT 1", domain)
        for host in hosts:
            if hit:
                host.hit += 1
            else:
                host.failed +=1

            if (len(host.ip) < 2):
                host.ip = ip
            host.update_date = datetime.utcnow()

            host.put()
            updated = True
            #logging.info("%s, %s, hit = %d, failed = %d" % (host.domain, host.ip, host.hit, host.failed))

        if (not updated):
            h = 1
            f = 0
            if (not hit):
                h = 0
                f = 1
                
            host = HostCache(ip = ip, domain = domain, hit = h, failed = f)
            host.put()
            #logging.info("%s, %s, hit = %d" % (domain, ip, hit))

    def get(self, domain):
        hosts = db.GqlQuery("SELECT * FROM HostCache WHERE domain = :1 LIMIT 1", domain)
        for host in hosts:
            return host

        return None

    def lookup(self, domain):
        host = self.get(domain)
        if host is None:
            return CANT_RESOLVE
        
        if host.ip == CANT_RESOLVE:
            return CANT_RESOLVE

        life = datetime.utcnow() - host.update_date
        if life.seconds < self.cache_life_limit:
            logging.debug("Cache hit: %s, life/limit: %d/%d" %
                          (domain, life.seconds, self.cache_life_limit))
            return host.ip
        else:
            logging.debug("Cache out of time: %s " % domain)

        # Mark as un avaliable
        host.ip = CANT_RESOLVE
        host.put()

        return CANT_RESOLVE

def main():
    print "Do some test here."

if __name__ == '__main__':
    main()
