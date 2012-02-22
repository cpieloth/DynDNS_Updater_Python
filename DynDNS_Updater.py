#!/usr/bin/env python
#
# Copyright 2012 Christof Pieloth
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib
import httplib
import base64
import logging

class DynDns:
    GOOD = "good"
    NOCHG = "nochg"
    BADAUTH = "badauth"
    NOTFQDN = "notfqdn"
    NOHOST = "nohost"
    NUMHOST = "numhost"
    ABUSE = "abuse"
    BADAGENT = "badagent"
    DNSERR = "dnserr"
    NINIONE = "991"
    
    @staticmethod
    def getMessage(rcode):
        rcode = rcode.strip()
        rcodes = rcode.split(' ')
        # http://dyn.com/support/developers/api/return-codes/
        if DynDns.GOOD == rcodes[0]:
            return "%s: successful update" % rcode
        elif DynDns.NOCHG == rcodes[0]:
            return "%s: successful update but the IP address or other settings have not changed" % rcode
        elif DynDns.BADAUTH == rcodes[0]:
            return "%s: The username and password pair do not match a real user." % rcode
        elif DynDns.NOTFQDN == rcodes[0]:
            return "%s: The hostname specified is not a fully-qualified domain name." % rcode
        elif DynDns.NOHOST == rcodes[0]:
            return "%s: The hostname specified does not exist in this user account." % rcode
        elif DynDns.NUMHOST == rcodes[0]:
            return "%s: Too many hosts (more than 20) specified in an update. Also returned if trying to update a round robin." % rcode
        elif DynDns.ABUSE == rcodes[0]:
            return "%s: The hostname specified is blocked for update abuse." % rcode
        elif DynDns.BADAGENT == rcodes[0]:
            return "%s: The user agent was not sent or HTTP method is not permitted." % rcode
        elif DynDns.DNSERR == rcodes[0]:
            return "%s: DNS error encountered." % rcode
        elif DynDns.NINIONE == rcodes[0]:
            return "%s: There is a problem or scheduled maintenance on our side." % rcode
        else:
            return "Unknown return code: %s" % rcode
        
    @staticmethod
    def checkCode(rcode, expected):
        rcode = rcode.strip()
        rcodes = rcode.split(' ')
        return rcodes[0] == expected
    
    @staticmethod
    def update(user, pwd, hostname, ip):
        # http://dyn.com/support/developers/api/perform-update/
        params = urllib.urlencode({"hostname": hostname, "myip": ip})
        url = "/nic/update?" + params
        base64auth = base64.b64encode('%s:%s' % (user, pwd))
        headers = {"Authorization": "Basic %s" % base64auth, "User-Agent": urllib.URLopener.version}
        
        conn = httplib.HTTPSConnection("members.dyndns.org", 443)
        conn.request("GET", url, None, headers)
        res = conn.getresponse()
        logging.debug("%s %s" % (res.status, res.reason))
        rcode = res.read()
        conn.close()
        return rcode


def main():
    logging.basicConfig(filename='DynDNS_Updater.log', format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    USER = "user" # TODO set user
    PASSWORD = "pwd"    # TODO set password
    HOSTNAME = "host.dyndns.org"    # TODO set hostname
    IP = "ip"    # TODO set ip
    
    rcode = DynDns.update(USER, PASSWORD, HOSTNAME, IP)
    if DynDns.checkCode(rcode, DynDns.GOOD) or DynDns.checkCode(rcode, DynDns.NOCHG):
        logging.info(DynDns.getMessage(rcode))
    else:
        logging.error(DynDns.getMessage(rcode))

if __name__ == "__main__":
    main()
