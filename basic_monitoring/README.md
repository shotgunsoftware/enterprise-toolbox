# Local Monitoring
The following instructions will set up two cron jobs that will monitor the status of Shotgun. 
The cron jobs will be gathering metrics in order to diagnose possible contentions sources. 
Logs are rotated in order to avoid filling up your disk.

## Metrics
For Application Servers:

- Top output
- Passenger status

For Database Servers:

- Top output
- Number of active requests

## App Server Monitoring Installation
On the App Server, execute the following, as the Shotgun admin user:

    # Create the log folder. Replace shotgun_user by the name of the Shotgun admin user
    sudo mkdir -p /var/log/shotgun && sudo chown $shotgun_user:$shotgun_user /var/log/shotgun
    
    # Copy the monitoring scripts
    sudo cp ./basic_monitoring/scripts/shotgun_monitor_app_server /usr/local/bin && sudo chmod +x /usr/local/bin/shotgun_monitor_app_server
    sudo cp ./basic_monitoring/crons/shotgun_app_server /etc/cron.d/shotgun_app_server
    sudo cp ./basic_monitoring/logrotates/shotgun_app_server /etc/logrotate.d/shotgun_app_server

## DB Server Monitoring Installation
On the database server, execute the following as the Shotgun admin user (database server may be the same server as
the application server):

    # Create the log folder. Replace shotgun_user by the name of the Shotgun admin user
    sudo mkdir -p /var/log/shotgun && sudo chown $shotgun_user:$shotgun_user /var/log/shotgun
    
    # Copy the monitoring scripts
    sudo cp ./basic_monitoring/scripts/shotgun_monitor_db_server /usr/local/bin && sudo chmod +x /usr/local/bin/shotgun_monitor_db_server
    sudo cp ./basic_monitoring/crons/shotgun_db_server /etc/cron.d/shotgun_db_server
    sudo cp ./basic_monitoring/logrotates/shotgun_db_server /etc/logrotate.d/shotgun_db_server
    
    # Edit the cron job so it run under the user used to manage Shotgun. Replace shotgun_user by the name of the Shotgun admin user
    sudo vi /etc/cron.d/shotgun_db_server

## Logs Location

App server logs: `/var/log/shotgun/app_server.log`  
DB server logs: `/var/log/shotgun/db_server.log`
