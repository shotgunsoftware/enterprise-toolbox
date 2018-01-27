'''Install Application'''
import base
import re
import versions

class App(base.Base):
    '''inherite from base'''
    gdata = ""
    p = ""

    version = versions.app_supported[0]
    gzfile = "shotgun-docker-se-%s.tar.gz" % (version)
    tarfile = 'shotgun-app.%s.tar' % (version)
    img = "shotgun-app"
    home = "se/"
    homefull = ""
    production_yml_home = ""
    staging_yml_home = ""
    
    STAT="Up      0.0.0.0:80->80/tcp"

    def __init__(self, gd, pub):
        self.gdata = gd
        self.p = pub
        self.homefull = self.gdata.shotgun_home + self.home
        self.production_yml_home = self.homefull + 'production/'
        self.staging_yml_home = self.homefull + 'staging/'

        self.p.printhead('Preparing to install %s ...' %(self.__class__.__name__))

    def setVersion(self):
        prompt ='%s Version (%s): ' % (self.__class__.__name__, versions.app_supported[0])
        ver = self.p.getinput(prompt)
        if ver == "":
            ver = versions.app_supported[0]

        if self.p.validate_version(ver, versions.app_supported):
            self.p.printsuc('%s Version %s is validated' % (self.__class__.__name__, ver))
            self.version = ver
        else:
            self.p.printfail('Inputed %s version %s is not supported!' % (self.__class__.__name__, ver))
            self.p.exit(0)

    def getVersion(self):
        return self.version
    
    def getappfile(self):
        return self.gdata.getTempfolder() + self.gzfile

    def getsiteurl(self, site):
        '''get site url, db server address'''
        prompt ='Please input your %s site url? (%s): ' % (site,self.gdata.SITE_URL)
        ans = self.p.getinput(prompt)
        if not ans == "":
            self.gdata.SITE_URL = ans

    def startover(self, sitetype, yml):
        '''Start over'''
        prompt ='Do you want to start from a fresh %s on %s site? (Y/n): ' % (self.gdata.yml, sitetype)
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            ymlold = self.homefull+'example/' + self.gdata.yml
            cmd='cp  %s %s' % (ymlold, yml)
            self.gencmd(cmd)

    def setupsite(self, sitetype, ymlhome, yml):
        '''Setup production or staging'''
        prompt ='Do you want to configure %s site? (Y/n): ' % (sitetype)
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            self.getsiteurl(sitetype)
            if not self.p.validate_folder(ymlhome):
                cmd='cp -r %s %s' % (self.homefull+'example', ymlhome)
                self.gencmd(cmd)
            else:
                msg ='%s folder exist.' % (sitetype)
                self.p.printfail(msg)
            
            self.startover(sitetype,yml)
            
            '''Edit docker-compose yml'''
            if not self.p.validate_file(yml):
                self.p.printfail('%s doesn\'t exist. Please make sure app package is untar and loaded.' % (yml))
                self.p.exit(0)
            else:
                self.p.printhead("Change Shotgun Site URL to %s." % (self.gdata.SITE_URL))
                self.ymlreplace(self.gdata.URL_IN_YML, self.gdata.SITE_URL,yml)

            if sitetype == "production":
                self.setupmedia(yml)
                self.setupdb()
                self.setupemailer(yml)
                self.setupproxy(yml)
        else:
            self.p.printwarn('Ignored configure %s.' % (sitetype))

    def setupmedia(self, yml):
        '''Setup media'''
        prompt ='Do you want to configure %s site? (Y/n): ' % ('media folder')
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            prompt ='Please input your media folder (./media):'
            ans = self.p.getinput(prompt)
            if not ans == '' and not ans == './media':
                '''Edit docker-compose yml'''
                if not self.p.validate_file(yml):
                    self.p.printfail('%s doesn\'t exist' % (yml))
                    self.p.exit(0)
                else:
                    self.p.printhead("Change media folder to %s." % (self.gdata.SITE_URL))
                    OVOL=".\/media:\/media"
                    NVOL="%s:\/media" % (ans.replace('/','\/'))
                    self.ymlreplace(OVOL, NVOL,yml)

    def setupemailer(self, yml):
        '''Setup email'''
        prompt ='Do you want to configure %s? (y/N): ' % ('emailnotification')
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y':
            EMLN1 = self.getlinenum('emailnotifier:', yml)
            EMLN2 = int(EMLN1)+13
            cmd="sed -i \"%s,%s s/^..#/ /g\" %s" % (str(EMLN1), str(EMLN2), yml)
            self.gencmd(cmd)
            
    def setupproxy(self, yml):
        '''Setup proxy'''
        prompt ='Do you want to configure %s? (y/N): ' % ('proxy')
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y':
            LN1 = self.getlinenum('proxy:', yml)
            LN2 = int(LN1)+11
            cmd="sed -i \"%s,%s s/^..#/ /g\" %s" % (str(LN1), str(LN2), yml)
            self.gencmd(cmd)
            
    def setupdb(self):
        '''Setup standalone database'''
        yml = self.production_yml_home + self.gdata.yml
        prompt ='Do you want to configure %s site? (Y/n): ' % ('standalone database')
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            prompt ='Is your database server running on the same server? (Y/n):'
            ans = self.p.getinput(prompt)
            if ans == 'Y' or ans == 'y' or ans == "":
                self.samedbserver()
            else:
                self.seperatedatabaseserver()
            self.modifydatabaseyml(yml)

    def samedbserver(self):
        '''Database is on the same shotgun server'''
        self.gdata.hostip = self.gethostip()
        PGSQLFILE="/var/lib/pgsql/9.6/data/pg_hba.conf"
        if self.p.validate_file(PGSQLFILE):
            self.p.printhead("Add Host IP and Docker Container IP to pg_hba.conf")
            ips = self.getipv4()
            ips.append(['172.17.0.1', 16])
            ips.append(['172.18.0.1', 16])
            print ips
            for ip in ips:
                i=self.getsubnet(ip)
                if not i == "":
                    sedstr=i.replace("/","\/")
                    echostr="host  all all %s md5" % (i)
                    pgline=self.getlinenum(sedstr, PGSQLFILE)
                    if pgline == "" :
                        cmd = "echo \"%s\" >> %s" % (echostr, PGSQLFILE)
                        self.gencmd(cmd)

            cmd = "systemctl restart postgresql-9.6"
            self.gencmd(cmd)
            cmd="sed -n 's/^.*shotgun://p' /root/.pgpass"
            self.gdata.POSTGRES_PASSWORD=self.popencmd(cmd)
        
    def seperatedatabaseserver(self):
        '''Get database server ip'''
        prompt ='Please input your database host (ip address or hostname):'
        self.gdata.hostip = self.p.getinput(prompt)
                    
        if self.gdata.hostip == "" or self.gdata.hostip == "db":
            self.p.printfail('database host is localhost. Ignored.')
            self.p.exit(0)

            prompt ='Please input your database password:'
            self.gdata.POSTGRES_PASSWORD = self.p.getinput(prompt)
            if self.gdata.POSTGRES_PASSWORD == "":
                self.p.printfail('Password is invalid.')
                self.p.exit(0)
        
    def modifydatabaseyml(self, yml):
        '''Edit docker-compose yml'''
        hostip = self.gdata.hostip
        POSTGRES_PASSWORD = self.gdata.POSTGRES_PASSWORD
        if not self.p.validate_file(yml):
            self.p.printfail('%s doesn\'t exist' % (yml))
            self.p.exit(0)
        else:
            self.p.printhead("Change DB host to %s." % (hostip))
            PGSQL="POSTGRES_HOST: db"
            PGHOST="POSTGRES_HOST: %s" % (hostip)
            self.ymlreplace(PGSQL, PGHOST, yml)

            DBOPHOST="PGHOST: db"
            DBOPHOSTNEW="PGHOST: %s" % (hostip)
            self.ymlreplace(DBOPHOST, DBOPHOSTNEW, yml)

            '''Modify DB'''
            DBOPPW="#POSTGRES_PASSWORD: dummy"
            DBOPPWNEW="POSTGRES_PASSWORD: %s" % (POSTGRES_PASSWORD)
            self.ymlreplace(DBOPPW, DBOPPWNEW, yml)

            '''Modify DBOPS'''
            DBOPPW="#PGPASSWORD: dummy"
            DBOPPWNEW="PGPASSWORD: %s" % (POSTGRES_PASSWORD)
            self.ymlreplace(DBOPPW, DBOPPWNEW, yml)

            '''Comment out db section'''
            DBLN1 = self.getlinenum('db:', yml)
            DBLN2= int(DBLN1) + 7
            self.commentline(DBLN1, DBLN2, yml)

            '''Remove dependency'''
            CDBLN1 = self.getlinenum('#- db', yml)
            if CDBLN1 == "" :
                self.ymlreplace('- db','#- db', yml)

    def loadappimage(self):
        self.setVersion()
        if self.p.validate_file(self.getappfile()):
            self.p.printsuc('%s file %s existed.' % (self.__class__.__name__, self.getappfile()))   

        '''Untar app tar.gz package'''
        untared = True
        if not self.p.validate_folder(self.homefull):
            untared = False    
        else:
            if not self.p.validate_file(self.homefull + self.tarfile):
                untared = False

        if not untared:   
            self.untar(self.getappfile(), self.gdata.opt)
            self.chown('shotgun', self.homefull)
        else:
            self.p.printwarn('%s file existed. Ignored!' % (self.homefull + self.tarfile))   
        
        IMGSTAT="%s                 %s" % (self.img, self.getVersion())
        if not self.validate_loaded(self.__class__.__name__, IMGSTAT):
            self.dcload(self.homefull, self.tarfile)

    def setupproduction(self):
        '''Setup Production'''
        yml = self.production_yml_home + self.gdata.yml
        sitetype ='production'
        self.setupsite(sitetype, self.production_yml_home, yml)
    
    def setupstaging(self):
        '''Setup Staging'''
        yml = self.staging_yml_home + self.gdata.yml
        sitetype ='staging'
        self.setupsite(sitetype, self.staging_yml_home, yml)
    
    def startserver(self):
        '''start production server'''
        if self.p.validate_folder(self.production_yml_home): 
            if self.p.validate_file(self.production_yml_home + self.gdata.yml):
                IMGSTAT="%s                 %s" % (self.img, self.getVersion())
                if self.validate_loaded(self.__class__.__name__, IMGSTAT):
                    if not self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT):
                        self.dcup(self.production_yml_home, 'production')
                    else:
                        self.p.printfail('shotgun production server is running')
                else:
                    self.p.printfail('shotgun image isn\'t loaded. Can\'t start')
            else:
                self.p.printfail('Production server isn\'t configured. Can\'t start')
        else:
            self.p.printfail('Production server isn\'t configured. Can\'t start')

    def setpassword(self):
        if self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT):
            self.p.printhead('Change shotgun_admin password to \'%s\'' % (self.gdata.SHOTGUN_ADMIN_PW))
            cmd = 'cd %s && docker-compose run --rm app rake admin:reset_shotgun_admin_password[%s]' % (self.production_yml_home, self.gdata.SHOTGUN_ADMIN_PW)
            self.gencmd(cmd)
        else:
            self.p.printfail('shotgun production server is not running, can\'t reset password')
