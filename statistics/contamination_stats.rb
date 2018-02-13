#!/usr/bin/env ruby
require 'securerandom'
require 'slop'
require 'pathname'
require 'fileutils'

params = Slop.parse do |o|
  o.banner = "Prepare MMETSP datasets for Decross"
  o.string '--results_path', '(required) Path of Decross the result folder'
  o.string '--output', '(required) Path for the output file'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end

results_path = File.join(params[:results_path], '')
output_path = File.join(params[:output])

files = Dir["#{results_path}*_deleted_stats.csv"]
result = []

files.each do |path|
  org_id = path[/MMETSP\d{4}/]

  clean_cnt = `grep -c '>' #{results_path}#{org_id}_clean.fasta`.strip.to_i
  food_cnt = 0
  other_cnt = 0

  File.open(path).readlines().each do |l|
    type = l.strip.split(',')[-2]
    if type == 'LEFT_EATS_RIGHT'
      food_cnt += 1
    else
      other_cnt += 1
    end
  end

  result << [org_id, clean_cnt, food_cnt, other_cnt].join(',')
end

File.open(output_path, 'w') do |f|
  f.puts('mmetsp_id,clean,food,other')
  result.each { |e| f.puts(e) }
end


