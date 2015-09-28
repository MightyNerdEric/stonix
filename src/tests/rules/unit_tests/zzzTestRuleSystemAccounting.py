#!/usr/bin/env python
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
This is a Unit Test for Rule SystemAccounting

@author: Breen Malmberg
@change: 2015/09/25 eball Updated to enable CI so that rule runs during test
@change: 2015/09/25 eball Added Debian/Ubuntu setup
'''
from __future__ import absolute_import
import unittest
import re
import os
from src.tests.lib.RuleTestTemplate import RuleTest
from src.stonix_resources.CommandHelper import CommandHelper
from src.tests.lib.logdispatcher_mock import LogPriority
from src.stonix_resources.rules.SystemAccounting import SystemAccounting


class zzzTestRuleSystemAccounting(RuleTest):

    def setUp(self):
        RuleTest.setUp(self)
        self.rule = SystemAccounting(self.config,
                                     self.environ,
                                     self.logdispatch,
                                     self.statechglogger)
        self.rulename = self.rule.rulename
        self.rulenumber = self.rule.rulenumber
        self.ch = CommandHelper(self.logdispatch)

    def tearDown(self):
        pass

    def runTest(self):
        self.simpleRuleTest()

    def setConditionsForRule(self):
        '''
        Configure system for the unit test
        @param self: essential if you override this definition
        @return: boolean - If successful True; If failure False
        @author: Breen Malmberg
        '''
        success = True
        self.rule.ci.updatecurrvalue(True)
        try:
            if re.search("debian|ubuntu", self.environ.getostype().lower()):
                sysstat = "/etc/default/sysstat"
                if os.path.exists(sysstat):
                    settings = open(sysstat, "r").read()
                    settings = re.sub(r"ENABLED=.+\n", "ENABLED=false",
                                      settings)
                else:
                    settings = "ENABLED=false"
                open(sysstat, "w").write(settings)
            else:
                f = open('/etc/rc.conf', 'w+')
                if os.path.exists('/etc/rc.conf'):
                    contentlines = f.readlines()
                    for line in contentlines:
                        if re.search('accounting_enable=', line):
                            contentlines = [c.replace(line,
                                                      'accounting_enable=NO\n')
                                            for c in contentlines]
                    if 'accounting_enable=NO\n' not in contentlines:
                        contentlines.append('accounting_enable=NO\n')
                    f.writelines(contentlines)
                    f.close()

                if os.path.exists('/var/account/acct'):
                    os.remove('/var/account/acct')

        except Exception:
            success = False
        return success

    def checkReportForRule(self, pCompliance, pRuleSuccess):
        '''
        check on whether report was correct
        @param self: essential if you override this definition
        @param pCompliance: the self.iscompliant value of rule
        @param pRuleSuccess: did report run successfully
        @return: boolean - If successful True; If failure False
        @author: Breen Malmberg
        '''
        self.logdispatch.log(LogPriority.DEBUG, "pCompliance = " +
                             str(pCompliance) + ".")
        self.logdispatch.log(LogPriority.DEBUG, "pRuleSuccess = " +
                             str(pRuleSuccess) + ".")
        success = True
        return success

    def checkFixForRule(self, pRuleSuccess):
        '''
        check on whether fix was correct
        @param self: essential if you override this definition
        @param pRuleSuccess: did report run successfully
        @return: boolean - If successful True; If failure False
        @author: Breen Malmberg
        '''
        self.logdispatch.log(LogPriority.DEBUG, "pRuleSuccess = " +
                             str(pRuleSuccess) + ".")
        success = True
        return success

    def checkUndoForRule(self, pRuleSuccess):
        '''
        check on whether undo was correct
        @param self: essential if you override this definition
        @param pRuleSuccess: did report run successfully
        @return: boolean - If successful True; If failure False
        @author: Breen Malmberg
        '''
        self.logdispatch.log(LogPriority.DEBUG, "pRuleSuccess = " +
                             str(pRuleSuccess) + ".")
        success = True
        return success

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
