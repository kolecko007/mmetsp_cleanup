#!/usr/bin/env ruby

require 'slop'
require 'pathname'
require 'fileutils'
require 'ruby-progressbar'
require 'pry'

params = Slop.parse do |o|
  o.banner = "Prepare MMETSP one vs all hits for Decross. Files are sorted before the sed."
  o.string '--wrong_names_path', 'wrong names .csv file'
  o.string '--hits_path', 'folder with .fas files'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end

names = File.open(params[:wrong_names_path])
            .readlines
            .map{ |l| l.strip.split(',')[1] }

search_query = names.join('\|')
paths = Dir["#{File.join(params[:hits_path], '')}*.blastab"].sort

paths.each_slice(1000) do |group|
  result = `grep '#{search_query}' #{group.join(' ')}`

  unless result.empty?
    puts "problem: #{result}"
    exit(0)
  end
end

puts 'Everything is OK'
