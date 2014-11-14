__author__ = 'Thomas'
import re
from os import path

class Settings(object):

    def __init__(self):
        print "[+] Initializing Settings class"
        if not path.isfile('vt.conf'):
            self.createConfig()
        # First initialize all settings to EMPTY, then read config file to get current settings
        self.parseConfig()

    # Getter & Setter for Base URL - so user cannot directly interact with variables
    def getBase(self):
        print "[+] Getting base URL of "+self.baseURL
        return self.baseURL
    def setBase(self, newBase):
        print "[+] Setting base URL to "+newBase
        self.baseURL = newBase
        self.updateConfig('base', newBase)
    # Getter & Setter for APIKey - so user cannot directly interact with variables
    def getAPI(self):
        print "[+] Getting API key of "+self.apikey
        return self.apikey
    def setAPI(self, newKey):
        print "[+] Setting API key to "+newKey
        self.apikey = newKey
        self.updateConfig('apikey', newKey)
        # Getter & Setter for Filename - so user cannot directly interact with variables
    def getFileName(self):
        print "[+] Getting filename of "+self.filename
        return self.filename
    def setFileName(self, filename):
        print "[+} Setting filename to "+filename
        self.filename = filename
    def getResource(self):
        print "[+] Getting resource id "+self.resource
        return self.resource
    def setResource(self, newID):
        print "[+] Setting resource id to "+newID
        self.resource = newID

    def parseConfig(self):
        with open("vt.conf", "r") as conf:
            lines = conf.readlines()
            # strip lines[i] of '\n', then parse around ':::', then select the latter part of the line
            apikey = lines[0].strip().split(":::")[1]
            baseURL = lines[1].strip().split(":::")[1]
            resource = lines[2].strip().split(":::")[1]
            lastfile = lines[3].strip().split(":::")[1]
            self.setAPI(apikey)
            self.setBase(baseURL)
            self.setResource(resource)
            self.setFileName(lastfile)
        conf.close()

    def updateConfig(self, key, val):
        # create temporary array to hold lines
        tmp = []
        with open("vt.conf", "r") as conf:
            lines = conf.readlines()
            # lines[0] = apikey, lines[1] = base
            for line in lines:
                # match beginning of 'line' to 'key'
                if re.match(key, line):  # append new key/val to a temporary list
                    tmp.append(key+":::"+val)
                else:  # keep old key/val if it's not what we're looking for
                    tmp.append(line.strip())
        # close file for reading
        conf.close()
        with open("vt.conf", "w") as conf:
            for line in tmp:
                conf.write(line+"\n")
        # close file for writing
        conf.close()

    def createConfig(self):
        with open("vt.conf", "w") as conf:
            conf.write("apikey:::\n")
            conf.write("base:::https://www.virustotal.com/vtapi/v2/\n")
            conf.write("resource:::\n")
            conf.write("lastfile:::\n")
        conf.close()