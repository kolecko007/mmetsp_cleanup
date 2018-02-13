### Represents SeqId
## Compares names of orasisms by exact exuality and hardcoded rules
## org = SeqId('gnl|Bigelowiella_natans_Strain_CCMP_2755|MMETSP0045-20121206|16598')
## org.db_id => 'MMETSP0045'
## org.genus_species => 'Bigelowiella natans'

class SeqId:
  UNKNOWN_PREFIXES = ['Genus nov', 'non described', 'NY0313808BC1', 'Undescribed']
  IDENTICAL_DATASETS = [['MMETSP0119', 'MMETSP0121'], ['MMETSP0121', 'MMETSP0119'],
                        ['MMETSP0118', 'MMETSP0121'], ['MMETSP0121', 'MMETSP0118'],
                        ['MMETSP1089', 'MMETSP0308'], ['MMETSP0308', 'MMETSP1089'],
                        ['MMETSP1451', 'MMETSP0288'], ['MMETSP0288', 'MMETSP1451'],
                        ['MMETSP1377', 'MMETSP1115'], ['MMETSP1115', 'MMETSP1377'],
                        ['MMETSP1377', 'MMETSP1117'], ['MMETSP1117', 'MMETSP1377'],
                        ['MMETSP1377', 'MMETSP1116'], ['MMETSP1116', 'MMETSP1377'],
                        ['MMETSP0595', 'MMETSP1132'], ['MMETSP1132', 'MMETSP0595'],
                        ['MMETSP0595', 'MMETSP1129'], ['MMETSP1129', 'MMETSP0595'],
                        ['MMETSP1130', 'MMETSP0595'], ['MMETSP0595', 'MMETSP1130'],
                        ['MMETSP1433', 'MMETSP0098'], ['MMETSP0098', 'MMETSP1433'],
                        ['MMETSP1131', 'MMETSP0595'], ['MMETSP0595', 'MMETSP1131'],
                        ['MMETSP1433', 'MMETSP0100'], ['MMETSP0100', 'MMETSP1433'],
                        ['MMETSP1433', 'MMETSP0099'], ['MMETSP0099', 'MMETSP1433'],
                        ['MMETSP1470', 'MMETSP1469'], ['MMETSP1469', 'MMETSP1470']]

  def __init__(self, seqid):
    self.seqid = seqid
    self.prepare_names()

  def prepare_names(self):
    splitted = self.seqid.split('|')

    if len(splitted) < 3:
      self.db_id = self.seqid.split('_')[0]
      self.short_seq_name = self.seqid
      self.genus_species = None
    else:
      # MMETSP0045
      self.db_id = splitted[2].split('-')[0].split('_')[0]

      # MMETSP0045-20121206|21405
      self.short_seq_name = '|'.join(splitted[2:])

      # Bigelowiella natans
      genus_species = ' '.join(splitted[1].split('_')[0:2]).strip()
      self.genus_species = None

      if genus_species and not self.name_is_unknown(genus_species):
        self.genus_species = genus_species

  def has_genus_species(self):
    return self.genus_species != None

  def has_equal_geus_species_to(self, other_seq_id):
    if not self.genus_species or not other_seq_id.genus_species:
      return False

    if [self.db_id, other_seq_id.db_id] in self.IDENTICAL_DATASETS:
      return True

    return self.genus_species.lower() == other_seq_id.genus_species.lower()

  def name_is_unknown(self, name):
    for prefix in self.UNKNOWN_PREFIXES:
      if name.startswith(prefix):
        return True
    return False


