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

#import base64
import httplib 

CANT_RESOLVE = "-"

class DNS():
    def __init__(self):
        pass
    
    def lookup(self, domain):
        pass
    
    @staticmethod
    def unshake(input_str):
        output_str = ""

        i = 0
        n = 0
        while (n < len(input_str) / 2):
            output_str += input_str[i + 1]
            output_str += input_str[i]
            i += 2
            n += 1

        if (i < len(input_str)):
            output_str += input_str[-1]

        return output_str

class DNSWeb(DNS):
    def __init__(self):
        self.server = "www.lookupserver.com"
        self.add_offset = 769
        self.url = "/?forward_dns=%s&submit=Lookup"
    
    def do_web_lookup(self, domain):
        httpconn = httplib.HTTPConnection(self.server, 80)
        target = self.url % domain
        httpconn.request('GET', target)
        data = ""

        try:
            response = httpconn.getresponse()
            data = response.read(1024)
        except urlfetch.DownloadError:
            pass

        return data

    # FIXME: Find a nother way to parse result
    def _parse_address(self, domain, data):
        if (len(data) == 0):
            return CANT_RESOLVE

        # Fix special char in domain, lookupserver filtered it in output
        special_chars = 0
        for ch in domain:
            if ch == '-':
                special_chars += 1

        start = data[self.add_offset + len(domain) - special_chars:]
        off = 0
        found = False
        address = ""
        while (off < len(start)):
            if (start[off] == '<'):
                found = True
                break
            else:
                off = off + 1
        if found:
            address = start[0:off]

        return address

    def lookup(self, domain):
        if (len(domain) == 0):
            return CANT_RESOLVE
        
        data = self.do_web_lookup(domain)
        address = self._parse_address (domain, data)

        if (len(address) == 0 or address == domain):
            return CANT_RESOLVE

        return address

def main():
    print "Do some test here."

if __name__ == '__main__':
    main()