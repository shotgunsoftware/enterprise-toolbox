'''Install SEC'''
import base
import versions

class SEC(base.Base):
    '''inherite from base'''
    gdata = ""
    p = ""

    version = versions.sec_supported[0]
    gzfile = "shotgun-docker-sec-%s.tar.gz" % (version)
    tarfile = 'shotgun-docker-sec-%s.tar' % (version)
    img = "shotgun-docker-sec"
    home = "sec/"
    homefull = ""

    SECRUN="/etc/systemd/system/secstart.service"
    SRC="dc/secstart.service"
    SECSTAT="Up      0.0.0.0:8080->8080/tcp"
    IMGSTAT="%s:%s" % (img,version)

    def __init__(self, gd, pub):
        self.gdata = gd
        self.p = pub
        self.homefull = self.gdata.shotgun_home + self.home
        self.p.printhead('Preparing to install %s ...' %(self.__class__.__name__))

    def setVersion(self):
        version = self.getappversion(self.gdata.temp_folder, "shotgun-docker-sec-", versions.sec_supported)
        if version == "":
            self.p.printfail('Can\'t find shotgun application software in the folder. Please make sure you have copy the file in the folder')
            prompt ='%s Version (%s): ' % (self.__class__.__name__, versions.sec_supported[0])
            ver = self.p.getinput(prompt)
            if ver == "":
                ver = versions.sec_supported[0]
        else:
            prompt ='%s Version: %s ' % (self.__class__.__name__, version)
            ver = self.p.getinput(prompt)
            if ver == "":
                ver = version

        if self.p.validate_version(ver, versions.sec_supported):
            self.p.printsuc('%s Version %s is validated' % (self.__class__.__name__, ver))
            self.version = ver
        else:
            self.p.printfail('Inputed %s version %s is not supported!' % (self.__class__.__name__, ver))
            self.p.exit(0)

    def getVersion(self):
        return self.version
    
    def getsecfile(self):
        return self.gdata.getTempfolder() + self.gzfile

    def loadimage(self):
        self.setVersion()
        if self.p.validate_file(self.getsecfile()):
            self.p.printsuc('%s file %s existed.' % (self.__class__.__name__, self.getsecfile()))   

        '''Untar sec tar.gz package'''
        untared = True
        if not self.p.validate_folder(self.homefull):
            untared = False    
        else:
            if not self.p.validate_file(self.homefull + self.tarfile):
                untared = False

        if not untared:   
            self.untar(self.getsecfile(), self.gdata.opt)
            self.chown('shotgun', self.homefull)
        else:
            self.p.printwarn('%s file existed. Ignored!' % (self.homefull + self.tarfile))   
        
        '''Setup sec up when system startup'''
        if not self.p.validate_file(self.SECRUN):
            cmd = 'cp %s %s' % (self.SRC, self.SECRUN)
            self.gencmd(cmd)

        cmd = 'systemctl enable secstart'
        self.gencmd(cmd)

    def startup(self):
        '''Start sec'''
        prompt ='Do you want to start (%s)? (Y/n): ' % (self.__class__.__name__)
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            IMGSTAT="%s:%s" % (self.img, self.getVersion())
            if not self.validate_loaded(self.__class__.__name__, self.IMGSTAT):
                self.dcload(self.homefull, self.tarfile)
            if not self.validate_running(self.__class__.__name__, self.homefull, self.SECSTAT):
                cmd = 'systemctl start secstart'
                self.gencmd(cmd)
                self.p.printsuc("Access Shotgun http://127.0.0.1:8080")
            
    def stopserver(self):
        '''start sec server'''
        if self.p.validate_folder(self.homefull): 
            IMGSTAT="%s          %s" % (self.img, self.getVersion())
            if self.validate_loaded(self.__class__.__name__, IMGSTAT):
                self.dcstop(self.homefull, 'sec')
            else:
                self.p.printfail('shotgun sec image isn\'t loaded. Can\'t stop')
        else:
            self.p.printfail('SEC server isn\'t configured. Can\'t stop')
            
        