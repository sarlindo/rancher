#!/usr/bin/python

import os
import sys
import getopt
import requests, json
from requests.auth import HTTPBasicAuth
from time import sleep
import random

# log errors
def log(msg):
        sys.stderr.write("%s\n" % msg)

# usage help message
def usage(msg = None):

        log("Usage: find_ports [--url=<RANCHER_URL> --key=<RANCHER_ACCESS_KEY> --secret=<RANCHER_SECRET_KEY>]\n"
            "                  --stack=<STACK> --service=<SERVICE> [--port=<PORT>] [--one] [--uri=<URI>] [--proto=<proto>]\n"
            "Finds public ports for a specific specific service in rancher\n"
            "Credentials can be supplied as args or defined as environment vars\n"
            "If port is specified then only that *private* port will be searched for, if not then you must have\n"
            "only one exposed port. If this script finds more than one it will return an error. THis is built\n"
            "in in order to handle random external ports when Rancher get round to it.\n"
            "This script returns a list of the public ips and ports <ip1>:<port1> <ip2>:<port2> ...\n"
            "Unless --one is specified in which case it returns one random instance\n"
            "Giving a uri which could be as simple as / will return an http:// url. THis obviously also implies --one\n"
            "URL protocol is normally http but can be specified if you need https, ssh etc\n"
            "%s" % msg or "")
        sys.exit(1)

# get credentials form args or env
def getArgs():
        args = {}
        args['rancher_url'] = os.environ.get("RANCHER_URL",None)
        args['rancher_key'] = os.environ.get("RANCHER_ACCESS_KEY",None)
        args['rancher_secret'] = os.environ.get("RANCHER_SECRET_KEY",None)
        args['port'] = 0
        args['one'] = False
        args['uri'] = False
        args['proto'] = 'http'

        try:
                opts, argv = getopt.getopt(sys.argv[1:],"hu:k:s:",
                                           ["help","url=","key=","secret=","stack=","service=","port=","one","uri=","proto="])
                for o,a in opts:
                        if o in ("-h","--help"):
                                usage()
                                sys.exit(1)
                        elif o in ("-u","--url"):
                                args['rancher_url'] = a
                        elif o in ("-k","--key"):
                                args['rancher_key'] = a
                        elif o in ("-s","--secret"):
                                args['rancher_secret'] = a
                        elif o in ("--stack"):
                                args['stack'] = a
                        elif o in ('--service'):
                                args['service'] = a
                        elif o in ("--port"):
                                args['port'] = int(a)
                        elif o in ("--one"):
                                args['one'] = True
                        elif o in ("--uri"):
                                args['one'] = True
                                args['uri'] = a
                        elif o in ("--proto"):
                                args['proto'] = a

        except getopt.GetoptError,e:
                usage(e)

        if args.get('rancher_url',None) == None:
                usage("Rancher URL not specified")
                sys.exit(1)
        if args.get('rancher_key',None) == None:
                usage("Rancher key not specified")
                sys.exit(1)
        if args.get('rancher_secret',None) == None:
                usage("Rancher secret not specified")
                sys.exit(1)
        if args.get('stack',None) == None:
                usage("Stack not specified")
                sys.exit(1)
        if args.get('service',None) == None:
                usage("Service not specified")
                sys.exit(1)

        args['rancher_protocol'], args['rancher_host'] = args['rancher_url'].split("://")

        return args

# make a rancher url
def rancherUrl(args,uri):

        url = "%s://%s%s" % (args['rancher_protocol'],args['rancher_host'],uri)

        return url

# general purpose rancher call
def rancherCall(args,url):
        response = requests.get(url,auth=HTTPBasicAuth(args['rancher_key'],args['rancher_secret']))

        if response.status_code == 200:
                data = json.loads(response.text)
        else:
                log("Could not retrieve link %s - staus %d" % (url, response.status_code))
                data = {}

        return response.status_code, data

# follow a link
def rancherLink(args,data,link):

        url = data['links'][link]
        status, data = rancherCall(args,url)

        return status,data

# find an item in data by name
def findByName(data,name):
        for item in data['data']:
                if item['name'] == name:
                        return item
        return None

# traverse a path from a given rancher item
def rancherTraverse(args,item,path):

        thisitem = item
        for step in path:
                status, children = rancherLink(args,thisitem,step[0])
                child = findByName(children,step[1])

                if not child:
                        log("Cannot find %s called %s in %s %s" % (step[0], step[1], item['type'], item['name']))
                        sys.exit(2)

                thisitem = child

        return thisitem

# get my environment with a bit of error checking
def getEnvironment(args):
        status, data = rancherCall(args,rancherUrl(args,'/v1/projects'))

        if status != 200:
                sys.exit(2)
        if len(data['data']) != 1:
                log("Found %d environments when expecting one" % len(data['data']))
                sys.exit(2)

        status, environment = rancherLink(args,data['data'][0],'self')
        return environment

args = getArgs()

environment = getEnvironment(args)
service = rancherTraverse(args,environment,[
                               ('environments', args['stack']),
                               ('services',     args['service'])])

status, instances = rancherLink(args,service,'instances')
if not instances:
        print "No instances of service %s in stack %s found" % (args['stack'],args['service'])

# if we are asked for a single instance then make it a random one
if args['one']:
        random.shuffle(instances['data'])

for instance in instances['data']:
        if instance['state'] == 'running':
                status, ports = rancherLink(args,instance,'ports')
                if args['port'] == 0 and len(ports['data']) > 1:
                        log("You must specify the internal port if multiple ports are exposed")
                else:
                        for port in ports['data']:
                                if port['state'] == 'active' and port['publicPort'] and (args['port'] == 0 or port['privatePort'] == args['port']):
                                        status, private_ip = rancherLink(args,port,'privateIpAddress')
                                        status, public_ip = rancherLink(args,port,'publicIpAddress')
                                        if args['uri']:
                                                print "%s://%s:%d%s" % (args['proto'],public_ip['address'],port['publicPort'],args['uri'])
                                        else:
                                                print "%s:%d" % (public_ip['address'],port['publicPort']),
                                        if args['one']:
                                                sys.exit(0)
