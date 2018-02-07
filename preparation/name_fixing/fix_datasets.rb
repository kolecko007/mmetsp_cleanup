#!/usr/bin/env ruby

require 'slop'
require 'pathname'
require 'fileutils'
require 'ruby-progressbar'

params = Slop.parse do |o|
  o.banner = "Prepare MMETSP datasets for Decross"
  o.string '--wrong_names_path', 'wrong names .csv file'
  o.string '--datasets_path', 'folder with .fas files'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end

lines = File.open(params[:wrong_names_path]).readlines

pb = ProgressBar.create(title: 'Fixing fasta', starting_at: 0, total: lines.count)

lines.each do |line|
  file_name, contig_name = line.strip.split(',')
  file_path = File.join(params[:datasets_path], "#{file_name}.fas")
  raise "File #{file_path} not exists" unless File.exists?(file_path)

  `pru 'gsub("#{contig_name}", "#{file_name}")' -i #{file_path}`

  pb.increment
end

