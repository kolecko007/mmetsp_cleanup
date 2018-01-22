#!/usr/bin/env ruby

require 'slop'
require 'pathname'
require 'fileutils'
require 'ruby-progressbar'
require 'pry'

params = Slop.parse do |o|
  o.banner = "Prepare MMETSP one vs all hits for Decross"
  o.string '--wrong_names_path', 'wrong names .csv file'
  o.string '--one_vs_all_path', 'folder with .fas files'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end


names = File.open(params[:wrong_names_path]).readlines.map{ |l| l.strip.split(',') }
pb = ProgressBar.create(title: 'Fixing blastabs', starting_at: 0, total: names.count)

names.each do |n|
  new_name = n[0]
  old_name = n[1]

  Dir["#{params[:one_vs_all_path]}/*.blastab"].each do |path|
    `pru 'gsub("#{old_name}", "#{new_name}")' -i #{path}`
  end

  pb.increment
end
