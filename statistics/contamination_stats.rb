#!/usr/bin/env ruby
require 'securerandom'
require 'slop'
require 'pathname'
require 'ruby-progressbar'

params = Slop.parse do |o|
  o.banner = "Prepare MMETSP datasets for Decross"
  o.string '--datasets_path', '(required) Folder with datasets .fas files'
  o.string '--results_path', '(required) Path of Decross the result folder'
  o.string '--output', '(required) Path for the output file'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end

results_path = File.join(params[:results_path], '')
datasets_path = File.join(params[:datasets_path], '')
output_path = File.join(params[:output])

def count_dataset_contigs(org_id)
  `grep -c '>' #{datasets_path}#{org_id}.fas`
end

files = Dir["#{results_path}*_deleted_stats.csv"]
result = []
pb = ProgressBar.create(title: 'Working with files', starting_at: 0, total: files.count)

files.each do |path|
  org_id = path[/MMETSP\d{4}/]

  clean_path = "#{results_path}#{org_id}_clean.fasta"
  deleted_path = "#{results_path}#{org_id}_deleted.fasta"

  clean_cnt = File.exist?(clean_path) ? `grep -c '>' #{clean_path}`.strip.to_i : 0
  contaminations_cnt = `grep -c '>' #{deleted_path}`.strip.to_i
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

  contigs_cnt = count_dataset_contigs(org_id)

  pb.increment
  result << [org_id, contigs_cnt, clean_cnt, contaminations_cnt, food_cnt, other_cnt].join(',')
end

File.open(output_path, 'w') do |f|
  f.puts('mmetsp_id,contigs,clean,dirty,food,other')
  result.each { |e| f.puts(e) }
end


