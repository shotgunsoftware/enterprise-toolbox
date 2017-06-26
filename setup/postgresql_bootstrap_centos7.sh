#!/bin/bash
#
# To prep for this script should have CentOS or RHEL 7.x 64bit installed with the minimal defaults
# for a server (really having no extra packages at all is good).  Then create a user named "shotgun"
# with sudo access that uses the bash shell as it's default.  This server needs access out to the
# internet.
#
# Then run this script, as the shotgun user, using bash

echo "Checking current Shell..."
MYSHELL=$(ps -p "$$"|grep bash)

if [ -n "$MYSHELL" ]; then
  echo  "Current shell is BASH, continue..."
else
  echo "Current shell is not BASH, please set bash as current shell and rerun this script. You can also try to run 'bash install_centos6.sh'"
  exit 1
fi

# Install bc
sudo yum install bc -y

# Os release checker
if [ $(cat /etc/*release | grep -c CentOS) -ne 0 ]; then
  export DISTRO='centos'
elif [ $(cat /etc/*release | grep -c 'Red Hat') -ne 0 ]; then
  export DISTRO='redhat'
else
  echo 'This install script only supports RHEL and CentOS 7.x'
  exit 1
fi

# Os release number checker
MOSR=`rpm -q --qf "%{VERSION}" $(rpm -q --whatprovides redhat-release)`

if (( $(echo "$MOSR == 7" |bc -l) )); then
   echo "RHEL 7/CentOS 7 detected ... continue installation"
else
   echo "RHEL 6/CentOS 6 does not detected ... installation canceled"
   exit 1
fi

#
# ENVIRONMENT VARIABLES
#

# Postgres 9.3
export SG_PGSQL_VER=93
export SG_PGSQL_VER_DOT=9.3
export SG_PGSQL_DISTRO=pgdg-${DISTRO}${SG_PGSQL_VER}-${SG_PGSQL_VER_DOT}-3.noarch.rpm

# Postgres 9.6
#export SG_PGSQL_VER=96
#export SG_PGSQL_VER_DOT=9.6
#export SG_PGSQL_DISTRO=pgdg-${DISTRO}${SG_PGSQL_VER}-${SG_PGSQL_VER_DOT}-3.noarch.rpm

# You can modify this folder to initialize a Shotgun ready database in a custom location.
# You will also need to modify your systemd configuration for the PostgreSQL service so the good data folder is used.
export PGDATA=/var/lib/pgsql/${SG_PGSQL_VER_DOT}/data
export DOWNLOAD_DIR=~

function validate {
    echo ==== VALIDATING ====

    # sudo user access
    echo "Testing as sudo https://download.postgresql.org"
    sudo curl -sS --fail https://download.postgresql.org >/dev/null

    sudo ls >/dev/null
    echo All Good!
}

function install_pgdg() {
  echo ======= INSTALLING COMMON COMPONENTS =======

  sudo yum update -y
  sudo yum install -y wget

  cd $DOWNLOAD_DIR
  wget https://download.postgresql.org/pub/repos/yum/${SG_PGSQL_VER_DOT}/redhat/rhel-6-x86_64/${SG_PGSQL_DISTRO}
  sudo rpm -Uvh --replacepkgs ${SG_PGSQL_DISTRO}
}

function install_postgresql () {
  echo ======= INSTALLING POSTGRESQL SERVER =======
  sudo yum install -y postgresql${SG_PGSQL_VER} postgresql${SG_PGSQL_VER}-server postgresql${SG_PGSQL_VER}-contrib pg_top${SG_PSQL_VER}

  sudo -u postgres /usr/pgsql-${SG_PGSQL_VER_DOT}/bin/initdb --locale 'en_US.UTF-8' --pgdata $PGDATA
}

function configure_postgresql () {
  # Disable transparent huge page defrags. Transparent huge page defrags have been known to cause
  # postgres performance issues under heavy load and with postgres maintenance tasks (ex. autovacuum).
  sudo sh -c 'echo "never" > /sys/kernel/mm/transparent_hugepage/defrag'
  sudo sh -c "echo 'echo \"never\" > /sys/kernel/mm/transparent_hugepage/defrag' >> /etc/rc.d/rc.local"

  # Accept connections from local network
  sudo sh -c "cat <<'END_OF_HBA_CONF' >${PGDATA}/pg_hba.conf
local all all peer
host  all all 127.0.0.1/32 md5
host  all all ::1/128 md5
END_OF_HBA_CONF"

  # Listen to connections on all interfaces
  sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" ${PGDATA}/postgresql.conf

  # Enable slow queries logging and change format to support pg_badger reports.
  # See
  sudo sed -i -e "s/.*log_min_duration_statement.*/log_min_duration_statement = 500/" ${PGDATA}/postgresql.conf
  sudo sed -i -e "s/.*log_line_prefix.*/log_line_prefix = '%t \[%p\]: \[%l-1\] db=%d '/" ${PGDATA}/postgresql.conf

  # Log message is produced when a session waits longer than deadlock_timeout to acquire a lock.
  sudo sed -i -e "s/.*log_lock_waits.*/log_lock_waits = on/" ${PGDATA}/postgresql.conf

  # make sure postgres starts up at boot
  sudo systemctl enable postgresql-${SG_PGSQL_VER_DOT}.service
  sudo systemctl start postgresql-${SG_PGSQL_VER_DOT}.service
  sudo service postgresql-${SG_PGSQL_VER_DOT} restart
}

function initialize_db () {
  if [ ! -f ~/.pgpass ]; then
    export PG_PASS=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    echo "localhost:5432:*:shotgun:${PG_PASS}" > ~/.pgpass
  else
    export PG_PASS=$(cat ~/.pgpass | grep shotgun | cut --delimiter ':' --fields 5)
  fi

  chmod 600 ~/.pgpass

  sudo -u postgres psql -c "CREATE USER shotgun WITH SUPERUSER PASSWORD '${PG_PASS}';"
  sudo -u postgres psql -c "ALTER USER postgres PASSWORD '${PG_PASS}'"

  sudo service postgresql-${SG_PGSQL_VER_DOT} restart
}

validate
install_pgdg
install_postgresql
configure_postgresql
initialize_db
