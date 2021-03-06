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

import argparse
import base64
import getpass 
import httplib
import logging
import urllib

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
        base64auth = base64.b64encode('%s:%s' % (user, pwd))
        return DynDns.updateBase(base64auth, hostname, ip)
    
    @staticmethod
    def updateBase(base64auth, hostname, ip):
        # TODO setUsername, setPassword, setAuthentication, setIp, setHostname, update
        # http://dyn.com/support/developers/api/perform-update/
        params = urllib.urlencode({"hostname": hostname, "myip": ip})
        url = "/nic/update?" + params
        headers = {"Authorization": "Basic %s" % base64auth, "User-Agent": urllib.URLopener.version}
        conn = httplib.HTTPSConnection("members.dyndns.org", 443)
        conn.request("GET", url, None, headers)
        res = conn.getresponse()
        logging.debug("%s %s" % (res.status, res.reason))
        rcode = res.read()
        conn.close()
        return rcode


def generateAuthentication(user, pwd):
    if(not user):
        user = raw_input("Username: ")
    if(not pwd):
        while(True):
            pwd = getpass.getpass("Password: ")
            pwd_check = getpass.getpass("Password again: ")
            if(pwd == pwd_check):
                break
            print("The passwords are different. Please try again or cancel with CTRL+C")
    base64auth = base64.b64encode('%s:%s' % (user, pwd))
    print("Your Base64 authentication is:")
    print(base64auth)
    return

def main():
    # Prepare CLI arguments
    parser = argparse.ArgumentParser(description='A DynDNS Updater in Python.')
    parser.add_argument("-u", "--user", help="DynDNS username (required or use -a)")
    parser.add_argument("-p", "--password", help="password for DynDNS account (required or use -a)")
    parser.add_argument("-a", "--authentication", help="Base64 encoded <user>:<password> (optional, to make username and password unreadable to the unaided eye)")
    parser.add_argument("-d", "--domain", help="DynDNS hostname")
    parser.add_argument("-i", "--ip", help="IP address to set")
    parser.add_argument("-g", "--generate", help="generate Base64 encoded <user>:<password> for authentication", action="store_true")
    parser.add_argument("-l", "--log", help="logging to file")
    
    # Check constraints
    args = parser.parse_args()
    if(args.generate):
        generateAuthentication(args.user, args.password)
        return
    if(args.log):
        logging.basicConfig(filename=args.log, format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    else:
        logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    if((not args.user or not args.password) and not args.authentication):
        logging.error("No authentication (username, password or authentication) set!")
        return
    if(not args.domain or not args.ip):
        logging.error("No domain or IP address set!")
        return
    
    # Update DynDNS
    if(args.authentication):
        rcode = DynDns.updateBase(args.authentication, args.domain, args.ip)
    else:
        rcode = rcode = DynDns.update(args.user, args.password, args.domain, args.ip)
        
    if DynDns.checkCode(rcode, DynDns.GOOD) or DynDns.checkCode(rcode, DynDns.NOCHG):
        logging.info(DynDns.getMessage(rcode))
    else:
        logging.error(DynDns.getMessage(rcode))

if __name__ == "__main__":
    main()
