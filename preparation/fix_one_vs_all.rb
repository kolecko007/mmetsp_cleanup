#!/usr/bin/env ruby

require 'slop'
require 'pathname'
require 'fileutils'
require 'ruby-progressbar'
require 'pry'
require 'parallel'

params = Slop.parse do |o|
  o.banner = "Prepare MMETSP one vs all hits for Decross. Files are sorted before the sed."
  o.string '--wrong_names_path', 'wrong names .csv file'
  o.string '--one_vs_all_path', 'folder with .fas files'
  o.integer '--threads', 'Number of threads for the proccess'
  o.integer '--files_limit', 'Number of files to proccess (for testing)'
  o.boolean '--reverse', 'Begin from the last file to the first'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end

names = File.open(params[:wrong_names_path]).readlines.map{ |l| l.strip.split(',') }

pru_command = ENV['PRU_EXEC'] || 'pru'
pru_options = "#{names.map { |n| "gsub(\"#{n[1]}\", \"#{n[0]}\")" }.join('.')}"

paths = Dir["#{params[:one_vs_all_path]}/*.blastab"].sort
paths.reverse! if params[:reverse]
paths = paths.first(params[:files_limit]) if params[:files_limit]

thread_num = params[:threads] || 1

pb = ProgressBar.create(title: 'Fixing blastabs', starting_at: 0, total: paths.count)

Parallel.each(paths, in_processes: thread_num) do |path|
  pb.title = File.basename(path)
  `#{pru_command} '#{pru_options}' -i #{path}`

  pb.increment
end
