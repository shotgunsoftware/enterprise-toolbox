'''Install Application'''
import base
import re
import versions

class TranscoderService(base.Base):
    '''inherite from base'''
    gdata = ""
    p = ""
    
    server_version = versions.server_supported[0]
    server_gzfile = "shotgun-docker-se-transcoder-server-%s.tar.gz" % (server_version)
    server_tarfile = "shotgun-transcoder-server.%s.tar" % (server_version)
    server_img="shotgun-transcoder-server"
    TRSDIR="/opt/shotgun/se/transcoder-server/"
    TRSSTR="%TCSERVER_VERSION%"
    SVRSTAT="Up      0.0.0.0:80->80/tcp"

    worker_version = versions.worker_supported[0]
    worker_gzfile = "shotgun-docker-se-transcoder-worker-%s.tar.gz" % (worker_version)
    worker_tarfile = "shotgun-transcoder-worker.%s.tar" % (worker_version)
    worker_img="shotgun-transcoder-worker"
    TRWDIR="/opt/shotgun/se/transcoder-worker/"
    TRWSTR="%TCWORKER_VERSION%"
    WORKERSTAT="Up      0.0.0.0:80->80/tcp"

    home = "se/"
    homefull = ""
    production_yml_home = ""
    staging_yml_home = ""

    def __init__(self, gd, pub):
        self.gdata = gd
        self.p = pub
        
        self.homefull = self.gdata.shotgun_home + self.home
        self.production_yml_home = self.homefull + 'production/'
        self.staging_yml_home = self.homefull + 'staging/'
        self.p.printhead('Preparing to install %s ...' %(self.__class__.__name__))
    
    def getsvrfile(self):
        return self.gdata.getTempfolder() + self.server_gzfile

    def getwkrfile(self):
        return self.gdata.getTempfolder() + self.worker_gzfile

    def setWorkerVersion(self):
        version = self.getappversion(self.gdata.temp_folder, "shotgun-docker-se-transcoder-worker", versions.worker_supported)
        if version == "":
            self.p.printfail('Can\'t find shotgun application software in the folder. Please make sure you have copy the file in the folder')
            prompt ='%s Version (%s): ' % ('transcoder worker', versions.worker_supported[0])
            ver = self.p.getinput(prompt)
            if ver == "":
                ver = versions.worker_supported[0]
        else:
            prompt ='%s Version: %s' % ('transcoder worker', version)
            ver = self.p.getinput(prompt)
            if ver == "":
                ver = version
            
        if self.p.validate_version(ver, versions.worker_supported):
            self.p.printsuc('%s Version %s is validated' % ('transcoder worker', ver))
            versions.worker_version = ver
        else:
            self.p.printfail('Inputed %s version %s is not supported!' % ('transcoder worker', ver))
            self.p.exit(0)

    def getWorkerVersion(self):
        return self.worker_version

    def setServerVersion(self):
        version = self.getappversion(self.gdata.temp_folder, "shotgun-docker-se-transcoder-server", versions.server_supported)
        if version == "":
            self.p.printfail('Can\'t find shotgun application software in the folder. Please make sure you have copy the file in the folder')
            prompt ='%s Version (%s): ' % ('transcoder server', versions.server_supported[0])
            ver = self.p.getinput(prompt)
            if ver == "":
                ver = versions.server_supported[0]
        else:
            prompt ='%s Version: %s' % ('transcoder server', version)
            ver = self.p.getinput(prompt)
            if ver == "":
                ver = version

        if self.p.validate_version(ver, versions.server_supported):
            self.p.printsuc('%s Version %s is validated' % ('transcoder server', ver))
            self.server_version = ver
        else:
            self.p.printfail('Inputed %s version %s is not supported!' % ('transcoder server', ver))
            self.p.exit(0)

    def getServerVersion(self):
        return self.server_version

    def setupServer(self):
        self.setServerVersion()
        if self.p.validate_file(self.getsvrfile()):
            self.p.printsuc('%s file %s existed.' % ('transcoder server', self.getsvrfile()))   

        '''Untar app tar.gz package'''
        untared = True
        if not self.p.validate_folder(self.TRSDIR):
            untared = False    
        else:
            if not self.p.validate_file(self.TRSDIR + self.server_tarfile):
                untared = False

        if not untared:   
            self.untar(self.getsvrfile(), self.gdata.opt)
            self.chown('shotgun', self.homefull)
        else:
            self.p.printwarn('%s file existed. Ignored!' % (self.TRSDIR + self.server_tarfile))

        SERVERIMGSTAT="%s   %s" % (self.server_img, self.getServerVersion())
        if not self.validate_loaded('Transcoder Server', SERVERIMGSTAT):
            self.dcload(self.TRSDIR, self.server_tarfile) 

    def setupWorker(self):
        self.setWorkerVersion()
        if self.p.validate_file(self.getwkrfile()):
            self.p.printsuc('%s file %s existed.' % ('transcoder server', self.getwkrfile()))   

        '''Untar app tar.gz package'''
        untared = True
        if not self.p.validate_folder(self.TRWDIR):
            untared = False    
        else:
            if not self.p.validate_file(self.TRWDIR + self.worker_tarfile):
                untared = False

        if not untared:   
            self.untar(self.getwkrfile(), self.gdata.opt)
            self.chown('shotgun', self.TRWDIR)
        else:
            self.p.printwarn('%s file existed. Ignored!' % (self.TRWDIR + self.worker_tarfile)) 

        WORKERIMGSTAT="%s   %s" % (self.worker_img,self.getWorkerVersion())
        if not self.validate_loaded('Transcoder Worker', WORKERIMGSTAT):
            self.dcload(self.TRWDIR, self.worker_tarfile) 

    def editproductionyml(self):
        '''Edit transcoder parts in yml'''
        siteype="production"
        yml = self.production_yml_home + self.gdata.yml
        prompt ='Do you want to configure transcoder service on %s site? (Y/n): ' % ('production')
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            '''Change version'''
            self.p.printhead('Change transcoder version in docker-compose.yml')
            self.ymlreplace(self.TRSSTR, self.getServerVersion(), yml)
            self.ymlreplace(self.TRWSTR, self.getWorkerVersion(), yml)

            SL1 = self.getlinenum('#  transcoderserver:', yml)
            if not SL1 == "":
                self.p.printhead('Edit docker-compose.yml')
                SL2 = int(SL1) + 22
                cmd = 'sed -i "%s,%s s/^.#//g" %s' % (str(SL1), str(SL2), yml)
                self.gencmd(cmd)
            else:
                self.p.printhead('docker-compose.yml was edited.')
        else:
            self.p.printwarn('Ignored transcoder service configuration.')

    def editstagingyml(self):
        '''Edit transcoder parts in yml'''
        siteype="staging"
        yml = self.staging_yml_home + self.gdata.yml
        prompt ='Do you want to configure transcoder service on %s site? (Y/n): ' % ('staging')
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            '''Change version'''
            self.p.printhead('Change transcoder version in docker-compose.yml')
            self.ymlreplace(self.TRSSTR, self.getServerVersion(), yml)
            self.ymlreplace(self.TRWSTR, self.getWorkerVersion(), yml)

            SL1 = self.getlinenum('#  transcoderserver:', yml)
            if not SL1 == "":
                self.p.printhead('Edit docker-compose.yml')
                SL2 = int(SL1) + 22
                cmd = 'sed -i "%s,%s s/^.#//g" %s' % (str(SL1), str(SL2), yml)
                self.gencmd(cmd)
            else:
                self.p.printhead('docker-compose.yml was edited.')
        else:
            self.p.printwarn('Ignored transcoder service configuration.')

    def loadimages(self):
        self.setupServer()
        self.setupWorker()


