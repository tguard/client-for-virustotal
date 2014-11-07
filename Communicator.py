__author__ = 'Thomas'
# Public API Key: 5c8c9935708d4833527cb91c2477a43cce5f508aad21fd26f19a454d5498ea6b
# Base URI: https://www.virustotal.com/vtapi/v2/
#       Send a file with: BaseURI + 'file/scan'
# Response: JSON object with a couple attributes, HTTP 204 Code is sent if the request limit is met
#       response_code: 0 if doesn't exist, -2 if queued for scanning, 1 if it was retrieved successfully
#       verbose_msg: Provides extra info about response_code
# Limit: 4 requests/minute

import postfile
import urllib
import urllib2
import simplejson
from Settings import *


class Communicator(object):

    def __init__(self):
        self.settings = Settings()

    def sendFile(self, filename):
        # if no file specified
        if filename is "Choose a File":
            return 0
        host = 'www.virustotal.com'
        selector = self.settings.getBase() + 'file/scan'
        if host is '' or filename is '':
            raise Exception("One or more sendFile arguments is empty. Double-check parameters.")

        files_to_send = open(filename, "rb").read()
        files = [("file", filename, files_to_send)]
        fields = [("apikey", self.settings.getAPI())]
        response = simplejson.loads(postfile.post_multipart(host, selector, fields, files))
        # print message about successful/failed queue
        print '[+]', response['verbose_msg']
        # return a dictionary containing VT's response
        return response

    def getReport(self, id):
        url = self.settings.getBase() + 'file/report'
        params = {'resource': id,
                  'apikey': self.settings.getAPI()}
        data = urllib.urlencode(params)
        # send a POST request for the specified report/resource
        req = urllib2.Request(url, data)
        # convert response from string to dict via simplejson.loads()
        response = simplejson.loads(urllib2.urlopen(req).read())
        return response

    def reScan(self, id):
        url = self.settings.getBase() + 'file/rescan'
        params = {'resource': id,
                  'apikey': self.settings.getAPI()}
        data = urllib.urlencode(params)
        req = urllib2.Request(url, data)
        # convert response from string to dict via simplejson.loads()
        response = simplejson.loads(urllib2.urlopen(req).read())
        return response

    def prettyPrint(self, response):
        print # extra line for more clarity
        for key in response:
            if key == 'scans':
                scans = response[key]
                for scanner in scans:
                    results = response['scans'][scanner]
                    print scanner.upper() + " " + str(results)
            else:
                print key.upper(), ':', response[key]
        print

    # special version of prettyPrint that formats response{} for relevant data
    def printReport(self, response):
        filename = "av_scans.log"
        output = open(filename, "w+")
        hashes = '-----------------------------------------------'
        print "\n" + hashes
        print response['verbose_msg']
        print 'Returned Scan for', response['scan_date']
        print hashes
        print "Positives:", str(response['positives']) + '/' + str(response['total'])
        print
        print 'MD5:', response['md5']
        print 'SHA1:', response['sha1']
        print 'SHA256:', response['sha256'], "\n"
        print 'Virus scan results logged to', filename
        for scanner in response['scans']:
            # write the results of each AV scanner to a log file
            line = str(scanner.upper()) + ':' + str(response['scans'][scanner]) + "\n"
            output.write(line)
        output.close()