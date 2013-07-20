#!/usr/bin/python
import os
import time

from eucaops import Eucaops
from eutester.eutestcase import EutesterTestCase
from eutester.machine import Machine


class SOSreport(EutesterTestCase):
    def __init__(self):
        self.setuptestcase()
        self.setup_parser()
        self.start_time = int(time.time())
        self.parser.add_argument("--ticket-number", default=self.start_time)
        self.parser.add_argument("--remote-dir", default="/root/")
        self.parser.add_argument("--local-dir", default=os.getcwd())
        self.parser.add_argument("--package-url", default="http://mongo.beldurnik.com/RPMS/eucalyptus-sos-plugins-0.1.1-0.el6.noarch.rpm")
        self.get_args()
        self.remote_dir = self.args.remote_dir + "/euca-sosreport-" + self.args.ticket_number + "/"
        # Setup basic eutester object
        self.tester = Eucaops( config_file=self.args.config,password=self.args.password)

    def clean_method(self):
        pass

    def Install(self):
        """
        This is where the test description goes
        """
        for machine in self.tester.get_component_machines():
            assert isinstance(machine, Machine)
            machine.install("sos")
            machine.sys("yum install -y " + self.args.package_url)

    def Run(self):
        for machine in self.tester.get_component_machines():
            assert isinstance(machine, Machine)
            machine.sys("mkdir -p " + self.args.remote_dir)
            machine.sys("sosreport --batch --tmp-dir " + self.args.remote_dir + " --ticket-number " + str(self.args.ticket_number),code=0)

    def Download(self):
        for machine in self.tester.get_component_machines():
            assert isinstance(machine, Machine)
            remote_tarball_path = machine.sys("ls -1 " + self.args.remote_dir + "*" + str(self.args.ticket_number) + "*", code=0)[0]
            tarball = remote_tarball_path.split("/")[-1]
            local_tarball_path = self.args.local_dir + '/' + tarball
            self.tester.debug("Downloading file to: " + local_tarball_path)
            machine.sftp.get(remote_tarball_path, local_tarball_path)

    def RunAll(self):
        self.Install()
        self.Run()
        self.Download()

if __name__ == "__main__":
    testcase = SOSreport()
    ### Use the list of tests passed from config/command line to determine what subset of tests to run
    ### or use a predefined list
    list = testcase.args.tests or ["RunAll"]

    ### Convert test suite methods to EutesterUnitTest objects
    unit_list = [ ]
    for test in list:
        unit_list.append( testcase.create_testunit_by_name(test) )

    ### Run the EutesterUnitTest objects
    result = testcase.run_test_case_list(unit_list,clean_on_exit=True)
    exit(result)