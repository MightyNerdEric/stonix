###############################################################################
#                                                                             #
# Copyright 2015.  Los Alamos National Security, LLC. This material was       #
# produced under U.S. Government contract DE-AC52-06NA25396 for Los Alamos    #
# National Laboratory (LANL), which is operated by Los Alamos National        #
# Security, LLC for the U.S. Department of Energy. The U.S. Government has    #
# rights to use, reproduce, and distribute this software.  NEITHER THE        #
# GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY,        #
# EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  #
# If software is modified to produce derivative works, such modified software #
# should be clearly marked, so as not to confuse it with the version          #
# available from LANL.                                                        #
#                                                                             #
# Additionally, this program is free software; you can redistribute it and/or #
# modify it under the terms of the GNU General Public License as published by #
# the Free Software Foundation; either version 2 of the License, or (at your  #
# option) any later version. Accordingly, this program is distributed in the  #
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the     #
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    #
# See the GNU General Public License for more details.                        #
#                                                                             #
###############################################################################
'''
This method runs all the report methods for RuleKVEditors in defined in the
dictionary

@author: ekkehard j. koch
@change: 2014/03/10 ekkehard Original Implementation
@change: 2014/10/17 ekkehard OS X Yosemite 10.10 Update
@change: 2014/10/20 ekkehard Artifact artf34318 : ConfigureNetworks(122)
@change: 2015/04/14 dkennel updated for new isApplicable
'''
from __future__ import absolute_import
import traceback
from ..ruleKVEditor import RuleKVEditor
from ..CommandHelper import CommandHelper
from ..ServiceHelper import ServiceHelper
from ..logdispatcher import LogPriority
from ..networksetup import networksetup


class ConfigureNetworks(RuleKVEditor):
    '''

    @author: ekkehard j. koch
    @change: Breen Malmberg - 12/20/2016 - (see method doc strings)
    '''

###############################################################################

    def __init__(self, config, environ, logdispatcher, statechglogger):
        RuleKVEditor.__init__(self, config, environ, logdispatcher,
                              statechglogger)
        self.rulenumber = 122
        self.rulename = 'ConfigureNetworks'
        self.formatDetailedResults("initialize")
        self.mandatory = True
        self.helptext = "This rules set the network setup of your OS X " + \
        "system. It disables bluetooth and disables the wireless " + \
        "(WiFi/802.11) interface(s) in the Network System Preference " + \
        "Panel unless the location name has 'wi-fi', 'wifi', 'wireless', " + \
        "'airport', 'off-site', or 'offsite' (case insensitive) in the " + \
        "location name. We recommend having one location for off-site " + \
        "DHCP, and one for each static IP address."
        self.rootrequired = True
        self.guidance = []
        self.applicable = {'type': 'white',
                           'os': {'Mac OS X': ['10.9', 'r', '10.12.10']}}
        self.nsobject = networksetup(self.logdispatch)
        self.ch = CommandHelper(self.logdispatch)
        self.sh = ServiceHelper(self.environ, self.logdispatch)
        self.addKVEditor("DisableBluetoothUserInterface",
                         "defaults",
                         "/Library/Preferences/com.apple.Bluetooth",
                         "",
                         {"ControllerPowerState": ["0", "-int 0"]},
                         "present",
                         "",
                         "Disable Bluetooth User Interface.",
                         None,
                         False,
                         {})
        self.addKVEditor("DisableBluetoothInternetSharing",
                         "defaults",
                         "/Library/Preferences/com.apple.Bluetooth",
                         "",
                         {"PANServices": ["0", "-int 0"]},
                         "present",
                         "",
                         "Disable Bluetooth Internet Sharing.",
                         None,
                         False,
                         {})

    def report(self):
        '''
        determine the compliance status of ConfigureNetworks
        on the current system

        @return: self.compliant
        @rtype: bool
        @author: ekkehard j. koch
        @change: Breen Malmberg - 12/20/2016 - added doc string; 
        '''

        self.logdispatch.log(LogPriority.DEBUG, "Entering ConfigureNetworks.report()...")

        self.detailedresults = ""
        self.compliant = True
        compliant = True
        kvcompliant = True

        try:

            if not RuleKVEditor.report(self, True):
                kvcompliant = False
                self.logdispatch.log(LogPriority.DEBUG, "KVeditor.report() returned False.")

            if not self.nsobject.getLocation():
                compliant = False
                self.logdispatch.log(LogPriority.DEBUG, "nsobject.getLocation() returned False. Will not run nsobject.updateCurrentNetworkConfigurationDictionary()!")

            if compliant:
                if not self.nsobject.updateCurrentNetworkConfigurationDictionary():
                    compliant = False
                    self.logdispatch.log(LogPriority.DEBUG, "nsobject.updateCurrentNetworkConfigurationDictionary() returned False. Will not run nsobject.report()!")

            if compliant:
                if not self.nsobject.report():
                    compliant = False
                    self.logdispatch.log(LogPriority.DEBUG, "nsobject.report() returned False.")
                self.resultAppend(self.nsobject.getDetailedresults())

            self.logdispatch.log(LogPriority.DEBUG, "compliant=" + str(compliant))
            self.logdispatch.log(LogPriority.DEBUG, "kvcompliant=" + str(kvcompliant))

            self.compliant = compliant and kvcompliant

            self.logdispatch.log(LogPriority.DEBUG, "Exiting ConfigureNetworks.report() and returning self.compliant=" + str(self.compliant))

        except (KeyboardInterrupt, SystemExit):
            # User initiated exit
            raise
        except Exception, err:
            self.rulesuccess = False
            messagestring = str(err) + " - " + str(traceback.format_exc())
            self.resultAppend(messagestring)
            self.logdispatch.log(LogPriority.ERROR, messagestring)
        self.formatDetailedResults("report", self.compliant,
                                   self.detailedresults)
        self.logdispatch.log(LogPriority.INFO, self.detailedresults)

        return self.compliant

###############################################################################

    def fix(self):
        '''
        run fix actions for ConfigureNetworks
        return True if all succeed

        @return: fixed
        @rtype: bool
        @author: ekkehard j. koch
        @change: Breen Malmberg - 12/20/2016 - added doc string; detailedresults
                and fixed var's moved to before try; 
        @change: Breen Malmberg - 1/12/2017 - added debug logging; default init kvfixed to True
        '''

        self.logdispatch.log(LogPriority.DEBUG, "Entering ConfigureNetworks.fix()...")

        self.detailedresults = ""
        fixed = True
        kvfixed = True

        try:

            self.logdispatch.log(LogPriority.DEBUG, "Running nsobject.getLocation()...")
            if not self.nsobject.getLocation():
                fixed = False

            if not fixed:
                self.logdispatch.log(LogPriority.DEBUG, "nsobject.getLocation() returned False! Will not run updateCurrentNetworkConfigurationDictionary() or nsobject.fix()!")

            if fixed:
                if not self.nsobject.updateCurrentNetworkConfigurationDictionary():
                    fixed = False

            if not fixed:
                self.logdispatch.log(LogPriority.DEBUG, "updateCurrentNetworkConfigurationDictionary() returned False! Will not run nsobject.fix()!")

            if fixed:
                self.logdispatch.log(LogPriority.DEBUG, "Running nsobject.fix()...")
                if not self.nsobject.fix():
                    fixed = False
                    self.logdispatch.log(LogPriority.DEBUG, "nsobject.fix() failed. fixed set to False.")
                self.resultAppend(self.nsobject.getDetailedresults())

            if not RuleKVEditor.fix(self, True):
                kvfixed = False
                self.logdispatch.log(LogPriority.DEBUG, "Kveditor fix failed. kvfixed set to False.")

            fixed = fixed and kvfixed

            self.logdispatch.log(LogPriority.DEBUG, "Exiting ConfigureNetworks.fix() and returning fixed=" + str(fixed) + "...")

        except (KeyboardInterrupt, SystemExit):
            # User initiated exit
            raise
        except Exception, err:
            self.rulesuccess = False
            fixed = False
            messagestring = str(err) + " - " + str(traceback.format_exc())
            self.resultAppend(messagestring)
            self.logdispatch.log(LogPriority.ERROR, self.detailedresults)
        self.formatDetailedResults("fix", fixed, self.detailedresults)
        self.logdispatch.log(LogPriority.INFO, self.detailedresults)
        return fixed

###############################################################################

    def afterfix(self):
        '''
        restart the service after fix

        @return: afterfixsuccessful
        @rtype: bool
        @author: ekkehard j. koch
        @change: Breen Malmberg - 12/20/2016 - added doc string; var init before
                try
        '''

        afterfixsuccessful = True

        try:

            service = "/System/Library/LaunchDaemons/com.apple.blued.plist"
            servicename = "com.apple.blued"
            if afterfixsuccessful:
                afterfixsuccessful = self.sh.auditservice(service, servicename)
            if afterfixsuccessful:
                afterfixsuccessful = self.sh.disableservice(service, servicename)
            if afterfixsuccessful:
                afterfixsuccessful = self.sh.enableservice(service, servicename)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as err:
            self.rulesuccess = False
            afterfixsuccessful = False
            messagestring = str(err) + " - " + str(traceback.format_exc())
            self.resultAppend(messagestring)
            self.logdispatch.log(LogPriority.ERROR, self.detailedresults)
        return afterfixsuccessful
