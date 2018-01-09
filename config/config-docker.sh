#!/bin/bash
#. ./Shotgun_Config.sh

###Shotgun Versions
APPVER="7.6.0.0"
TSVER="5.0.7"
TWVER="8.2.5"
SECVER="1.2.1"

###Customer OpenVPN
OVPNFILENAME="" #Leave it blank if you don't want to install OpenVPN Client

###Standalone Postgresql Configuration
POSTGRES_HOST="" #Leave if blank if you don't use standalone DB

###Globle configuration
SHOTGUN_SITE_URL="sg.autodesk.com"
VOLUMES="" #Have to use \/ to represent /
ENABLEEMAILER=0 #1=uncomment emailnotifier 0=don't change
ENABLETRANSCODER=1 #1=uncomment transcoder 0=don't change
ENABLEPROXY=0 #1=uncomment proxy 0=don't change


####Define folders
TMP="/usr/tmp"
TARGET="/opt"

###Shotgun APP
SGDIR="/opt/shotgun/se"
DCTAR="shotgun-docker-se-${APPVER}.tar.gz"
DC="shotgun-app.${APPVER}.tar"
SGOLD="shotgun.mystudio.test"
DCIMG="shotgun-app"
EXP="example"
PUD="production"
DCYML="docker-compose.yml"

###Shotgun Transcoder and Worker
TSDIR="/opt/shotgun/se/transcoder-server"
TCSTAR="shotgun-docker-se-transcoder-server-${TSVER}.tar.gz"
TCS="shotgun-transcoder-server.${TSVER}.tar"
TSIMG="shotgun-transcoder-server"
TSSTR="%TCSERVER_VERSION%"

TWDIR="/opt/shotgun/se/transcoder-worker"
TCWTAR="shotgun-docker-se-transcoder-worker-${TWVER}.tar.gz"
TCW="shotgun-transcoder-worker.${TWVER}.tar"
TWIMG="shotgun-transcoder-worker"
TWSTR="%TCWORKER_VERSION%"

###Shotgun SEC
SECDIR="/opt/shotgun/sec"
SECTAR="shotgun-docker-sec-${SECVER}.tar.gz"
SEC="shotgun-docker-sec-${SECVER}.tar"
SECIMG="shotgun-docker-sec"

###Security Settings

function _secur {
  ###Disable firewall
  echo "Disable firewalld ..."
  systemctl stop firewalld
  systemctl disable firewalld
  echo "firewalld is disabled."
  echo

  ###Disable SELinux
  echo "Disable selinux ..."
  SElinuxConfig="/etc/selinux/config"
  SEconfig1="SELINUX=enforcing"
  SEconfig2="SELINUX=permissive"
  SEconfig3="SELINUX=disabled"
  SESTAT=`getenforce`
  if [[ $SESTAT == "Permissive" ]]; then
    sed -i "s/${SEconfig2}/${SEconfig3}/g" $SElinuxConfig
  fi
  if [[ $SESTAT == "Enforcing" ]]; then
    sed -i "s/${SEconfig1}/${SEconfig3}/g" $SElinuxConfig
  fi
  echo "Selinux is disabled. Please reboot."
  echo
}

###Install Client VPN
function _clientvpn {
  OVPNENV='Environment=\"OPENSSL_ENABLE_MD5_VERIFY=1 NSS_HASH_ALG_SUPPORT=+MD5\"'
  OVPNCLIENTSERVICE="/usr/lib/systemd/system/openvpn-client@.service"
  OVPNSVC="[Service]"
  OVPNCFGPATH="/etc/openvpn/client/"
  OVPNFILEEXT=".conf"
  CLTFNAME=$OVPNFILENAME$OVPNFILEEXT
  
  echo "Configuring OpenVPN ..."
  yum install -y openvpn openssl openssl098e.x86_64
  yum update -y all

  SVCLIN=$(sed -n "/$OVPNENV/=" $OVPNCLIENTSERVICE);
  if [[ $SVCLIN == "" ]]; then
    SVCLIN==$(sed -n "/$OVPNSVC/=" $OVPNCLIENTSERVICE);
    sed -i "/${OVPNSVC}/a ${OVPNENV}" $OVPNCLIENTSERVICE
    systemctl daemon-reload
  fi

  if [[ ! -f $OVPNCFGPATH$OVPNFILENAME$OVPNFILEEXT ]]; then
    cp $CLTFNAME $OVPNCFGPATH$CLTFNAME
  fi

  systemctl enable openvpn-client@$OVPNFILENAME
  systemctl start openvpn-client@$OVPNFILENAME
  echo
}

###Add sudoers
function _add_sudoer {
  USERNAME="shotgun"  
  SGUSER="${USERNAME}	ALL=(ALL)	NOPASSWD: ALL"
  SUDOER="/etc/sudoers"
  SGPASSWORD="password"

  echo "Add sudoer"
  if [ ! -d /home/shotgun ]; then
    /usr/sbin/useradd -p `openssl passwd -1 $SGPASSWORD` $USERNAME
  fi

  SUDOLIN=$(sed -n "/$SGUSER/=" $SUDOER);
  if [[ $SUDOLIN == "" ]]; then
    echo $SGUSER >> $SUDOER
  fi
}

###untar all packages
function _untar {
  echo "Extracting ${1} ..."
  echo "Extracted file is ${2}"
  if [[ ! -f $2 ]]; then
    echo "tar xvfz ${1} -C ${TARGET}"
    tar xvfz $1 -C $TARGET
  else
    echo "The file is existed."
  fi
  echo
}

#$1=Image dir $2=Image file $3=docker application name
function _dcload {
  echo "Checking if ${3} loaded..."
  echo "docker images | grep ${3} &> /dev/null"
  if docker images | grep $3 &> /dev/null
  then
    echo "${3} is loaded"
  else
    echo "${3} isn't loaded"
    echo "Loading ${3} ..."
    echo "cd ${1} && docker load < ${2}"
    cd $1 && docker load < $2
    echo "${3} is loaded"
  fi
  echo
}

#$1=Production yml file
function _edityml {
  echo "Change Shotgun Site URL to ${SHOTGUN_SITE_URL} ... "
  sed -i "s/$SGOLD/$SHOTGUN_SITE_URL/g" $1 
  echo
  
  if [[ ! $VOLUMES == "" ]]; then 
    echo "Modifying media folder ... "
    OVOL=".\/media:\/media"
    NVOL=$VOLUMES":\/media"
    sed -i "s/$OVOL/$NVOL/g" $1 
    echo
  fi
  
  if [[ $ENABLEEMAILER == 1 ]]; then 
    echo "Enable emailnotifier ..."
    EM1="emailnotifier:"
    EMLN1=$(sed -n "/$EM1/=" $1);
    let EMLN2=EMLN1+13
    sed -i "$EMLN1,$EMLN2 s/^..#/ /g" $1
    echo
  fi

  if [[ $ENABLETRANSCODER == 1 ]]; then 
    echo "Enable transcoder ..."
    TC1="transcoderserver:"
    TCLN1=$(sed -n "/$TC1/=" $1);
    let TCLN2=TCLN1+22
    sed -i "$TCLN1,$TCLN2 s/^.#//g" $1
    echo
    
    echo "Change transcoder server version ${TSVER} ..."
    sed -i "s/$TSSTR/$TSVER/g" $1 
    echo

    echo "Change transcoder worker version ${TWVER} ..."
    sed -i "s/${TWSTR}/${TWVER}/g" $1
    echo
  fi

  if [[ $ENABLEPROXY == 1 ]]; then 
    echo "Enable proxy ..."
    PR1="proxy:"
    PRLN1=$(sed -n "/$PR1/=" $1);
    let PRLN2=PRLN1+6
    sed -i "$PRLN1,$PRLN2 s/^..#//g" $1
    sed -i "$PRLN1,$PRLN2 s/^/ /g" $1
    echo
  fi

  if [ ! $POSTGRES_HOST == "" ]; then 
    echo "Enable Postgresql ..."
    PGSQLFILE="/var/lib/pgsql/9.6/data/pg_hba.conf"
    PGIP1="all all 172.18"
    PGIP1F="host  all all 172.18.0.0/24 md5"
    PGIP2="all all 172.19"
    PGIP2F="host  all all 172.19.0.0/24 md5"
    POSTGRES_PASSWORD=`sed -n 's/^.*shotgun://p' /root/.pgpass` 
    PGSQL="POSTGRES_HOST: db"
    PGHOST="POSTGRES_HOST: "$POSTGRES_HOST
    DBPWOLD="#POSTGRES_PASSWORD: dummy"
    DBPWNEW="POSTGRES_PASSWORD: "$POSTGRES_PASSWORD
    DBOPHOST="PGHOST: db"
    DBOPHOSTNEW="PGHOST: "$POSTGRES_HOST
    DBOPPW="#PGPASSWORD: dummy"
    DBOPPWNEW="PGPASSWORD: "$POSTGRES_PASSWORD
    
    echo "Changing DB hostname ..."
    sed -i "s/${PGSQL}/${PGHOST}/g" $1 
    sed -i "s/${DBOPHOST}/${DBOPHOSTNEW}/g" $1 

    echo "Adding Postgresql password in docker-compose.yml... "
    sed -i "s/${DBPWOLD}/${DBPWNEW}/g" $1
    sed -i "s/${DBOPPW}/${DBOPPWNEW}/g" $1
    echo "Password added"
    echo

    ###Comment out db dependency
    CDBLN1=$(sed -n "/#- db/=" $1);
    echo $DCBLN1
    if [[ $CDBLN1 == "" ]]; then
      sed -i "s/- db/#- db/g" $1
    fi

    echo "Add Docker Container IP to pg_hba.conf"
    PGDBIPLN1=$(sed -n "/$PGIP1/=" $PGSQLFILE);
    echo $PGDBIPLN1
    if [[ $PGDBIPLN1 == "" ]]; then
      echo $PGIP1F >> $PGSQLFILE
    else
      echo "Docker Container IP existed"
    fi

    PGDBIPLN1=$(sed -n "/$PGIP2/=" $PGSQLFILE);
    echo $PGDBIPLN1
    if [[ $PGDBIPLN1 == "" ]]; then
      echo "Add Docker Container IP to pg_hba.conf"
      echo $PGIP2F >> $PGSQLFILE
    else
      echo "Docker Container IP existed"
    fi
    echo "Done"

    systemctl restart postgresql-9.6 

    echo "Disable Postgresql in YML ..."
    CDBSLN1=$(sed -n "/#  db:/=" $1);
    echo $CDBSLN1
    if [[ $CDBSLN1 == "" ]]; then
      DB1="db:"
      DBLN1=$(sed -n "/$DB1/=" $1);
      let PRLN2=DBLN1+7
      sed -i "$DBLN1,$PRLN2 s/^/#/g" $1
    fi
    echo
  fi
}

#### add shotgun sec
function _sec_start_script {
  SECRUN="/etc/systemd/system/secstart.service"
  SRC="secstart.service"
  echo "Checking if SEC startup exist"
  if [[ ! -f $SECRUN ]]; then
    echo "cp ${SRC} ${SECRUN}"
    cp $SRC $SECRUN 
    systemctl enable secstart
    systemctl start secstart
  fi
}

function _start {
  ###Change System Security Settings
  _secur

  ###Install OpenVPN
  if [ ! $OVPNFILENAME == "" ]; then
    _clientvpn
  fi
  
  ###Add shotgun user and add to sudoer
  _add_sudoer

  ###Extracting all files
  _untar $TMP/$DCTAR $SGDIR/$DC
  _untar $TMP/$TCSTAR $TSDIR/$TCS
  _untar $TMP/$TCWTAR $TWDIR/$TCW
  _untar $TMP/$SECTAR $SECDIR/$SEC

  ###Change /opt/shotgun owner
  echo "Modify /opt ownership ..."
  echo "sudo chown -R shotgun:shotgun ${TARGET}"
  sudo chown -R shotgun:shotgun $TARGET
  echo

  ###Load docker images
  _dcload $SGDIR $DC $DCIMG
  _dcload $TSDIR $TCS $TSIMG
  _dcload $TWDIR $TCW $TWIMG
  _dcload $SECDIR $SEC $SECIMG

  ###Add sec service and start up
  _sec_start_script
  
  ###Create production folder
  echo "Creating productoin folder ..."
  if [[ ! -d $SGDIR/$PUD ]]; then
    cp -r $SGDIR/$EXP $SGDIR/$PUD
    echo "Production folder created in ${SGDIR}"
  else
    echo "Production folder existed in ${SGDIR}"
  fi
  echo
  
  ###Edit docker-compose.yml
  echo "Editing ${DCYML} ..."
  _edityml $SGDIR/$PUD/$DCYML

  ###Install NTP
  yum install ntpdate -y && ntpdate pool.ntp.org

  ###Install screen
  yum install -y screen
}


_start
