#!/usr/bin/env ruby
require 'securerandom'
require 'slop'
require 'pathname'
require 'fileutils'
require 'parallel'

# input:
# - fas files
# - all-vs-all .blastab files
# - one-vs-all .blastab files
# output:
# file structure for decross contamination finding

params = Slop.parse do |o|
  o.banner = "Prepare MMETSP datasets for Decross"
  o.string '--datasets_path', '(required) tar archive with .fas files'
  o.string '--one_vs_all_path', '(required) tar archive with one-vs-all .blastab files'
  o.string '--all_vs_all_path', '(required) tar archive with all-vs-all .blastab files'
  o.string '--output_path', '(required) output folder'
  o.integer '-t', '--threads', 'number of threads (32 by default)'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end

input_paths = {
  contigs:    File.join(params[:datasets_path]),
  one_vs_all: File.join(params[:one_vs_all_path]),
  all_vs_all: File.join(params[:all_vs_all_path])
}

out_paths = {
  base:          params[:output_path],
  blast_results: File.join(params[:output_path], 'blast_results', ''),
  contigs:       File.join(params[:output_path], 'datasets', '')
}

out_paths.merge!({
  one_vs_all:    File.join(out_paths[:blast_results], 'one_vs_all', ''),
  all_vs_all:    File.join(out_paths[:blast_results], 'all_vs_all', '')
})

thread_num = params[:threads] || 32
pru_command = ENV['PRU_EXEC'] || 'pru'

`rm -r #{out_paths[:base]}`
out_paths.each{ |k, v| FileUtils.mkpath v }

out_paths[:coverage_db] =  File.join(out_paths[:base], 'db.sql')
out_paths[:system_names] = File.join(out_paths[:base], 'system_names.csv')

puts "Extracting files"
`tar -xf #{input_paths[:contigs]} -C #{out_paths[:contigs]}`
`tar -xf #{input_paths[:one_vs_all]} -C #{out_paths[:one_vs_all]}`
`tar -xf #{input_paths[:all_vs_all]} -C #{out_paths[:all_vs_all]}`


puts "Preparing names dict"
org_id_by_hash = {}
hash_by_org_id = {}

Dir["#{out_paths[:contigs]}*.fas"].each do |path|
  org_id = File.basename(path, File.extname(path))
  hsh = SecureRandom.hex
  org_id_by_hash[hsh] = org_id
  hash_by_org_id[org_id] = hsh
end


puts "Writing names dict"
File.open(out_paths[:system_names], 'w') do |f|
  f.write(org_id_by_hash.map { |hsh, org_id| "#{org_id},#{hsh}\n" }.join)
end


puts "Changing contigs name in datasets"
Dir["#{out_paths[:contigs]}*.fas"].each do |path|
  org_id = File.basename(path, File.extname(path))
  if `uname -s`.strip == 'Darwin'
    `sed -i '' 's#^>#>#{hash_by_org_id[org_id]}_#' #{path}`
  else
    `sed -i 's#^>#>#{hash_by_org_id[org_id]}_#' #{path}`
  end
end


def extract_org_id(contig_id)
  return contig_id[/MMETSP\d+/]
end

def check_ids_validity(line, *names)
  if names.include?(nil)
    raise "ERROR: cannot find hash for hit:\n
           line: #{line},\n #{names.join("\n")}"
  end
end

puts "Changing contig names in one_vs_all BLAST hits"
paths = Dir["#{out_paths[:one_vs_all]}*.blastab"]
Parallel.each(paths, in_processes: thread_num) do |path|
  lines = []
  left_org_id = nil
  left_org_hash = nil

  File.open(path, 'r').each do |line|
    line = line.split("\t")

    left_org_id ||= extract_org_id(line[0])
    right_org_id = extract_org_id(line[1])

    left_org_hash ||= hash_by_org_id[left_org_id]
    right_org_hash = hash_by_org_id[right_org_id]

    check_ids_validity line, left_org_id,
                             right_org_id,
                             left_org_hash,
                             right_org_hash

    line[0] = "#{hash_by_org_id[left_org_id]}_#{line[0]}"
    line[1] = "#{hash_by_org_id[right_org_id]}_#{line[1]}"

    lines << line.join("\t")
  end

  File.open(path, 'w') do |f|
    lines.each { |l| f.write(l) }
  end
end


puts "Changing contig names in all_vs_all BLAST hits"
paths = Dir["#{out_paths[:all_vs_all]}*.blastab"]

Parallel.each(paths, in_processes: thread_num) do |path|
  parts = File.basename(path).split('VS')
  left_org_id, right_org_id = extract_org_id(parts[0]), extract_org_id(parts[1])

  left_org_hash = hash_by_org_id[left_org_id]
  right_org_hash = hash_by_org_id[right_org_id]

  check_ids_validity path, left_org_id,
                           right_org_id,
                           left_org_hash,
                           right_org_hash

  pru_options = "gsub(/(\\A.*#{left_org_id}.*)\\t(.*#{right_org_id})/, \"#{left_org_hash}_\\\\1\\t#{right_org_hash}_\\\\2\")"
  `#{pru_command} '#{pru_options}' -i #{path}`
end

puts "Done!"
