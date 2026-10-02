require "jekyll"

Liquid::Template.register_filter(Jekyll::Filters)
template = Liquid::Template.parse(File.read(File.expand_path("../_includes/post-content.html", __dir__)))

render = lambda do |markdown|
  html = Kramdown::Document.new(markdown, input: "GFM").to_html
  template.render!({ "include" => { "html" => html }, "page" => { "title" => "Article" }, "display_title" => "Article" })
end

checks = {
  "two H2s omit TOC" => lambda do
    output = render.call("Introduction.\n\n## One\n\nText.\n\n## Two\n\nText.")
    !output.include?('class="post-toc"') && output.scan(/<h2 /).size == 2
  end,
  "three H2s generate links after introduction" => lambda do
    output = render.call("Introduction.\n\n## One\n\n## Two\n\n## Three")
    output.index("Introduction.") < output.index('class="post-toc"') &&
      output.scan(/href="#/).size == 3 && output.include?('href="#three"')
  end,
  "code examples do not count as headings" => lambda do
    output = render.call("Introduction.\n\n## One\n\n```html\n<h2 id=\"fake\">Fake</h2>\n```\n\n## Two")
    !output.include?('class="post-toc"') && output.include?("&lt;h2")
  end,
  "duplicate body title leaves introduction intact" => lambda do
    output = render.call("# Article\n\nIntroduction.\n\n## One\n\n## Two\n\n## Three")
    !output.include?("<h1") && !output.include?(">Article</h2>") && output.scan(/Introduction\./).size == 1
  end,
  "heading labels preserve code, entities and line breaks" => lambda do
    output = render.call("Introduction.\n\n## `main` & dev<br>branch\n\n## Two\n\n## Three")
    output.include?("main &amp; dev branch</a>") && !output.include?("&amp;amp;")
  end,
  "legacy opening paragraph becomes introduction" => lambda do
    output = render.call("## One\n\nIntroduction.\n\nRemaining text.\n\n## Two\n\n## Three")
    output.index("Introduction.") < output.index('class="post-toc"') &&
      output.index('class="post-toc"') < output.index('<h2 id="one"') &&
      output.scan(/Introduction\./).size == 1 && output.include?("Remaining text.")
  end
}

checks.each do |name, check|
  raise "FAILED: #{name}" unless check.call
  puts "PASS: #{name}"
end
