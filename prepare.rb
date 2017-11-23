#!/usr/bin/env ruby
require 'securerandom'

## System names generation ##

outfile = 'system_names.csv'

File.open(outfile, 'w') do |f|
  Dir['datasets/*.fas'].each do |path|
    org_id = File.basename(path, File.extname(path))
    hsh = SecureRandom.hex
    f.puts("#{org_id},#{hsh}")
  end
end

## Coverage db generation ##
