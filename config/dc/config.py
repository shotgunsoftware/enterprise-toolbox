'''
Configure base environments
images folder = /usr/tmp
base target folder = /opt/shotgun
docker command = docker-compose
docker-compose.yml
media volum
'''
import os
import base

class Conf(base.Base):
    '''inherite from base'''
    gdata = ""
    p = ""

    SElinuxConfig="/etc/selinux/config"
    SEconfig1="SELINUX=enforcing"
    SEconfig2="SELINUX=permissive"
    SEconfig3="SELINUX=disabled"

    def __init__(self, gd, pub):
        self.gdata = gd
        self.p = pub
        self.p.printhead('\nPreparing to install Shotgun Enterprise Docker Version ...')

    def firewall(self):
        '''Disable firewall'''
        self.p.printhead('Disabling firewalld ...')
        cmd='systemctl disable firewalld'
        self.popencmd(cmd)
        cmd='systemctl stop firewalld'
        self.popencmd(cmd)
        self.p.printsuc('Firewalld is disabled.')

    def sysselinux(self):
        '''setenforce'''
        cmd="getenforce"
        result=self.popencmd(cmd)
        if not result == "Disalbed" or not result == 'disabled':
            cmd = "sed -i \"s/%s/%s/g\" %s" % (self.SEconfig1, self.SEconfig3, self.SElinuxConfig)
            self.popencmd(cmd)
            cmd = "sed -i \"s/%s/%s/g\" %s" % (self.SEconfig2, self.SEconfig3, self.SElinuxConfig)
            self.popencmd(cmd)
            cmd = 'setenforce 0'
            self.popencmd(cmd)
        
        self.p.printsuc("Selinux is disabled.")
            
    def sguser(self):
        '''Add shotgun user'''
        m='Add shotgun user'
        self.p.printhead(m)
        m='Check if shotgun user existed.'
        self.p.printhead(m)
        cmd = "getent passwd shotgun"
        result = self.popencmd(cmd)
        if result == "":
            self.p.printhead('User shotgun doesn\'t exist. Creating ...')
            cmd = "useradd -m -s /bin/bash -U shotgun -u 2000 "
            self.popencmd(cmd)
            cmd="echo \"shotgun:%s\" | chpasswd" % ('password')
            self.popencmd(cmd)
            self.p.printsuc('User shotgun added. Default password is \'password\'')
        else:
            self.p.printsuc('User shotgun existed.')

    def sgsudo(self):
        '''Add sudoers'''
        self.p.printhead('Add shotgun as sudoer.')
        if not self.p.validate_file('/etc/sudoers.d/shotgun'):
            self.p.printhead('shotgun isn\'t sudoer.\n Add shotgun as sudoer.')
            cmd = "echo \"%s ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/%s" % (self.gdata.shotgun_user, self.gdata.shotgun_user)
            self.popencmd(cmd)
        else:
            self.p.printhead('shotgun is sudoer.')
    
    def createshotgunuser(self):
        self.sguser()

    def systemsecurity(self):
        self.sgsudo()
        self.sysselinux()
        self.firewall()

    def setuppgsql(self):
        cmd = "bash postgresql_bootstrap_centos7.sh"
        self.gencmd(cmd)
         
    def tempfolder(self):
        prompt ='All your docker images are in folder (%s): ' % (self.gdata.getTempfolder())
        temp = self.p.getinput(prompt)
        if temp != "" :
            self.gdata.setTempfolder(temp+"/")
        
        if self.p.validate_folder(self.gdata.getTempfolder()) :
            self.p.printsuc('Folder %s is valid.' % (self.gdata.getTempfolder()))
            self.p.printsuc('Please make sure all your docker images are in %s.' % (self.gdata.getTempfolder()))
        else:
            self.p.printfail('The folder %s is invalid!' % (self.gdata.getTempfolder()))
            self.p.exit(0)