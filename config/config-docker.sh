#!/bin/bash
#. ./Shotgun_Config.sh

###Shotgun Versions
APPVER="7.4.3.0"
TSVER="5.0.7"
TWVER="8.2.5"
SECVER="1.2.1"

###Globle configuration
SHOTGUN_SITE_URL="sg.autodesk.com"
VOLUMES="\/ABC" #Have to use \/ to represent /
ENABLEEMAILER=0 #1=uncomment emailnotifier 0=don't change
ENABLETRANSCODER=0 #1=uncomment transcoder 0=don't change
ENABLEPROXY=0 #1=uncomment proxy 0=don't change

###Standalone Postgresql Configuration
ENABLEPGSQL=0 #1=uncomment Postgresql 0=don't change
POSTGRES_HOST=""
POSTGRES_PASSWORD=""

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
    sed -i "$EMLN1,$EMLN2 s/^..#//g" $1
    sed -i "$EMLN1,$EMLN2 s/^/ /g" $1
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

  if [[ $ENABLEPGSQL == 1 ]]; then 
    echo "Enable Postgresql ..."
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

    echo "Changing Postgresql password ... "
    sed -i "s/${DBPWOLD}/${DBPWNEW}/g" $1
    sed -i "s/${DBOPPW}/${DBOPPWNEW}/g" $1

    echo "Disable Postgresql in YML ..."
    DB1="db:"
    DBLN1=$(sed -n "/$DB1/=" $1);
    let PRLN2=DBLN1+7
    sed -i "$DBLN1,$PRLN2 s/^/#/g" $1
    echo
  fi
}

function _start {
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
}


_start
