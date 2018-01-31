#!/usr/bin/env ruby

require 'pathname'
require 'slop'
require 'sqlite3'
require 'ruby-progressbar'

# Datasets must be prepared

params = Slop.parse do |o|
  o.banner = "Prepare coverage database for MMETSP"
  o.string '--old_db_path', '(required) .sql file with an old database'
  o.string '--new_db_path', '(required) .sql file with a new prepared database'
  o.string '--datasets_path', '(required) folder with prepared *.fas files (with system names)'
  o.on '-h', '--help', 'Print options' do
    puts o
    exit
  end
end

def get_contig(db, org_name)
  db.execute("SELECT * from `coverage_entries` where `org_name` = '#{org_name}'").first
end

`rm #{params[:new_db_path]}` if Pathname.new(params[:new_db_path]).exist?

datasets_path = File.join(params[:datasets_path], '')

old_db = SQLite3::Database.new params[:old_db_path]
new_db = SQLite3::Database.new params[:new_db_path]

new_db.execute <<-SQL
  CREATE TABLE IF NOT EXISTS `coverage_entries` (
    `contig_id` char[256] NOT NULL,
    `rpkm` float NOT NULL,
    PRIMARY KEY (`contig_id`))
SQL

fas_files = Dir["#{datasets_path}*.fas"]
pb = ProgressBar.create(title: 'Working with database', starting_at: 0, total: fas_files.count)

fas_files.each do |path|
  new_db.transaction

  `grep '>' #{path}`.split("\n").map(&:strip).each do |line|
    new_contig_id = line.gsub('>', '')
    old_db_id = new_contig_id[/MMETSP.+$/]
    contig = get_contig(old_db, old_db_id)

    if contig
      command = "INSERT INTO `coverage_entries` (`contig_id`, `rpkm`) VALUES ('#{new_contig_id}', #{contig[1]})"
      new_db.execute(command)
    end
  end

  new_db.commit
  pb.increment
end
