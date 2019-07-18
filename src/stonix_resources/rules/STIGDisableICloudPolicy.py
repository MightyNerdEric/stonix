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
Created on Oct 27, 2016

@author: dwalker
@change: 2017/03/30 dkennel Marked rule as FISMA high
@change: 2017/07/17 ekkehard - make eligible for macOS High Sierra 10.13
@change: 2018/06/08 ekkehard - make eligible for macOS Mojave 10.14
'''

import traceback
import os
from re import search
from ..rule import Rule
from ..logdispatcher import LogPriority
from ..stonixutilityfunctions import iterate
from ..CommandHelper import CommandHelper


class STIGDisableICloudPolicy(Rule):

    def __init__(self, config, environ, logdispatch, statechglogger):
        '''Constructor'''
        Rule.__init__(self, config, environ, logdispatch, statechglogger)

        self.logger = logdispatch
        self.rulenumber = 366
        self.rulename = "STIGDisableICloudPolicy"
        self.formatDetailedResults("initialize")
        self.sethelptext()
        self.rootrequired = True
        self.applicable = {'type': 'white',
                           'os': {'Mac OS X': ['10.11.0', 'r', '10.14.10']},
                           'fisma': 'high'}
        datatype = "bool"
        key = "DISABLEICLOUDPROMPT"
        instructions = "To disable the installation of the Disable " + \
            "iCloud profile set the value of DISABELICLOUDPROMPT to False"
        default = True
        self.ci = self.initCi(datatype, key, instructions, default)
        self.iditerator = 0
        self.identifier = "mil.disa.STIG.Disable_iCloud_Prompt.alacarte"
        if search("10\.11\.*", self.environ.getosver()):
#             self.profile = "/Users/username/stonix/src/" + \
#                 "stonix_resources/files/" + \
#                 "U_Apple_OS_X_10-11_V1R1_STIG_Disable_iCloud_Policy.mobileconfig"
            self.profile = "/Applications/stonix4mac.app/Contents/" + \
                         "Resources/stonix.app/Contents/MacOS/" + \
                         "stonix_resources/files/" + \
                         "U_Apple_OS_X_10-11_V1R1_STIG_Disable_iCloud_Policy.mobileconfig"
        else:
#             self.profile = "/Users/username/stonix/src/" + \
#                 "stonix_resources/files/" + \
#                 "U_Apple_macOS_10-12_V1R1_STIG_Disable_iCloud_Policy.mobileconfig"
            self.profile = "/Applications/stonix4mac.app/Contents/" + \
                         "Resources/stonix.app/Contents/MacOS/" + \
                         "stonix_resources/files/" + \
                         "U_Apple_macOS_10-12_V1R1_STIG_Disable_iCloud_Policy.mobileconfig"
    def report(self):
        try:
            compliant = False
            self.detailedresults = ""
            self.ch = CommandHelper(self.logger)
            cmd = ["/usr/bin/profiles", "-P"]
            if not self.ch.executeCommand(cmd):
                compliant = False
                self.detailedresults += "Unable to run profiles command\n"
            else:
                output = self.ch.getOutput()
                if output:
                    for line in output:
                        if search("^There are no configuration profiles installed", line.strip()):
                            compliant = False
                            self.detailedresults += "There are no configuration profiles installed\n"
                            break
                        elif search("mil\.disa\.STIG\.Disable_iCloud_Prompt\.alacarte$", line.strip()):
                            compliant = True
                            break
            self.compliant = compliant
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
    
    def fix(self):
        try:
            if not self.ci.getcurrvalue():
                return
            if os.path.exists(self.profile):
                success = True
                self.detailedresults = ""
                self.iditerator = 0
                eventlist = self.statechglogger.findrulechanges(self.rulenumber)
                for event in eventlist:
                    self.statechglogger.deleteentry(event)
                cmd = ["/usr/bin/profiles", "-I", "-F", self.profile]
                if not self.ch.executeCommand(cmd):
                    success = False
                else:
                    self.iditerator += 1
                    myid = iterate(self.iditerator, self.rulenumber)
                    cmd = ["/usr/bin/profiles", "-R", "-p", self.identifier]
                    event = {"eventtype": "comm",
                             "command": cmd}
                    self.statechglogger.recordchgevent(myid, event)
            else:
                success = False
            self.rulesuccess = success
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.rulesuccess = False
            self.detailedresults += "\n" + traceback.format_exc()
            self.logdispatch.log(LogPriority.ERROR, self.detailedresults)
        self.formatDetailedResults("fix", self.rulesuccess,
                                   self.detailedresults)
        self.logdispatch.log(LogPriority.INFO, self.detailedresults)
        return self.rulesuccess