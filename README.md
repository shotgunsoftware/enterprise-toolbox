# Shotgun Enterprise Toolbox This repository contains various tools that can be useful for Shotgun System Administrators
## How to use
Clone this repository and follow the instructions related to the tools you want to use.

## Basic Monitoring
Scripts and cron jobs that can be used to gather helpful information about Shotgun health.

[Basic Monitoring](./basic_monitoring)

## Troubleshooting

### Shotgun Log Analyzer
Ruby script that produces a report on underlying psql hot points, heaviest users
and scripts, and slowest queries. The output of this script is a good starting
point to troubleshoot performance issues related to usage patterns. Instructions
in the script header.

[Shotgun Log Analyzer](./troubleshooting/shotgun_log_analyzer.rb)

### Log Chop

This ruby script is also a prod log analyzer, but instead of focusing solely on psql queries and query time, it's focused primarily on discovering 'when' and 'what' for investigating the cause of 503 errors, by reporting on the following:

- per-minute summaries of CPU time taken, broken down into Controller, Passenger, CRUD, and psql time. This also includes number of Controller requests per minute.
- per-user summaries, broken down as above. Report will show top 5 user and top 5 script users for the whole log. the full user summary (not just the top 5) can be generated with the `-c` option.
- per-user/per-minute summaries. This is a combination of per-minute overall usage PLUS a per-user breakdown per minute in the log file.

Usage help can be obtained with `./log_chop.rb -h`, but here's a quick quide for order of operations:

Parsing a log can be time-consuming if looking at an entire day's worth of activity, so this script is intended to both crop a log file to interesting time periods, and to analyze both full and cropped log files, especially if you already know the timestamps of the 503 incidents. First thing to do is to get the range of the log file in question with the `-r` option.  This option will parse a log and quickly give you the range of time (start and end, in UTC) covered in the log. For example:

```
./log_chop -r com_shotgunstudio_mystudio_production.log-20190130.gz
            log begins: 2019-Jan-29 03:50:06 UTC / 2019-Jan-28 19:50:06 PST (-0800)
              log ends: 2019-Jan-30 03:29:15 UTC / 2019-Jan-29 19:29:15 PST (-0800)
        total duration: 23h 39m 09.000s
time spent parsing log: 62.66 sec
```

With that output, you can then chop the full log into a smaller piece for analysis with the `-s` and `-e` options. In this example, we know that we experienced 503s at around 09:27 UTC, so it would be good to analyze the half-hour or so (or more, depending) surrounding the incident. We'll crop from 09:00 to 10:00.

```
./log_chop -s '2019-Jan-29 09:00:00' -e '2019-Jan-29 10:00:00' com_shotgunstudio_mystudio_production.log-20190130.gz
looking at time from 2019-01-29 09:00:00 UTC to 2019-01-29 10:00:00 UTC.
total window: 0 days, 1h 0m 0s
parsing log elapsed time: 177.29 sec

new slice file: timber_20190129_090000_to_20190129_100000.log.gz
```

The `timber_<timestamp>_to_<timestamp>.log.gz` files are the cropped log files that result from using the `-s/-e` options. Due to smaller size, they will be inherently quicker to analyze.

We can employ the `-t` and `-u` options to perform the analysis. `-t` gives a per-minute global summary, while `-u` will give a per-user summary _for the period of time encompassed by the log file being analyzed_. So if you're looking at a whole day's log, the `-u` option will be less useful than looking at an hour or couple minutes' slice of time.

On top of the previous options, using `-tu` together will give both a per-minute summary AND a per-user/per-minute summary, which is extremely granular and frankly a lot of data. On the other hand, this is very useful, but probably good to hold in reserve until you have a chopped log around the incident time. Until then, it's best to start with just the `-t` option to get a high-level read of trouble spots.

For example:

```
./log_chop -tu com_shotgunstudio_mystudio_production.log-20190130.gz
```

**Note**: If you have more than 10 Passenger threads configured for your site, make sure to use the `-p` option so that the stats are calculated correctly; otherwise the stats will be generated with the assumption of a default 10 threads.

#### How to read the output:

- Controller is the initial request from the webapp or an api user. the Controller routes external requests into internal action. This is the best gauge for overall usage.
- Passenger is the request handler. The queue has 10 threads and a backup shared queue of 100 requests. This is where we get the "ten minutes per minute" of possible processing time -- per minute, each Passenger thread has a minute of processor time, for a total of ten (or however many Passenger threads you have configged for your site). Large amounts of time spent here means that the queue is filling up and requests are waiting to be addressed, but big numbers here don't mean that things are crazy, it's just an indicator that the queue is active (though it could be full).
- CRUD is what most requests get passed onto next, this is where Create, Read, Update, and Delete requests start to get processed.
- SQL is where we're spending time handling queries that are generated from CRUD requests.

Of these times, they generally fold up into each other. CRUD time envelops SQL time, and Controller time envelops CRUD time. Passenger time is an outlier and doesn't follow, since a request could spend a bit of time in the queue.

Note that this output is very rough and not currently formatted well for client consumption (this was originally an internal tool), but some massaging could get it into an excel spreadsheet.

TODO:

- allow `log_chop.rb` to read non-gzipped files
- add an option for pure csv output instead of text intended for terminal output.
- combine user and api_user, as it's not terribly important to have them separated.

[Shotgun Log Analyzer](./troubleshooting/log_chop.rb)

## Docker Setup
Create setup menu for Shotgun Docker version.

[Config](./config)
