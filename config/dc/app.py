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
    
    STAT="sg_r ...   Up      0.0.0.0:80->80/tcp"
    STAT1="Up      0.0.0.0:8888->80/tcp"
    STAT2="Up      0.0.0.0:9999->80/tcp"

    def __init__(self, gd, pub):
        self.gdata = gd
        self.p = pub
        self.homefull = self.gdata.shotgun_home + self.home
        self.production_yml_home = self.homefull + 'production/'
        self.staging_yml_home = self.homefull + 'staging/'

        self.p.printhead('Preparing to install %s ...' %(self.__class__.__name__))

    def setVersion(self):
        version = self.getappversion(self.gdata.temp_folder, "shotgun-docker-se-", versions.app_supported[0])
    
        if version == "":
            self.p.printfail('Can\'t find shotgun application software in the folder. Please make sure you have copy the file in the folder')
            prompt ='%s Version (%s): ' % (self.__class__.__name__, versions.app_supported[0])
            ver = self.p.getinput(prompt)
            if ver == "":
               ver = versions.app_supported[0]
        else:
            prompt ='%s Version (%s): ' % (self.__class__.__name__, version)
            ver = self.p.getinput(prompt)
            if ver == "":
                ver = version

        if self.p.validate_version(ver, versions.app_supported):
            self.p.printsuc('%s Version %s is validated' % (self.__class__.__name__, ver))
            self.version = ver

            self.gzfile = "shotgun-docker-se-%s.tar.gz" % (self.version)
            self.tarfile = 'shotgun-app.%s.tar' % (self.version)
        else:
            self.p.printfail('Inputed %s version %s is not supported!' % (self.__class__.__name__, ver))
            self.p.exit(0)

    def getVersion(self):
        return self.version
    
    def getappfile(self):
        return self.gdata.getTempfolder() + self.gzfile

    def getsiteurl(self, sitetype, yml):
        '''get site url, db server address'''
        getstatus =  False
        SITE_URL = self.getsinglevalue("SHOTGUN_SITE_URL:", yml)
        self.p.printhead('Find site url %s in %s' % (SITE_URL, yml))
        if sitetype == "production":
            self.gdata.SITE_Production_URL=SITE_URL
        else:
            self.gdata.SITE_Staging_URL=SITE_URL

        prompt ='Please input your %s site url? (%s): ' % (sitetype, SITE_URL)
        ans = self.p.getinput(prompt)
        if not ans == "":
            if sitetype == "production":
                if not self.gdata.SITE_Production_URL == ans:
                    self.gdata.SITE_Production_URL = ans
                    getstatus = True
            else:
                if not self.gdata.SITE_Staging_URL == ans:
                    self.gdata.SITE_Staging_URL = ans
                    getstatus = True
        if not getstatus:
            self.p.printhead('The input is %s. Nothing to change.' % (ans))
        return getstatus

    def startover(self, sitetype):
        '''Start over'''
        prompt ='Do you want to start from a fresh %s on %s site? (Y/n): ' % (self.gdata.yml, sitetype)
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            yml = ""
            if sitetype == "production":
                yml = self.production_yml_home + self.gdata.yml
                ymlhome = self.production_yml_home
            else:
                yml = self.staging_yml_home + self.gdata.yml
                ymlhome = self.staging_yml_home

            if not self.p.validate_file(yml):
                cmd = 'rm -f %s' % ymlhome
                self.gencmd(cmd)
            if not self.p.validate_folder(ymlhome):
                cmd = 'mkdir %s' % ymlhome
                self.gencmd(cmd)

            ymlexample = self.homefull+'example/' + self.gdata.yml
            cmd='cp %s %s' % (ymlexample, yml)
            self.gencmd(cmd)

    def setupsite(self, sitetype, ymlhome, yml):
        '''Setup production or staging'''
        prompt ='Do you want to configure %s site? (Y/n): ' % (sitetype)
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            if not self.p.validate_folder(ymlhome):
                cmd='cp -r %s %s' % (self.homefull+'example', ymlhome)
                self.gencmd(cmd)
            else:
                msg ='%s folder exist.' % (sitetype)
                self.p.printfail(msg)
            
                
            '''Edit docker-compose yml'''
            if not self.p.validate_file(yml):
                self.p.printfail('%s doesn\'t exist. Please make sure app package is untar and loaded.' % (yml))
                self.p.exit(0)
            else:
                getstatus = self.getsiteurl(sitetype, yml)
                if getstatus:
                    if sitetype=="production":
                        SITE_URL = self.gdata.SITE_Production_URL
                    else:
                        SITE_URL = self.gdata.SITE_Staging_URL

                    self.p.printhead("Change Shotgun Site URL to %s." % (SITE_URL))
                    
                    self.ymlreplace(self.gdata.URL_IN_YML, SITE_URL,yml)

                    if sitetype == "production":
                        self.setupmedia()
                        #self.setupdb()
                        #self.setupemailer()
                        #self.setupproxy()
        else:
            self.p.printwarn('Ignored configure %s.' % (sitetype))

    def setupmedia(self):
        '''Setup media'''
        prompt ='Do you want to configure %s site? (Y/n): ' % ('media folder')
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y' or ans == '':
            prompt ='Please input your media folder (./media):'
            ans = self.p.getinput(prompt)
            if not ans == '' and not ans == './media':
                '''Edit docker-compose yml'''
                yml = self.production_yml_home + self.gdata.yml
                if not self.p.validate_file(yml):
                    self.p.printfail('%s doesn\'t exist' % (yml))
                    self.p.exit(0)
                else:
                    self.p.printhead("Change media folder to %s." % (ans))
                    OVOL=".\/media:\/media"
                    NVOL="%s:\/media" % (ans.replace('/','\/'))
                    self.ymlreplace(OVOL, NVOL,yml)

    def setupemailer(self, sitetype):
        '''Setup email'''
        if sitetype == "production":
            yml = self.production_yml_home + self.gdata.yml
        else:
            yml = self.staging_yml_home + self.gdata.yml

        prompt ='Do you want to configure %s? (y/N): ' % ('emailnotifier')
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y':
            LN1 = self.getlinenum('# emailnotifier:', yml)
            if not LN1 == "":    
                LN2 = int(LN1)+13
                cmd="sed -i \"%s,%s s/^..#/ /g\" %s" % (str(LN1), str(LN2), yml)
                self.gencmd(cmd)
            else:
                self.p.printhead("Emailnotifier was enabled.")
            
    def setupproxy(self):
        '''Setup proxy'''
        prompt ='Do you want to configure %s? (y/N): ' % ('proxy')
        ans = self.p.getinput(prompt)
        if ans == 'Y' or ans == 'y':
            pro_yml = self.production_yml_home + self.gdata.yml
            sta_yml = self.staging_yml_home + self.gdata.yml
            if self.p.validate_file(pro_yml) and self.p.validate_file(sta_yml):
                '''Enable haproxy in production yml'''
                LN1 = self.getlinenum('# proxy:', pro_yml)
                if not LN1 == "":
                    LN2 = int(LN1)+11
                    cmd="sed -i \"%s,%s s/^..#/ /g\" %s" % (str(LN1), str(LN2), pro_yml)
                    self.gencmd(cmd)
                else:
                    self.p.printhead("Haproxy was enabled.")
                '''Copy haproxy.conf to .proxy folder'''
                hostip = self.gethostip()
                cmd="cp %s %s" % ("dc/haproxy.cfg", self.production_yml_home+"proxy/")
                self.gencmd(cmd)
                self.ymlreplace('replace_host_ip', hostip, self.production_yml_home+"proxy/haproxy.cfg")
                
                self.ymlreplace('replace_production_dns', SITE_Production_URL, self.production_yml_home+"proxy/haproxy.cfg")
                self.ymlreplace('replace_staging_dns', SITE_Staging_URL, self.production_yml_home+"proxy/haproxy.cfg")


                '''Change app http 80 to 8888'''
                self.p.replacethefirstmatch("80:80","8888:80",pro_yml)

                '''Change staging http 80 to 9999'''
                self.p.replacethefirstmatch("80:80","9999:80",sta_yml)

                '''Change transcoder 8008 to 9009'''
                TLN = self.getlinenum("8008:80", sta_yml)
                if not TLN == "":
                    self.ymlreplace("8008:80", "9009:80", sta_yml)
                else:
                    self.p.printhead("Transcoder port was changed.")
            else:
                self.p.printfail("Production server or Staging server was not configured.")

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
            ips.append(['172.0.0.1', 8])
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
        while self.gdata.hostip == "" or not re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', self.gdata.hostip): 
            self.gdata.hostip = self.p.getinput(prompt)

        prompt ='Please input your database password:'
        self.gdata.POSTGRES_PASSWORD = self.p.getinput(prompt)
        while self.gdata.POSTGRES_PASSWORD == "":
            self.gdata.POSTGRES_PASSWORD = self.p.getinput(prompt)
        
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
        prompt='Do you want to load shotgun app image? (Y/n):'
        ans=self.p.getinput(prompt)
        if ans=='Y' or ans=='y' or ans =='':
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
    
    def startserver(self, servertype):
        '''start production server'''
        if servertype == "production":
            if self.p.validate_folder(self.production_yml_home): 
                if self.p.validate_file(self.production_yml_home + self.gdata.yml):
                    IMGSTAT="%s                 %s" % (self.img, self.getVersion())
                    if not self.validate_loaded(self.__class__.__name__, IMGSTAT):
                        if not self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT) and not self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT1):
                            self.dcup(self.production_yml_home, 'production')
                        else:
                            self.p.printfail('shotgun production server is running')
                    else:
                        self.p.printfail('shotgun image isn\'t loaded. Can\'t start')
                else:
                    self.p.printfail('Production server isn\'t configured. Can\'t start')
            else:
                self.p.printfail('Production server isn\'t configured. Can\'t start')
        if servertype == "staging":
            if self.p.validate_folder(self.staging_yml_home): 
                if self.p.validate_file(self.staging_yml_home + self.gdata.yml):
                    IMGSTAT="%s                 %s" % (self.img, self.getVersion())
                    if not self.validate_loaded(self.__class__.__name__, IMGSTAT):
                        if not self.validate_running(self.__class__.__name__, self.staging_yml_home, self.STAT) and not self.validate_running(self.__class__.__name__, self.staging_yml_home, self.STAT2):
                            self.dcup(self.staging_yml_home, 'staging')
                        else:
                            self.p.printfail('shotgun staging server is running')
                    else:
                        self.p.printfail('shotgun image isn\'t loaded. Can\'t start')
                else:
                    self.p.printfail('Staging server isn\'t configured. Can\'t start')
            else:
                self.p.printfail('Staging server isn\'t configured. Can\'t start')

    def stopserver(self, servertype):
        '''start production server'''
        if servertype == "production":
            if self.p.validate_folder(self.production_yml_home): 
                if self.p.validate_file(self.production_yml_home + self.gdata.yml):
                    IMGSTAT="%s                 %s" % (self.img, self.getVersion())
                    if self.validate_loaded(self.__class__.__name__, IMGSTAT):
                        self.dcstop(self.production_yml_home, 'production')
                    else:
                        self.p.printfail('shotgun image isn\'t loaded. Can\'t stop')
                else:
                    self.p.printfail('Production server isn\'t configured. Can\'t stop')
            else:
                self.p.printfail('Production server isn\'t configured. Can\'t stop')
        if servertype == "staging":
            if self.p.validate_folder(self.staging_yml_home): 
                if self.p.validate_file(self.staging_yml_home + self.gdata.yml):
                    IMGSTAT="%s                 %s" % (self.img, self.getVersion())
                    if self.validate_loaded(self.__class__.__name__, IMGSTAT):
                        self.dcstop(self.staging_yml_home, 'staging')
                    else:
                        self.p.printfail('shotgun image isn\'t loaded. Can\'t stop')
                else:
                    self.p.printfail('Staging server isn\'t configured. Can\'t stop')
            else:
                self.p.printfail('Staging server isn\'t configured. Can\'t stop')
    
    def setpassword(self, sitetype):
        if sitetype == "production":
            if self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT) or self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT1):
                self.p.printhead('Change shotgun_admin password to \'%s\'' % (self.gdata.SHOTGUN_ADMIN_PW))
                cmd = 'cd %s && docker-compose run --rm app rake admin:reset_shotgun_admin_password[%s]' % (self.production_yml_home, self.gdata.SHOTGUN_ADMIN_PW)
                self.gencmd(cmd)
            else:
                self.p.printfail('shotgun production server is not running, can\'t reset password')
        
        if sitetype == "staging":
            if self.validate_running(self.__class__.__name__, self.staging_yml_home, self.STAT) or self.validate_running(self.__class__.__name__, self.staging_yml_home, self.STAT2):
                self.p.printhead('Change shotgun_admin password to \'%s\'' % (self.gdata.SHOTGUN_ADMIN_PW))
                cmd = 'cd %s && docker-compose run --rm app rake admin:reset_shotgun_admin_password[%s]' % (self.staging_yml_home, self.gdata.SHOTGUN_ADMIN_PW)
                self.gencmd(cmd)
            else:
                self.p.printfail('shotgun staging server is not running, can\'t reset password')


    def rakeupgrade(self, sitetype):
        if sitetype == "production":
            if self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT) or self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT1):
                cmd = 'cd %s && docker-compose run --rm app rake admin:upgrade' % (self.production_yml_home)
                self.gencmd(cmd)
            else:
                self.p.printfail('shotgun production server is not running, can\'t reset password')
        
        if sitetype == "staging":
            if self.validate_running(self.__class__.__name__, self.staging_yml_home, self.STAT) or self.validate_running(self.__class__.__name__, self.staging_yml_home, self.STAT2):
                cmd = 'cd %s && docker-compose run --rm app rake admin:upgrade' % (self.staging_yml_home)
                self.gencmd(cmd)
            else:
                self.p.printfail('shotgun staging server is not running, can\'t reset password')

    def rakescaletranscoder(self, sitetype):
        if sitetype == "production":
            if self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT) or self.validate_running(self.__class__.__name__, self.production_yml_home, self.STAT1):
                cmd = 'cd %s && docker-compose scale transcoderworker=8'  % (self.production_yml_home)
                self.gencmd(cmd)
            else:
                self.p.printfail('shotgun production server is not running, can\'t reset password')
        
        if sitetype == "staging":
            if self.validate_running(self.__class__.__name__, self.staging_yml_home, self.STAT) or self.validate_running(self.__class__.__name__, self.staging_yml_home, self.STAT2):
                cmd = 'cd %s && docker-compose scale transcoderworker=8' % (self.staging_yml_home)
                self.gencmd(cmd)
            else:
                self.p.printfail('shotgun staging server is not running, can\'t reset password')

    def dockercomposestatus(self, sitetype):
        yml = ""
        if sitetype == "production":
            yml = self.production_yml_home 
        else:
            yml = self.staging_yml_home

        print yml
        if self.p.validate_folder(yml):
            cmd="cd %s && docker-compose ps" % (yml)
            self.gencmd(cmd)
        else:
            self.p.printfail(('%s server isn\'t configured.') % (sitetype))
