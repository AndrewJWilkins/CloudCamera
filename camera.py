#! /usr/bin/python
"""
camera.py
Camera imaging and fits routines using input from camera.cpp
"""

__author__ = "John Armstrong"
__copyright__ = "NA"
__credits__ = ["Joseph Huehnerhoff"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "NA"
__email__ = "NA"
__status__ = "Developement"

import numpy as np
import pyfits
import subprocess
import time
import os
#import Image
import thread
from logger import *

class CameraExpose(object):
    def __init__(self):
        self.l = Logger()
        self.wait = 1.0
        self.status = None
        self.ssag = os.getcwd()+"/camera"
        #self.ssag = 'camera2'
        self.statusDict = {1:'idle', 2:'expose', 3:'reading'}
        self.logType = 'cloud'
        self.gain = 1

    def expose(self, name, exp, dir, gain):
        thread.start_new_thread(self.runExpose, (name, exp, dir, gain))

    def runExpose(self, name, exp, dir, gain):
        """
        Connect to the OpenSSAG and take image
        input a given file name and exposure
        output whether the image was successful


        Tells camera to take an image, it will output a binary file named "test" with 1000 ms exposure.
        Can also use './camera test 0 0' to check camera.
        """

        if dir == None:
            dir = os.getcwd()

        if '.fit' not in name:
            name = name+'.fits'
        name = dir+'/'+str(name)
        #print dir, name, self.ssag, exp
        expose = float(exp)*1000
        #print expose

        if gain == None:
            gain = self.gain


        try:

            subprocess.Popen([self.ssag, 'image', 'binary', str(expose), str(gain)])
            #self.l.logStr(str('Expose\t%s image binary %s' % (self.ssag,str(exp * 1000))), self.logType)
            self.status = 2
            #Pause for the camera to run
            time.sleep(self.wait+float(exp))
            self.status = 1

            binary=np.fromfile('binary',dtype='u1').reshape(1024,1280)

            # --------------------------
            # Used for testing array procedure, can remove once program is tested on-sky.
            # print binary.shape
            # print binary.dtype.name
            # print binary
            # ---------------------------

            prihdr = self.createHeader(exp, gain)  #create emtpy header information
            hdu=pyfits.PrimaryHDU(binary, header = prihdr)  #create a primary header file for the FITS image
            hdulist=pyfits.HDUList([hdu])

            prihdr['EXPTIME'] = str(exp)
            prihdr['IMAGTYP'] = 'guide'
            # Write the image and header to a FITS file using variable name.
            name = self.checkFile(name)
            hdulist.writeto(name, clobber=True)
            #im = Image.fromarray(binary)
            #im.save("tmp.jpg")

            #self.l.logStr('SaveIm\t%s' % name)
            return True

        except Exception,e:
            print "failed"
            print str(e)
            return False

    def checkFile(self, fileName):
        if os.path.exists(fileName):
            #print '%s exists, appending unique date stamp' % fileName
            name = fileName.replace('.fits','')+time.strftime('_%Y%m%dT%H%M%S.fits')
            #print 'New filename is %s' % name
            return name
        else:
            return fileName

    def createHeader(self, exp, gain):
        prihdr = pyfits.Header()
        prihdr['COMMENT'] = 'MRO Guider Camera'
        prihdr['COMMENT'] = 'Orion Star Shoot Auto Guider'
        prihdr['IMAGTYP'] = None
        prihdr['EXPTIME'] = exp
        prihdr['CCDBIN1'] = 1
        prihdr['CCDBIN2'] = 1
        prihdr['GAIN'] = gain
        prihdr['RN'] = None
        return prihdr

    def checkStatus(self):
        print "return some status message"
        print self.status, self.statusDict[self.status]
        return self.status

    def checkConnection(self):
        try:
            subprocess.Popen([self.ssag, '0', '0', '0'])
        except Exception, e:
            print e


    def help(self):
        print __doc__
        return

if __name__=="__main__":
    c = CameraExpose()
    c.runExpose('test',0.1, None, 8)
