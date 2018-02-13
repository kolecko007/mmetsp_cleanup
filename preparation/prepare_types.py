#!/usr/bin/python2.7

from optparse import OptionParser

from lib.metadata import *
from lib.predefined_types_manager import *
from lib.seq_id import *

parser = OptionParser(description="Add predefined types and metadata information to types")
parser.add_option("--predefined_types", default='data/predefined_types.csv')
parser.add_option("--metadata", default='data/datasets_metadata.json')
parser.add_option("--seq_ids", default='data/seq_ids.csv')
parser.add_option("--input")
parser.add_option("--output", default='data/final_types.csv')
(options, args) = parser.parse_args()

def predefined_type(left_id, right_id):
  return PredefinedTypesManager.get_type(left_id, right_id)

MetadataCollection.load(options.metadata)
PredefinedTypesManager.load(options.predefined_types)
print

TYPES = { 'no': 'NO', 'regular': 'REGULAR', 'close': 'CLOSE' }

SEQ_IDS = {}
for line in open(options.seq_ids).readlines():
  parsed = line.strip().split(',')
  SEQ_IDS[parsed[0]] = SeqId(parsed[1])

with open(options.input) as in_f, open(options.output, 'w') as out_f:
  for line in in_f.readlines():
    parsed = line.strip().split(',')

    left_meta = MetadataCollection.find_by_id(parsed[0])
    right_meta = MetadataCollection.find_by_id(parsed[1])

    left_seq_id = SEQ_IDS[parsed[0]]
    right_seq_id = SEQ_IDS[parsed[1]]

    new_type = parsed[3]

    if left_meta.has_equal_genus_to(right_meta) or left_seq_id.has_equal_geus_species_to(right_seq_id):
      new_type = TYPES['no']
    elif left_meta.has_equal_taxon_class_to(right_meta):
      new_type = TYPES['close']

    parsed[3] = new_type
    out_f.write("%s\n" % ','.join(parsed))

    # left eats right, but regular by predefined (see predefined_or_regular.txt)!
    # else:
    #   predefined = predefined_type(parsed[0], parsed[1])
    #   if predefined and predefined != parsed[3]:
    #     log_args = (predefined, parsed[0], parsed[1], parsed[3])
    #     print "PREDEFINED type %s for %s and %s (was %s)" % log_args


