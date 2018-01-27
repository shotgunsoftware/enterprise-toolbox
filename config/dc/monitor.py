'''Install Basic Monitor'''
import os
import base

class Monitor():
    gd = base.global_data()
    p = base.pub()
    b = base.Base()
    monitor_folder = "../../basic_monitoring"
    monitor_folder1 = "../basic_monitoring"
    def cmd(self,cmd):
        print '\nExcuting %s' % (cmd)
        result=os.system(cmd)
        print 'Finished.'
        return result
        
    def createmonitorfolder(self):
        cmd = "mkdir -p /var/log/shotgun_monitoring && chown %s:%s /var/log/shotgun_monitoring" % (gd.shotgun_user, gd.shotgun_user)
        self.cmd(cmd)
        
    def monitor(self, server_type, monitor_type):
        cmd = "cp %s/scripts/%s /usr/local/bin && chmod +x /usr/local/bin/%s" % (self.monitor_folder1, monitor_type, monitor_type)
        self.cmd(cmd)
        cmd = "cp %s/crons/%s /etc/cron.d/%s" % (self.monitor_folder1,server_type,server_type )
        self.cmd(cmd)
        cmd = "cp %s/logrotates/%s /etc/logrotate.d/%s" % (self.monitor_folder1, server_type, server_type)
        self.cmd(cmd)

    def setup(self):
        if not self.p.validate_folder(self.monitor_folder):
            self.monitor("shotgun_app_server", "shotgun_monitor_app_server")
            self.monitor("shotgun_db_server", "shotgun_monitor_db_server")
            self.p.replacefilecontent('shotgun_user', 'shotgun_admin', '/etc/cron.d/shotgun_db_server')
            self.p.printsuc('\nPlease find your shotgun APP server log at /var/log/shotgun_monitoring/app_server.log')
            self.p.printsuc('\nPlease find your shotgun DB server log at /var/log/shotgun_monitoring/db_server.log\n')
        else:
            self.p.printfail("Basic Monitor folder doesn't exist. Please copy the folder at same level with config.")