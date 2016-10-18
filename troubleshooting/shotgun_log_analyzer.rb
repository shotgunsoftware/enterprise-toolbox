# Analyse shotgun production logs to produce a report on slow SQL queries.
# Logs are usually found at /var/rails/<application_name>/shared/log/
#
# Usage: gunzip -c production.log.gz | ruby shotgun_log_analyzer.rb > report.txt
#
# Requires: ruby 1.9.3 or higher

STDERR.puts "Parsing the log..."

all_queries = []

ARGF.each_line do |e|
  m = e.match(/SQL\..*?\:(.*?)ms(.*)--(.*)$/)
  
  if m && m[1].to_f

    query = {
        time: m[1].to_f,
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
total_time = all_queries.inject(0) { |sum, query| sum + query[:time]}  
total_user_time = all_queries.inject(0) { |sum, query| sum + (query[:user] ? query[:time] : 0) }  
total_api_time = all_queries.inject(0) { |sum, query| sum + (query[:api_user] ? query[:time] : 0)  }

puts "Total time:      %10d ms" % total_time
puts "Total user time: %10d ms" % total_user_time
puts "Total api time:  %10d ms" % total_api_time


users = all_queries.group_by {|query| query[:user]}
users.delete(nil)
users = users.map { |key, queries| 
    time = queries.inject(0) { |sum, query| sum + query[:time] }
    [key, time]
}
users = users.sort_by { |pair| pair[1]}.reverse 

puts ""
puts "Top 20 users by total database queries time"
puts "-------------------------------------------"
users = users.take(20)
users.each do |pair|
  puts "%20s %8d ms" % pair
end

users = all_queries.group_by {|query| query[:api_user]}
users.delete(nil)
users = users.map { |key, queries| 
    time = queries.inject(0) { |sum, query| sum + query[:time] }
    [key, time]
}
users = users.sort_by { |pair| pair[1]}.reverse

puts ""
puts "Top 20 api users by total database queries time"
puts "-------------------------------------------"
users = users.take(20)
users.each do |pair|
  puts "%20s %8d ms" % pair
end

by_page_id = all_queries.group_by {|query| query[:page_id]}
by_page_id.delete(nil)
by_page_id = by_page_id.map { |key, queries| 
    time = queries.inject(0) { |sum, query| sum + query[:time] }
    [key, time, queries.length]
}
by_page_id = by_page_id.sort_by { |pair| pair[1]}.reverse

puts ""
puts "Top page by total time"
puts "-------------------------------------------"
by_page_id = by_page_id.take(20)
by_page_id.each do |pair|
  puts "%20s %8d ms" % pair
end

sorted_queries = all_queries.sort_by { |query| query[:time]}.reverse

puts ""
puts "Worse queries"
puts "-------------------------------------------"
puts "%10s ms %20s %6s %s" % ["Time", "User", "page_id", "SQL"]
sorted_queries = sorted_queries.take(20)
sorted_queries.each do |query|
  puts "%10d ms %20s %6s %s" % [query[:time], query[:user] || query[:api_user], query[:page_id], query[:sql]]
end
