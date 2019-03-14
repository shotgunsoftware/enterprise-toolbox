#!/usr/bin/env ruby
# frozen_string_literal: false

# TODO: on a bad minute, either chop a minute out or use current log to
# pull any tasks longer than \d\{4,}\.\d\+ms and pull the request id,
# and spit out relevant info

$color_text = true

# for parsing options
require 'optparse'
require 'ostruct'
require 'pp'

# for opening log files and checking timestamps
require 'time'
require 'zlib'

# for color
if Gem::Dependency.new('colorize').matching_specs.max_by(&:version).nil?
  $color_text = false
else
  require 'colorize'
end

# for debugging
require 'pry' unless Gem::Dependency.new('pry').matching_specs.max_by(&:version).nil?

# collect arguments
class OptParse
  #
  # Return a structure describing the options.
  #
  def self.parse(args)
    # The options specified on the command line will be collected in *options*.
    # We set default values here.
    options = OpenStruct.new
    options.start_time = ''
    options.end_time = ''
    options.threads = 10
    options.complete = false

    opt_parser = OptionParser.new do |opts|
      opts.banner = 'Usage: log_chop.rb [options]'

      opts.separator ''
      opts.separator 'Specific options:'

      opts.on('-u', '--analyze_user',
              'Analyze chopped log file for amount of Controller, Crud, and',
              'database time used; compared to available CPU time available.') do |u|
        options.analyze_user = u
      end

      opts.on('-t', '--analyze_time',
              'Analyze chopped log file for amount of Controller, Crud, and',
              'database time used; compared to available CPU time available.') do |t|
        options.analyze_time = t
      end

      opts.on('-c', '--complete',
              'During an analysis, report all users instead of just top 10.') do |c|
        options.complete = c
      end

      opts.on('-s', '--start START_TIME',
              "start time for chopping log, in the format 'Mon DD HH:MM:SS'.",
              'If used, must be used with the --end option.',
              'Note that time must be supplied in UTC timezone') do |s|
        options.start_time = s
      end

      opts.on('-e', '--end END_TIME',
              "end time for chopping log, in the format 'Mon DD HH:MM:SS'.",
              'If invoked, must be used with the --start option.',
              'Note that time must be supplied in UTC timezone') do |e|
        options.end_time = e
      end

      opts.on('-r', '--range',
              'Display the start and end times of a given logfile.') do |r|
        options.get_range = r
      end

      opts.on('-p', '--passenger_threads [NUMBER_THREADS]',
              'Specify the humber of active Passenger threads (default 10).') do |p|
        options.threads = p.to_i
      end

      opts.separator ''
      opts.separator 'Common options:'

      # No argument, shows at tail.  This will print an options summary.
      # Try it and see!
      opts.on_tail('-h', '--help', 'Show this message') do
        puts opts
        exit
      end
    end

    begin
      opt_parser.parse!(args)

      if args.count == 0
        ARGV << '-h'
        opt_parser.parse!(args)
      end

      raise 'must supply logfile at end of switches.' unless args.count == 1 && args[0].end_with?('.gz')
      # make sure that both start and end options are used together, show usage otherwise
      if !options.start_time.empty? || !options.end_time.empty?
        unless options.start_time && options.end_time
          ARGV << '-h'
          opt_parser.parse!(args)
        end
      end

      options
    rescue OptionParser::InvalidOption => e
      puts e
      puts opt_parser
    end
  end
end

def format_time(seconds)
  Time.at(seconds).utc.strftime('%M:%S.%L')
end

def format_days(seconds)
  days = (seconds / (60 * 60 * 24)).floor
  hours = (seconds / (60 * 60) % 24).floor
  minutes = ((seconds / 60) % 60).floor
  seconds = (seconds % 60).floor

  "#{days} days, #{hours}h #{minutes}m #{seconds}s"
end

def get_range(logfile)
  f_utc = Time.new
  l_utc = Time.new
  duration = 0.0

  Zlib::GzipReader.open(logfile) do |gz|
    first_line = ''
    last_line = ''
    read_flag = true

    gz.each_line do |l|
      if read_flag
        first_line = l[0..14]
        read_flag = false
      end
      last_line = l[0..14] if gz.eof?
    end

    f_utc = Time.parse(first_line + ' UTC')
    l_utc = Time.parse(last_line + ' UTC')
    duration = l_utc - f_utc
  end
  [f_utc, l_utc, duration]
rescue StandardError => e
  e
end

def print_range(logfile)
  t1 = Time.now
  f_utc, l_utc, duration = get_range(logfile)
  t2 = Time.now
  puts "            log begins: #{f_utc.strftime('%Y-%b-%d %H:%M:%S %Z')} / #{f_utc.getlocal.strftime('%Y-%b-%d %H:%M:%S %Z (%z)')}"
  puts "              log ends: #{l_utc.strftime('%Y-%b-%d %H:%M:%S %Z')} / #{l_utc.getlocal.strftime('%Y-%b-%d %H:%M:%S %Z (%z)')}"
  puts "        total duration: #{Time.at(duration).utc.strftime('%Hh %Mm %S.%Ls')}"
  puts "time spent parsing log: #{(t2 - t1).round(2)} sec\n\n"
end

def do_chop(options, logfile)
  options.start_time += ' utc' unless options.start_time.downcase.end_with?(' utc')
  options.end_time += ' utc' unless options.end_time.downcase.end_with?(' utc')
  start_time = Time.parse(options.start_time)
  end_time = Time.parse(options.end_time)

  sts = start_time.strftime('%Y%m%d_%H%M%S')
  ets = end_time.strftime('%Y%m%d_%H%M%S')
  scope = end_time - start_time

  puts "looking at time from #{start_time} to #{end_time}."
  puts "total window: #{format_days(scope)}"

  begin
    Zlib::GzipReader.open(logfile) do |gzs|
      # Time.at(seconds).utc.strftime('%d days %H:%M:%S.%L')

      t1 = Time.now
      filename = "timber_#{sts}_to_#{ets}.log.gz"

      File.open(filename, 'w') do |file|
        gzd = Zlib::GzipWriter.new(file)
        gzs.each_line do |l|
          yr = Time.now.year
          mo = l[0..2]
          dy = l[4..5]
          hr = l[7..8]
          mn = l[10..11]
          sc = l[13..14]
          timestamp = Time.new(yr, mo, dy, hr, mn, sc, -0)

          gzd.write l if timestamp.between?(start_time, end_time)
        end
        gzd.close
      end

      t2 = Time.now
      puts "parsing log elapsed time: #{(t2 - t1).round(2)} sec\n\n"
      puts "new slice file: #{filename}"
    end
  rescue StandardError => e
    puts e
  end
end

def count(line_parts, duration_index)
  timestamp = Time.parse(line_parts[0..2].join(' ') + ' UTC')
  duration = line_parts[duration_index].tap { |t| t.slice!('ms') }.to_f unless duration_index.nil?
  user_index = line_parts.index { |p| p.include?('user=') }
  user_type = line_parts[user_index].split('=')[0]
  user_type = 'client_user' if user_type.nil? && line_parts[user_index + 1] == '--'
  user_name = line_parts[user_index].split('=')[1]
  type_index = line_parts.index { |p| p.start_with?('INFO:') } + 1
  type = line_parts[type_index].tap { |t| t.slice!(':') } unless type_index.nil?
  parent_type = type.split('.')[0]
  sub_type = type.split('.')[1..-1].join('.')
  # puts "#{user_type}/#{user_name}: #{parent_type}, #{sub_type}, #{duration} milliseconds" unless duration.nil?

  {
    timestamp: timestamp,
    user_name: user_name,
    user_type: user_type,
    duration: duration,
    parent_type: parent_type,
    sub_type: sub_type
  }
end

def analyze(logfile)
  start_time, end_time, duration = get_range(logfile)

  Zlib::GzipReader.open(logfile) do |gz|
    data = {}
    idx = 1

    puts "looking at time from #{start_time} to #{end_time}."
    puts "total window: #{format_days(duration)}"
    t1 = Time.now
    gz.each_line do |l|
      line_parts = l.split
      if l.include?('INFO:')
        duration_index = line_parts.index { |p| p =~ /\d+\.\d+ms/ }
        data[idx.to_s] = count(line_parts, duration_index) unless duration_index.nil?
      end
      idx += 1
    end
    t2 = Time.now
    puts "parsing log: #{(t2 - t1).round(2)} sec\n\n"
    data
  end
end

def calc_per_user(data, scope, options)
  t1 = Time.now
  debug_calc = false
  start_time = data.first[1][:timestamp]

  # stolen tip about how to create an auto-vivifying hash
  per_user = Hash.new { |h, k| h[k] = Hash.new(&h.default_proc) }

  # add up some times and initialize those that need to exist
  data.each do |_k, v|
    # initialize some defaults for each new username. If the key that we want to
    # assign a value to is still a Hash, it's uninitialized.

    puts "doing v! -- #{v}" if debug_calc
    puts "per_user[#{v[:user_type]}][#{v[:user_name]}][#{v[:parent_type]}] -- #{per_user[v[:user_type]][v[:user_name]][:controller]}" if debug_calc
    if per_user[v[:user_type]][v[:user_name]][:controller].is_a?(Hash)
      per_user[v[:user_type]][v[:user_name]][:controller] = 0.0
      per_user[v[:user_type]][v[:user_name]][:requests] = 0
      per_user[v[:user_type]][v[:user_name]][:total] = 0.0
      puts "initializing #{v[:user_name]} controller: #{per_user[v[:user_type]][v[:user_name]][:controller]}" if debug_calc
    else
      puts 'not initializing.' if debug_calc
    end

    # if the process type hasn't been recorded yet, initialize it for user_name
    puts "per_user[#{v[:user_type]}][#{v[:user_name]}][#{v[:parent_type]}] -- #{per_user[v[:user_type]][v[:user_name]][v[:parent_type]]}" if debug_calc
    if per_user[v[:user_type]][v[:user_name]][v[:parent_type]].is_a?(Hash)
      per_user[v[:user_type]][v[:user_name]][v[:parent_type]] = v[:duration]
      puts "initializing #{v[:user_name]}, #{v[:parent_type]}: #{v[:duration]}" if debug_calc
    else
      # if the category exists, sum up. these are the building blocks for the
      # totals we want to generate later
      foo = per_user[v[:user_type]][v[:user_name]][v[:parent_type]] if debug_calc
      per_user[v[:user_type]][v[:user_name]][v[:parent_type]] += v[:duration]
      puts "new value for #{v[:user_name]}, #{v[:parent_type]}: adding #{v[:duration]} to #{foo} -- #{per_user[v[:user_type]][v[:user_name]][v[:parent_type]]}" if debug_calc
    end

    per_user[v[:user_type]][v[:user_name]][:total] += v[:duration]

    next unless v[:parent_type].to_s.end_with?('Controller')
    bar = per_user[v[:user_type]][v[:user_name]][:controller] if debug_calc
    per_user[v[:user_type]][v[:user_name]][:controller] += v[:duration]
    per_user[v[:user_type]][v[:user_name]][:requests] += 1
    puts "per_user[#{v[:user_type]}][#{v[:user_name]}][:controller] was #{bar}, now #{per_user[v[:user_type]][v[:user_name]][:controller]}" if debug_calc
  end

  main_categories = [:controller, :requests, 'Passenger', 'CRUD', 'SQL']

  puts "#{start_time}: "
  per_user.each do |user_type, users|
    arr = users.sort_by { |_key, value| value[:total] }.reverse
    puts "#{user_type}: (% of theoretical Passenger queue limit of 600 seconds; #{options.threads} threads * #{scope} seconds)"
    arr.each_with_index do |i, idx|
      next if options.complete == false && idx >= 5
      formatted_times = {}
      main_categories.each do |category|
        if category == :requests
          formatted_times[category.to_s] = "#{i[1][category]} |"
        else
          i[1][category] = 0.0 if i[1][category].is_a?(Hash)
          ftime = format_time(i[1][category] / 1000).to_s
          duration_ms = i[1][category].to_i
          # (((total ms / (scope in s * 1000)) / 10 passenger queues) * 100 for percent)
          percent = (((i[1][category] / (scope * 1000)) / options.threads) * 100).round(2).to_s
          if $color_text
            percent = if percent.to_f > 69
                        percent.yellow
                      elsif percent.to_f > 89
                        percent.red
                      else
                        percent.green
                      end
          end
          formatted_times[category.to_s] = "#{duration_ms}ms #{ftime}s #{percent}% "
          formatted_times[category.to_s] << '|' unless category.to_s == main_categories.last.to_s
        end
      end

      stats_output = "#{i[0]}: "
      formatted_times.each do |cat, times|
        next if cat == 'Passenger' && options.analyze_user && options.analyze_time
        stats_output << if $color_text
                          "#{cat.cyan}: #{times} "
                        else
                          "#{cat}: #{times} "
                  end
      end
      puts stats_output
    end
    puts "\n"
  end
  t2 = Time.now
  puts "time spent calulating user time: #{(t2 - t1).round(2)} sec\n" if debug_calc
end

def calc_per_time(data, duration, threads)
  t1 = Time.now
  time_stats = Hash.new { |h, k| h[k] = Hash.new(&h.default_proc) }
  scope = duration < 60 ? duration : 60
  data.each do |_k, v|
    mark = v[:timestamp].utc.strftime('%H:%M')
    if time_stats[mark][:controller].is_a?(Hash)
      time_stats[mark][:controller] = 0.0
      time_stats[mark][:requests] = 0
      # puts "instantiating #{mark} controller: #{time_stats[mark][:controller]}"
    end

    if time_stats[mark][v[:parent_type]].is_a?(Hash)
      time_stats[mark][v[:parent_type]] = v[:duration]
      # puts "  instantiating #{v[:parent_type]}: #{v[:duration]}"
    else
      foo = time_stats[mark][v[:parent_type]]
      time_stats[mark][v[:parent_type]] += v[:duration]
      # puts "    adding #{foo} to #{v[:duration]}: #{time_stats[mark][v[:parent_type]]}"
    end

    if v[:parent_type].to_s.end_with?('Controller')
      time_stats[mark][:controller] += v[:duration]
      time_stats[mark][:requests] += 1
    end
  end

  main_categories = [:controller, :requests, 'Passenger', 'CRUD', 'SQL']

  puts "hour:minute: (% of capacity -- theoretical Passenger queue limit of 600 seconds; #{threads} threads * #{scope} seconds)"
  time_stats.each do |timeslice, type|
    formatted_times = {}
    main_categories.each do |category|
      type.each_with_index do |i, _idx|
        next unless i[0] == category
        if category == :requests
          formatted_times[category.to_s] = "#{i[1]} |"
        else
          ftime = format_time(i[1] / 1000).to_s
          duration_ms = i[1].to_i
          # (((total ms / (scope in s * 1000)) / 10 passenger threads) * 100 for percent)
          percent = (((i[1] / (scope * 1000)) / threads) * 100).round(2)
          if $color_text
            percent = if percent.to_f > 89
                        percent.to_s.red
                      elsif percent.to_f > 69
                        percent.to_s.yellow
                      else
                        percent.to_s.green
                      end
          end
          formatted_times[category.to_s] = "#{duration_ms}ms #{ftime}s #{percent}% "
          formatted_times[category.to_s] << '|' unless category.to_s == main_categories.last.to_s
        end
      end
    end

    stats_output = "#{timeslice}: "
    formatted_times.each do |cat, times|
      stats_output << if $color_text
                        "#{cat.cyan}: #{times} "
                      else
                        "#{cat}: #{times} "
                end
    end
    puts stats_output
  end
  t2 = Time.now
  puts "time spent calulating per-minute time: #{(t2 - t1).round(2)} sec\n\n"
end

def calc_user_per_time(data, _duration, options)
  t1 = Time.now
  start_time = data.first[1][:timestamp]
  end_time = start_time + 60
  slice_key = start_time.to_s
  minute_data = {}
  data.each do |d|
    # puts d if debug_calc
    minute_data[slice_key] = {} if minute_data[slice_key].nil?
    if d[1][:timestamp] < end_time
      minute_data[slice_key][d[0]] = d[1]
      # puts "add to #{slice_key}" if debug_calc
    else
      slice_key = d[1][:timestamp].to_s
      start_time = d[1][:timestamp]
      end_time = start_time + 60
      # puts "new key: #{slice_key}" if debug_calc
      minute_data[slice_key] = {} if minute_data[slice_key].nil?
      minute_data[slice_key][d[0]] = d[1]
    end
  end
  t2 = Time.now
  puts "time spent dividing data into per-minute time: #{(t2 - t1).round(2)} sec\n\n"

  minute_data.each do |minute|
    calc_per_user(minute[1], 60, options)
  end
end

options = OptParse.parse(ARGV)
logfile = ARGV[0]
data = {}
duration = 0.0

print_range(logfile) if options.get_range
do_chop(options, logfile) if !options.start_time.empty? && !options.end_time.empty?

if options.analyze_user || options.analyze_time
  data = analyze(logfile)
  _f, _l, duration = get_range(logfile)
end

calc_per_user(data, duration, options) if options.analyze_user && !options.analyze_time
calc_per_time(data, duration, options.threads) if options.analyze_time

calc_user_per_time(data, duration, options) if options.analyze_user && options.analyze_time
