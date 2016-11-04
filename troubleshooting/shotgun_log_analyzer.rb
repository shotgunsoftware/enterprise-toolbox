# Analyse shotgun production logs to produce a report on slow SQL queries.
# Logs are usually found at /var/rails/<application_name>/shared/log/
# More information on logs can be found at https://support.shotgunsoftware.com/hc/en-us/articles/219030198-Production-log-for-Shotgun-Enterprise
#
# Usage: gunzip -c production.log.gz | ruby shotgun_log_analyzer.rb > report.txt
#
# Requires: ruby 1.9.3 or higher

STDERR.puts "Parsing the log..."

all_queries = []

ARGF.each_line do |e|
  # Extract timestamp
  m_timestamp = e.match(/[a-zA-Z]{3} (\d{2}) (\d{2}):(\d{2}):(\d{2})/)

  # Extract output after the contextual information (starting at controller type)
  m = e.match(/SQL\..*?\:(.*?)ms(.*)--(.*)$/)
  
  if m && m[1].to_f

    query = {
        timestamp: m_timestamp,
        duration: m[1].to_f,
        sql: m[3]
    }

    info = m[2]

    m = info.match(/ user=(.*?) /)

    if m && m[1]
      query[:user] = m[1]

      m = info.match(/ page_id=(.*?) /)
      if m && m[1]
        query[:page_id] = m[1]
      end
    else
      m = info.match(/ api_user=(.*)\s/)
 
      if m && m[1]      
        query[:api_user] = m[1]
      end
    end

    all_queries << query
   end
end

STDERR.puts "Parsed %d SQL queries" % all_queries.length

STDERR.puts "Analysing..."
total_time = all_queries.inject(0) { |sum, query| sum + query[:duration]}
total_user_time = all_queries.inject(0) { |sum, query| sum + (query[:user] ? query[:duration] : 0) }
total_api_time = all_queries.inject(0) { |sum, query| sum + (query[:api_user] ? query[:duration] : 0)  }

puts "Total duration:      %10d ms" % total_time
puts "Total user duration: %10d ms" % total_user_time
puts "Total api duration:  %10d ms" % total_api_time


users = all_queries.group_by {|query| query[:user]}
users.delete(nil)
users = users.map { |key, queries| 
    duration = queries.inject(0) { |sum, query| sum + query[:duration] }
    [key, duration]
}
users = users.sort_by { |pair| pair[1] }.reverse

puts ""
puts "Top 20 users by total database queries duration"
puts "-------------------------------------------"
users = users.take(20)
users.each do |pair|
  puts "%20s %8d ms" % pair
end

users = all_queries.group_by {|query| query[:api_user]}
users.delete(nil)
users = users.map { |key, queries| 
    duration = queries.inject(0) { |sum, query| sum + query[:duration] }
    [key, duration]
}
users = users.sort_by { |pair| pair[1] }.reverse

puts ""
puts "Top 20 api users by total database queries duration"
puts "-------------------------------------------"
users = users.take(20)
users.each do |pair|
  puts "%20s %8d ms" % pair
end

by_page_id = all_queries.group_by {|query| query[:page_id]}
by_page_id.delete(nil)
by_page_id = by_page_id.map { |key, queries| 
    duration = queries.inject(0) { |sum, query| sum + query[:duration] }
    [key, duration, queries.length]
}
by_page_id = by_page_id.sort_by { |pair| pair[1] }.reverse

puts ""
puts "Top page by total time"
puts "-------------------------------------------"
by_page_id = by_page_id.take(20)
by_page_id.each do |pair|
  puts "%20s %8d ms" % pair
end

sorted_queries = all_queries.sort_by { |query| query[:duration] }.reverse

puts ""
puts "Worse queries"
puts "-------------------------------------------"
puts "%15s    %10s %20s %8s  %s" % ["Timestamp", "Duration", "User", "page_id", "SQL"]
sorted_queries = sorted_queries.take(20)
sorted_queries.each do |query|
  puts "%15s %10d ms %20s %8s %s" % [query[:timestamp], query[:duration], query[:user] || query[:api_user], query[:page_id], query[:sql]]
end
