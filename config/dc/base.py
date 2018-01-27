'''Define basic fucntion'''
import os, sys
import tarfile
import commands,re,socket

class global_data(object):
    '''Define global data'''
    temp_folder = '/usr/tmp/'
    opt='/opt/'
    shotgun_home = opt + 'shotgun/'
    dc_cmd = 'docker-compose'
    yml = 'docker-compose.yml'
    media_volume="./media"

    SITE_URL="sg.autodesk.com"
    URL_IN_YML="shotgun.mystudio.test"
    VOLUMES="" #Have to use excape '\' to represent /. Exapmle '\/'
    ENABLEEMAILER=1 #1=uncomment emailnotifier 0=don't change
    ENABLETRANSCODER=1 #1=uncomment transcoder 0=don't change
    ENABLEPROXY=0 #1=uncomment proxy 0=don't change
    RESETADMINPW=1 #Please also enable INSSHOTGUNUID variable
    INSSHOTGUNUID=1

    SHOTGUN_ADMIN_PW="password"
    SHOTGUN_USER_ID="2000" #By default

    shotgun_user="shotgun"

    hostip="db"
    POSTGRES_PASSWORD=""

    def setTempfolder(self, folder):
        self.temp_folder = folder

    def getTempfolder(self):
        return self.temp_folder

    def setMedia(self, folder):
        self.media_volume = folder

    def getMedia(self):
        return self.media_volume

    def setSGUser(self, username):
        self.shotgun_user = username

    def setSGUser(self):
        return self.shotgun_user

class pub(object):
    '''Define shared functions'''  
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    DCUP="docker-compose up -d app"
    DCSTOP="sudo docker-compose stop app"

    def validate_folder(self, folder):
        '''Test if the folder existed'''
        print 'Validating folder %s ...' % (folder)
        return os.path.isdir(folder)

    def validate_version(self, ver, verlist):
        if ver in verlist:
            return True
        else:
            return False

    def validate_file(self, filename):
        '''Validate if the package installed'''
        print 'Validating file %s ...' % (filename)
        return os.path.isfile(filename)

    def getinput(self, prompt):
        return raw_input(self.BOLD + prompt + self.ENDC)

    def printwarn(self, m):
        print self.WARNING + m + self.ENDC

    def printfail(self, m):
        print self.FAIL + m + self.ENDC

    def printsuc(self, m):
        print self.OKGREEN + m + self.ENDC

    def printhead(self, m):
        print self.OKBLUE + m + self.ENDC

    def printend(self, m):
        print self.BOLD + m + self.ENDC
        
    def exit(self, stat):
        if stat == 1:
            self.printsuc('All done!')
        else:
            self.printfail('System terminated!')
        sys.exit(0)

class Base(object):
    '''Basic setup function for all packages'''
    version_app="7.6.2.0"
    version_trs_worker="6.0.4"
    version_trs_server="9.0.4"

    def __init__(self):
        '''Initiate data. Package path, version etc'''
        class_name = self.__class__.__name__
        print class_name, "init"
    
    def chown(self, username, folder):
        '''chown'''
        print '\nChange owner %s ...' % (folder)
        cmd = 'chown -R %s:%s %s' % (username, username, folder)
        print cmd
        self.gencmd(cmd)

    def untar(self, f_tgz, f_target):
        '''Untar package'''
        print '\nExtract %s to %s ...' % (f_tgz, f_target)
        cmd = 'tar xvfz %s -C %s' % (f_tgz, f_target)
        self.gencmd(cmd)

    def gencmd(self,cmd):
        print '\nExcuting %s' % (cmd)
        result=os.system(cmd)
        print 'Finished.'
        return result

    def popencmd(self,cmd):
        print '\nExcuting %s' % (cmd)
        t=os.popen(cmd)
        l = t.readline()
        print 'Finished.'
        l=l.rstrip()
        return l

    def validate_yml(self):
        '''validate yml'''
        print 'validate " + self.dcfile + " yml part'
        
    def modify_yml(self):
        '''modify yml file'''
        print 'modify " + self.dcfile + " yum file'

    def validate_running(self, app, pkgpath, stat):
        '''validate if docker package loaded'''
        print 'validate if %s running ...' % (app)
        cmd = "cd %s && docker-compose ps | grep \"%s\"" % (pkgpath, stat)
        print cmd
        t=os.popen(cmd)
        if t.read() == "":
            print 'Not running.'
            return False
        else:
            print 'Running.'
            return True
   
    def validate_loaded(self, app, stat):
        '''Validate if dc package loaded'''
        print 'validate if %s loaded ...' % (app)
        cmd = "docker images| grep \"%s\"" % (stat)
        print cmd
        t=os.popen(cmd)
        if t.read() == "":
            print 'Not loaded.'
            return False
        else:
            print 'Loaded.'
            return True

    def dcload(self, pkgpath, pkg):
        '''load dc package'''
        print 'loading %s  package' % (pkg)
        cmd = "cd %s && docker load < %s" % (pkgpath, pkg)
        self.gencmd(cmd)

    def dcup(self, pkgpath, pkg):
        '''start up server'''
        print 'Starting %s server' % pkg
        cmd = 'cd %s && docker-compose up -d' % (pkgpath)
        print cmd
        self.gencmd(cmd)

    def ymlreplace(self, oldstr, newstr, yml):
        cmd="sed -i \"s/%s/%s/g\" %s" % (oldstr, newstr, yml)
        self.gencmd(cmd)
        print cmd, ' excuted.'

    def commentline(self, line1, line2, yml):
        cmd = "sed -i \"%s,%s s/^/#/g\" %s" % (str(line1), str(line2), yml)
        self.gencmd(cmd)
        print cmd, ' excuted.'
    
    def getlinenum(self, linestr, yml):
        cmd="sed -n \"/%s/=\" %s" % (linestr, yml);
        linunum = self.popencmd(cmd)
        return linunum

    def getipv4(self):
        '''will return [('127.0.0.1', 8), ('10.0.2.15', 24), ('172.19.0.1', 16), ('172.17.0.1', 16), ('172.18.0.1', 16)]'''
        iplines=(line.strip() for line in commands.getoutput("ip address show").split('\n'))
        addresses1=reduce(lambda a,v:a+v,(re.findall(r"inet ([\d.]+/\d+)",line)+re.findall(r"inet6 ([\:\da-f]+/\d+)",line) for line in iplines))
        ipv4s=[(ip,int(subnet)) for ip,subnet in (addr.split('/') for addr in addresses1 if '.' in addr)]
        print ipv4s
        return ipv4s

    def getsubnet(self, ip):
        sub = ""
        print "Find %s subnet" % (ip[0])
        if not ip[0].split('.', 1)[0] == "127":
            print "Processing ip %s" % (ip[0])
            i=ip[0].split('.')
            print i
            sub=i[0]+'.'+i[1]+'.'+i[2]+'.0/' + str(ip[1])
            print sub
        else:
            print "Ignore ip %s" % (ip[0])
        return sub
    
    def gethostip(self):
        ips=self.getipv4()
        hosts=[]
        localip = ""
        for ip in ips: 
            if not ip[0].split('.', 1)[0] == "127" and not ip[0].split('.', 1)[0] == "172":
                hosts.append(ip[0])
        if len(hosts) > 0:
            localip = hosts[0]
        else:
            localip = "127.0.0.1"
        print 'Find host ip address'
        return localip

    def setup(self):
        pass
