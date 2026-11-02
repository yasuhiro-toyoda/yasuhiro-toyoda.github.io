require "jekyll"
require "jekyll-feed"
require "tmpdir"
require "fileutils"
require "rexml/document"

root = File.expand_path("..", __dir__)
original_tz = ENV["TZ"]
# Midnight, UTC/JST day boundary, month boundary and year boundary.
dates = ["2026-01-01 00:00:00", "2026-04-01 00:01:00", "2026-04-16 08:59:59",
         "2026-04-16 09:00:00", "2026-04-30 23:59:59"]

begin
  ["UTC", "Asia/Tokyo"].each do |host_tz|
    ENV["TZ"] = host_tz
    Dir.mktmpdir("publication-dates-") do |tmp|
      source = File.join(tmp, "source")
      FileUtils.mkdir_p(File.join(source, "_posts"))
      %w[_layouts _includes].each { |dir| FileUtils.cp_r(File.join(root, dir), source) }
      dates.each_with_index do |date, i|
        File.write(File.join(source, "_posts", "#{date[0, 10]}-boundary-#{i}.md"), <<~POST)
          ---
          layout: post
          title: "Boundary #{i}"
          date: #{date} +0900
          ---
          Introduction.

          ## Section

          Content.
        POST
      end
      # Load the real config: removing timezone must fail even on a UTC host.
      config = Jekyll.configuration("config" => File.join(root, "_config.yml"),
                                    "source" => source, "destination" => File.join(tmp, "site"),
                                    "quiet" => true)
      site = Jekyll::Site.new(config)
      site.process
      dates.each_with_index do |date, i|
        url = "/blog/#{date[0, 10].tr('-', '/')}/boundary-#{i}/"
        html = File.read(File.join(site.dest, url.delete_prefix("/"), "index.html"))
        expected = Time.new(*date.split(/[- :]/).map(&:to_i), "+09:00")
        display = expected.strftime("%Y年%-m月%-d日")
        raise "Wrong date/offset: #{host_tz} #{date}" unless html.include?(%(<time datetime="#{expected.xmlschema}">#{display}</time>))
        raise "Wrong canonical: #{host_tz} #{date}" unless html.include?(%(rel="canonical" href="https://musashistudio.com#{url}"))
      end
      feed = REXML::Document.new(File.read(File.join(site.dest, "feed.xml")))
      entries = REXML::XPath.match(feed, "//a:entry", "a" => "http://www.w3.org/2005/Atom")
      raise "Missing fixture feed entries" unless entries.size == dates.size
      entries.each do |entry|
        published = REXML::XPath.first(entry, "a:published", "a" => "http://www.w3.org/2005/Atom").text
        raise "Feed timezone differs: #{host_tz}" unless published.end_with?("+09:00")
        day = published[0, 10].tr("-", "/")
        link = REXML::XPath.first(entry, "a:link", "a" => "http://www.w3.org/2005/Atom").attributes["href"]
        raise "Feed URL/date differ: #{host_tz}" unless link.include?("/blog/#{day}/")
      end
      puts "PASS: JST dates, URLs, canonical and feed at #{dates.size} boundaries with host TZ=#{host_tz}"
    end
  end
ensure
  ENV["TZ"] = original_tz
end
