#!/usr/bin/env python3.6

"""Coverage statistics for contamination simulation

Authors: Serafim Nenarokov, Martin Kolisko.

1. Take query fasta file (clean brucei or giardia)
2. Take BLAST results (6th format)
3. Make csv output: qseqid, length, bh-length, bh-pident

"""


import argparse

from Bio import SeqIO


parser = argparse.ArgumentParser(description="Coverage statistics for contamination simulation")
parser.add_argument("--query",
                    required=True,
                    type=argparse.FileType('r'),
                    help="Fasta file with query")
parser.add_argument("--blast_results",
                    required=True,
                    type=argparse.FileType('r'),
                    help="BLAST results path (6th format)")
parser.add_argument("--output",
                    required=True,
                    type=argparse.FileType('w'),
                    help="output file in .csv format")
arguments = parser.parse_args()


def parse_blast_results(file):
  results = {}

  for line in file.readlines():
    splitted = line.strip().split("\t")

    if splitted[0] not in results:
      results[splitted[0]] = []

    results[splitted[0]].append({ "sseqid": splitted[1], "pident": float(splitted[2]), "hit_len": (int(splitted[7])-int(splitted[6])+1) })

  return results

def filter_best_hit(old_results):
  results = {}

  for key, value in old_results.items():
    results[key] = sorted(value, key=lambda k: [k["hit_len"], k["pident"]])[-1]

  return results

def main():
  blast_results = parse_blast_results(arguments.blast_results)
  blast_results = filter_best_hit(blast_results)

  arguments.output.write(f"qseqid,qlength,hit_length,bh_pident\n")

  for record in SeqIO.parse(arguments.query, "fasta"):
    if record.id in blast_results:
      arguments.output.write(f"{record.id},{len(record.seq)},{blast_results[record.id]['sseqid']},{blast_results[record.id]['hit_len']},{blast_results[record.id]['pident']}\n")
    else:
      arguments.output.write(f"{record.id},{len(record.seq)},-,0,0\n")



if __name__ == '__main__':
    main()
