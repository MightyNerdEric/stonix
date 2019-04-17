###############################################################################
#                                                                             #
# Copyright 2019. Triad National Security, LLC. All rights reserved.          #
# This program was produced under U.S. Government contract 89233218CNA000001  #
# for Los Alamos National Laboratory (LANL), which is operated by Triad       #
# National Security, LLC for the U.S. Department of Energy/National Nuclear   #
# Security Administration.                                                    #
#                                                                             #
# All rights in the program are reserved by Triad National Security, LLC, and #
# the U.S. Department of Energy/National Nuclear Security Administration. The #
# Government is granted for itself and others acting on its behalf a          #
# nonexclusive, paid-up, irrevocable worldwide license in this material to    #
# reproduce, prepare derivative works, distribute copies to the public,       #
# perform publicly and display publicly, and to permit others to do so.       #
#                                                                             #
###############################################################################

'''
Created on Jun 27, 2012
This InstallVLock object installs the vlock package to enable screen locking
@author: Derek T Walker
@change: dkennel 04/18/2014 replaced old-style CI invocation
@change: 2014/10/17 ekkehard OS X Yosemite 10.10 Update
@change: 2015/04/15 dkennel updated for new isApplicable
'''
from __future__ import absolute_import
from ..pkghelper import Pkghelper
from ..logdispatcher import LogPriority
from ..rule import Rule
from ..CommandHelper import CommandHelper
import traceback
import re


class InstallVLock(Rule):
    '''
    This class installs the vlock package to enable screen locking
    '''

    def __init__(self, config, environ, logger, statechglogger):
        '''
        Constructor
        '''
        Rule.__init__(self, config, environ, logger, statechglogger)
        self.logger = logger
        self.rulenumber = 121
        self.rulename = "InstallVLock"
        self.mandatory = True
        self.rootrequired = True
        self.detailedresults = "InstallVLock has not yet been run."
        self.guidance = ["NSA 2.3.5.6"]
        self.applicable = {'type': 'white',
                           'family': ['linux', 'freebsd']}

        # Configuration item instantiation
        datatype = 'bool'
        key = 'INSTALLVLOCK'
        instructions = "To disable installation of the command line " + \
            "screen lock program vlock set the value of INSTALLVLOCK to False."
        default = True
        self.ci = self.initCi(datatype, key, instructions, default)

        self.sethelptext()

    def report(self):
        '''Perform a check to see if package is already installed.
           If so, there is  no need to run Fix method

           @return: Bool
           @author: Derek T Walker '''
        try:
            self.detailedresults = ""
            self.ph = Pkghelper(self.logger, self.environ)
            self.ch = CommandHelper(self.logger)
            vlock = ""
            if self.ph.manager == "yum":
                cmd = ["/usr/bin/yum", "whatprovides", "vlock"]
            elif self.ph.manager == "dnf":
                cmd = ["/usr/bin/dnf", "whatprovides", "vlock"]
            if self.ph.manager == "yum" or self.ph.manager == "dnf":
                self.ch.executeCommand(cmd)
                output = self.ch.getOutput()
                for line in output:
                    if re.search("kbd", line):
                        vlock = "kbd"
                if vlock != "kbd":
                    vlock = "vlock"
            elif self.ph.manager == "zypper":
                vlock = "kbd"
            else:
                vlock = "vlock"
            present = self.ph.check(vlock)
            if present:
                self.compliant = True
            else:
                self.compliant = False
        except (KeyboardInterrupt, SystemExit):
            # User initiated exit
            raise
        except Exception:
            self.rulesuccess = False
            self.detailedresults += "\n" + traceback.format_exc()
            self.logdispatch.log(LogPriority.ERROR, self.detailedresults)
        self.formatDetailedResults("report", self.compliant,
                                   self.detailedresults)
        self.logdispatch.log(LogPriority.INFO, self.detailedresults)
        return self.compliant

###############################################################################

    def fix(self):
        '''
        The fix method will apply the required settings to the system.
        self.rulesuccess will be updated if the rule does not succeed.
        Attempt to install Vlock, record success or failure in event
        logger.
        @return: bool
        @author: Derek T Walker'''
        try:
            self.detailedresults = ""
            if not self.ci.getcurrvalue():
                return

            # Clear out event history so only the latest fix is recorded
            eventlist = self.statechglogger.findrulechanges(self.rulenumber)
            for event in eventlist:
                self.statechglogger.deleteentry(event)

            self.rulesuccess = self.ph.install("vlock")
            if self.rulesuccess and self.ph.manager != "zypper":
                myid = "0121001"
                cmd = self.ph.getInstall()
                cmd += "vlock"
                event = {"eventtype": "comm",
                         "command": cmd}
                self.statechglogger.recordchgevent(myid, event)
                self.detailedresults += "InstallVLock fix was run and was " + \
                    "successful"
            else:
                self.detailedresults += "InstallVLock fix was run and was " + \
                    "not successful"
        except (KeyboardInterrupt, SystemExit):
            # User initiated exit
            raise
        except Exception:
            self.rulesuccess = False
            self.detailedresults += "\n" + traceback.format_exc()
            self.logdispatch.log(LogPriority.ERROR, self.detailedresults)
        self.formatDetailedResults("fix", self.rulesuccess,
                                   self.detailedresults)
        self.logdispatch.log(LogPriority.INFO, self.detailedresults)
        return self.rulesuccess
