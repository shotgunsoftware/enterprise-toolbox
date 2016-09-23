#!/bin/bash
#
# To prep for this script should have CentOS 6.x installed with the minimal defaults
# for a server (really having no extra packages at all is good).  Then create a user named "shotgun"
# with sudo access that uses the bash shell as it's default.  This server needs access out to the
# internet, specifically:
#
#  https://share.shotgunsoftware.com
#  svn to https://github.com
#  http://yum.pgrpms.org
#  ftp://ftp.ruby-lang.org
#  http://rubyforge.org
#  https://www.tn123.org
#
# Then run this script, as the shotgun user

# Current shell checker
# Script should be run under BASH shell.
# e.g.:
# - /bin/bash setup_validation.sh
# - bash setup_validation.sh
# - ./setup_validation.sh (if you current shell is BASH)

echo "Checking current Shell..."
MYSHELL=$(ps -p "$$"|grep bash)

if [ -n "$MYSHELL" ]; then
  echo  "Current shell is BASH, continue..."
else
  echo "Current shell is not BASH, please set bash as current shell and rerun this script. You can also try to run 'bash setup_validation.sh'"
  exit 1
fi

# Os release checker
if [ $(cat /etc/*release | grep -c CentOS) -ne 0 ]; then
  export DISTRO='centos'
elif [ $(cat /etc/*release | grep -c 'Red Hat') -ne 0 ]; then
  export DISTRO='redhat'
else
  echo 'This script only supports RHEL and CentOS 6.x'
  exit 1
fi


# Usage function
function showUsage {
    echo "Usage: bash setup_validation.sh [options]"
    echo "Validate server setup for Shotgun."
    echo -e "\t[-h,--help,--usage]   Display this help and exit."
    echo -e "\t[-v,--verbose]        Print commands before executing them."
}

function validate {
    echo ==== VALIDATING ====

    if [ `whoami` != "shotgun" ]; then
      echo "setup_validation.sh must be run as shotgun user"
      exit 1
    fi

    if [ `date +%Z` != "UTC" ]; then
      echo "time zone must be UTC"
      exit 1
    fi

    if ! [[ `getenforce` == "Permissive" || `getenforce` == "Disabled" ]]; then
      echo "SELinux must be deactivated"
      exit 1
    fi

    # shotgun user access
    echo "Testing http://rubygems.org"
    curl -sS --fail http://rubygems.org >/dev/null
    echo "Testing https://github.com"
    curl -sS --fail https://github.com >/dev/null
    echo "Testing http://yum.pgrpms.org"
    curl -sS --fail http://yum.pgrpms.org >/dev/null
    echo "Testing http://ftp.ruby-lang.org"
    curl -sS --fail http://ftp.ruby-lang.org >/dev/null
    echo "Testing http://production.cf.rubygems.org"
    curl -sS --fail http://production.cf.rubygems.org >/dev/null
    echo "Testing https://share.shotgunsoftware.com"
    curl -sS --fail https://share.shotgunsoftware.com >/dev/null
    echo "Testing https://tn123.org"
    curl -sS --fail https://www.tn123.org >/dev/null

    # sudo user access
    echo "Testing as sudo - http://rubygems.org"
    sudo curl -sS --fail http://rubygems.org >/dev/null
    echo "Testing as sudo http://yum.pgrpms.org"
    sudo curl -sS --fail http://yum.pgrpms.org >/dev/null

    sudo ls >/dev/null
    echo All Good!
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
*)
    ;;
esac
done

validate
