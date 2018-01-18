#!/usr/bin/env ruby
require 'securerandom'
require 'slop'
require 'pathname'
require 'fileutils'

# input:
# - fas files
# - all-vs-all .blastab files
# - one-vs-all .blastab files
# output:
# file structure for decross contamination finding

params = Slop.parse do |o|
  o.banner = "Prepare MMETSP datasets for Decross"
  o.string '--contigs_path', '(required) tar archive with .fas files'
  o.string '--one_vs_all_path', '(required) tar archive with one-vs-all .blastab files'
  o.string '--all_vs_all_path', '(required) tar archive with all-vs-all .blastab files'
  o.string '--output_path', '(required) output folder'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end

input_paths = {
  contigs:    File.join(params[:contigs_path]),
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

`rm -r #{out_paths[:base]}`
out_paths.each{ |k, v| FileUtils.mkpath v }

out_paths[:coverage_db] =  File.join(out_paths[:base], 'db.sql')
out_paths[:system_names] = File.join(out_paths[:base], 'system_names.csv')

puts "Extracting files"
`tar -xvf #{input_paths[:contigs]} -C #{out_paths[:contigs]}`
`tar -xvf #{input_paths[:one_vs_all]} -C #{out_paths[:one_vs_all]}`
`tar -xvf #{input_paths[:all_vs_all]} -C #{out_paths[:all_vs_all]}`


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


puts "Changing contigs name in BLAST hits"
Dir["#{out_paths[:contigs]}*.fas"].each do |path|
  org_id = File.basename(path, File.extname(path))
  if `uname -s`.strip == 'Darwin'
    `sed -i '' 's#^>#>#{hash_by_org_id[org_id]}_#' #{path}`
  else
    `sed -i 's#^>#>#{hash_by_org_id[org_id]}_#' #{path}`
  end
end

paths = Dir["#{out_paths[:one_vs_all]}*.blastab", "#{out_paths[:all_vs_all]}*.blastab"]


puts "Changing contig names in BLAST hits"
def extract_org_id(contig_id)
  return contig_id[/MMETSP\d+/]
end

paths.each do |path|
  lines = []

  File.open(path, 'r').each do |line|
    line = line.split("\t")

    org_1_id = extract_org_id(line[0])
    org_2_id = extract_org_id(line[1])

    if !org_1_id || !org_2_id
      raise "ERROR: cannot find org_id for hit: #{line[0]} (#{org_1_id || 'not found'}), #{line[1]} (#{org_2_id} || 'not found')"
    end

    org_1_hsh = hash_by_org_id[org_1_id]
    org_2_hsh = hash_by_org_id[org_2_id]

    if !org_1_hsh || !org_2_hsh
      raise "ERROR: cannot find hash for hit: #{org_1_id} (#{org_1_hsh || 'not found'}), #{org_2_id} (#{org_2_hsh || 'not found'})"
    end

    line[0] = "#{hash_by_org_id[org_1_id]}_#{line[0]}"
    line[1] = "#{hash_by_org_id[org_2_id]}_#{line[1]}"

    lines << line.join("\t")
  end

  File.open(path, 'w') do |f|
    lines.each { |l| f.write(l) }
  end
end

puts "Done!"
