#!/bin/bash

#######################################################################################
#  This scripts is doing basic docket on Centos 7 only  #
#######################################################################################

set +e

#Postgresql configuration file
PG_FILE=/var/lib/pgsql/9.*/data/postgresql.conf

function showUsage {
    echo "Usage: " `basename "$0"` "[options]"
    echo -e "\t[--validate]          Validate server configuration"
    echo -e "\t[--install]           Install docker and docker-compose"
    echo -e "\t[-h,--help,--usage]   Display this help and exit."
    echo -e "\t[-v,--verbose]        Print commands before executing them."
}


# Validates
function validate {
    sudo yum install bc -y > /dev/null

    echo -e "\nShotgun Enterprise Setup Validation\n"
    echo -e "\nHIGH LEVEL"
    echo "=========="

    # Hostname
    printf "Hostname               : %-10s \n" $HOSTNAME

    # Os release number checker
    MOSR=`rpm -q --qf "%{VERSION}" $(rpm -q --whatprovides redhat-release)`

    if (( $(echo "$MOSR > 6" |bc -l) )); then
	export OVER="OK"
    else
	export OVER="BAD"
    fi

    # Os release checker
    if [ $(cat /etc/*release | grep -c CentOS) -ne 0 ]; then
	export DISTRO='centos'
	export OVER="OK"
    elif [ $(cat /etc/*release | grep -c 'Red Hat') -ne 0 ]; then
	export DISTRO='redhat'
	export OVER="OK"
    else
	export DISTRO="unknown"
	export OVER="BAD"
    fi
    printf "RHEL 7/CentOS 7        : %-10s %-10s %-10d\n" $OVER $DISTRO $MOSR

    #Kernel version checker
    DRV=3.10
    CCV=`uname -r|awk -F. '{print $1"."$2}'`

    if (( $(echo "$CCV >= $DRV" |bc -l) )); then
	export OVER="OK"
    else
	export OVER="BAD"
    fi
    printf "Kernel version         : %-10s %-10s\n" $OVER $CCV

    # CPU model
    CPU=`cat /proc/cpuinfo |grep "model name" |awk -F: '{print $2}'| uniq`
    printf "CPU model              :$CPU\n"

    # Number of CPU
    NCPU=`cat /proc/cpuinfo |grep "model name" |awk -F: '{print $2}'| wc -l`
    if (( $NCPU < 6)); then
	export OVER="BAD"
    else
	export OVER="OK"
    fi
    printf "NB CPU                 : %-10s %-10d\n" $OVER $NCPU

    # Memory check
    MEM=`cat /proc/meminfo |grep "MemTotal:"|awk '{print $2}'`
    TMEM=`echo "scale = 3; $MEM/1024/1024" |bc`

    if (( $MEM < 67108864 ));then
	export OVER="BAD"
    else
        export OVER="OK"
    fi
    printf "RAM                    : %-10s %-10sKB\n" $OVER $MEM

    # SELinux check
    export OVER="OK"
    if [ ! \( `getenforce` == "Permissive" -o `getenforce` == "Disabled" \) ]; then
      export OVER="BAD"
    fi
    printf "SE Linux               : %-10s %-10s\n" $OVER `getenforce`

    echo -e "\nDOCKER"
    echo "======"
    # Docker version check
    export OVER="BAD"
    DOV=`docker -v`
    if [ -n "$DOV" ];then
	DOCK=`docker -v|awk '{print $3}'|awk -F. '{print $1}'`
	if (( $DOCK < 17 ));then
    	    export OVER="BAD"
	else
    	    export OVER="OK"
	fi
    else
	echo "Docker is not installed. Please install." `basename "$0"` "--help"
    fi
    printf "Docker installed       : %-10s $DOV\n" $OVER

    # Docker compose version check
    export OVER="BAD"
    DCOV=`docker-compose -v`
    if [ -n "$DCOV" ];then
	DOCKC=`docker-compose -v|awk '{print $3}'|awk -F. '{print $1" "$2}'`
	V=($DOCKC)
	if (( ${V[0]} < 1 && ${V[1]} < 13 ));then
	    export OVER="BAD"
	else
    	    export OVER="OK"
	fi
    else
	echo "Docker-compose is not installed. Please install." `basename "$0"` "--help"
    fi
    printf "Docker-compose         : %-10s $DCOV\n" $OVER

    # Docker status
    export OVER="BAD"
    DRUN=`rpm -qa|grep docker`
    if [ -n "$DRUN" ]; then
    STATUS=`systemctl status docker.service|grep active|awk '{print $2}'`
	if [ $STATUS = 'active' ];then
	    export OVER="OK"
	else
	    export OVER="BAD"
	fi
    else
	echo "Docker is not installed. Please install." `basename "$0"` "--help"
    fi
    printf "Docker-status          : %-10s %-10s\n" $OVER $STATUS



    # ADDITIONAL INFO
    echo -e "\nADDITIONAL INFO"
    echo "==============="
    s3_hosts=(sg-media-usor-01 sg-media-tokyo sg-media-ireland)
    for i in ${s3_hosts[@]}; do
	if ( curl -sS  https://${i}.s3.amazonaws.com|grep "AccessDenied">/dev/null );then
	    export OVER="OK"
	else
	    export OVER="NO"
	    break
	fi
    done
    printf "S3 available           : %-10s\n" $OVER


    # DATABASE INFO
    echo -e "\nDATABASE INFO"
    echo "==============="
    export OVER="NO"
    if (rpm -qa|grep postgres); then
    STATUS=`systemctl status postgresql.service|grep active|awk '{print $2}'`
	if [ $STATUS = 'active' ];then
	    export OVER="YES"
	else
	    export OVER="NO"
	fi
    else
	echo "Postgres is not installed."
    fi
    printf "PostgreSQL-running     : %-10s %-10s\n" $OVER $STATUS

    # Postgres parameters
    if sudo test -f $PG_FILE; then 
	printf "\nPostgres parameters:\n"
	sudo cat /var/lib/pgsql/9.*/data/postgresql.conf|grep -E 'shared_buffers|work_mem|maintenance_work_mem|vacuum_cost_delay|effective_cache_size|max_connections|statement_timeout'|uniq
    else
	export OVER="NONE"
	printf "Postgres parameters    : %-10s\n" $OVER
    fi
}

function install_all {

sudo yum install -y yum-utils epel-release

sudo yum-config-manager \
    --add-repo \
        https://download.docker.com/linux/centos/docker-ce.repo
sudo yum makecache fast

# Install docker
sudo yum -y install docker-ce python2-pip
sudo systemctl start docker
sudo docker run hello-world

# Install docker compose
sudo pip install docker-compose
}

# Parse command-line options
for i in "$@"
do
case $i in
-v|--verbose)
    set -x
    shift
    ;;
-h|-help|--usage|--help)
    showUsage
    exit 0
    ;;
--validate)
    validate
    shift
    ;;
--install)
    install_all
    shift
    ;;
*)
    ;;
esac
done



