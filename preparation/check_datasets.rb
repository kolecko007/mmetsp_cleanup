#!/usr/bin/env ruby

require 'slop'
require 'pathname'
require 'fileutils'
require 'ruby-progressbar'

params = Slop.parse do |o|
  o.banner = "Prepare MMETSP datasets for Decross"
  o.string '--datasets_path', 'folder with .fas files'
  o.bool '--display_only', 'do not write results to wrong_names.csv'
  o.string '--wrong_names_path', 'path for wrong_names.csv ("wrong_names.csv" by default)'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end

MMETSP_REGEXP = /MMETSP\w{4,}/

def detect_fas_contig_id(fas_file_path)
  by_filename = fas_file_path[MMETSP_REGEXP]
  by_content = `head -n1 #{fas_file_path}`[MMETSP_REGEXP]

  result = { by_filename: by_filename, by_content: by_content }
  raise "Problem in #{fas_file_path}: #{result}" if result.values.include?(nil)
  result
end

def check_fas_consistency(fas_file_path)
  id = `head -n1 #{fas_file_path}`[MMETSP_REGEXP]
  `grep -c '>' #{fas_file_path}`.to_i == `grep -c '#{id}' #{fas_file_path}`.to_i
end

datasets_path = File.join(params[:datasets_path], '')
paths = Dir["#{datasets_path}*"]
pb = ProgressBar.create(title: 'Checking fasta', starting_at: 0, total: paths.count)

wrong_names = []
inconsistent_fas = []
paths.sort.each do |fas_path|
  pair = detect_fas_contig_id fas_path

  # check, if content of file and filename are equal
  if pair[:by_filename] != pair[:by_content]
    wrong_names << pair
  end

  unless check_fas_consistency(fas_path)
    inconsistent_fas << fas_path
  end

  pb.increment
end

if wrong_names.any?
  if params[:display_only]
    wrong_names.each { |e| puts "Wrong name #{e[:by_filename]}, #{e[:by_content]}" }
  else
    File.open(params[:wrong_names_path] || 'wrong_names.csv', 'w') do |f|
      wrong_names.each { |e| f.puts "#{e[:by_filename]},#{e[:by_content]}" }
    end
  end
elsif inconsistent_fas.any?
  puts "inconsistent: #{inconsistent_fas}"
else
  'Datasets: ok'
end

if wrong_names.any? || inconsistent_fas.any?
  exit 1
else
  exit 0
end
