import json, re, os

class MetadataCollection():
  organisms_index = None

  @staticmethod
  def find_by_id(idx):
    if idx in MetadataCollection.organisms_index:
      return MetadataCollection.organisms_index[idx]
    else:
      return Metadata('', {})

  @staticmethod
  def find_all_by_genus(genus):
    genus = genus.capitalize()
    return [e for e in MetadataCollection.organisms_index.values() if e.genus() == genus]

  @staticmethod
  def load(file_path):
    if MetadataCollection.organisms_index:
      return True

    print 'Loading Metadata hash...'

    if not os.path.exists(file_path):
      print 'Metadata file not found!'
      MetadataCollection.organisms_index = {}
      return True

    with open(file_path, 'r') as f:
      org_hash = json.loads(f.read())

    organisms = [Metadata(k, v) for k, v in org_hash.iteritems()]
    MetadataCollection.organisms_index = { e.org_id: e for e in organisms }

    return True

### Represents organism metadata by its db id (MMETSPXXXX)
## Compares orasism genus by metadata information
class Metadata():
  UNKNOWN_LEXEMS = ['unidentified', 'non described', 'genus nov.', 'unid.', 'unid', 'unknown']

  def __init__(self, org_id, org_hash):
    self.org_id = org_id.split('.')[0]
    self.org_hash = org_hash
    self.prepare_attributes()

  def full_name(self):
    return ' '.join([self.genus(), self.species()]).strip()

  def description(self):
    return self.fetch_value('specimen', 'sample_description')

  def genus(self):
    genus = self.fetch_value('taxon', 'genus')

    if not genus:
      return ''

    return genus.capitalize()

  def taxon_class(self):
    taxon_class = self.fetch_value('taxon', 'class')

    if not taxon_class:
      return ''

    return taxon_class.capitalize()

  def species(self):
    return self.fetch_value('taxon', 'species') or ''

  def prey_genus(self):
    prey_str = self.prey_organisms_string()

    if not prey_str or prey_str.strip() == '':
      return []

    stop_genus = ['none', 'n/a', 'na']
    if len([e for e in stop_genus if prey_str == e]) > 0:
      return []

    splitted = map(lambda x: x.strip(), re.split('\s?,\s|\sand\s', prey_str))
    stop_words = ['mixed', 'bacteria', 'diatoms', 'algae']
    filtered = [e for e in splitted if len([w for w in stop_words if w in e]) == 0 and not e.capitalize().startswith('Ccmp')]
    return map(lambda x: x.capitalize(), [re.split('\s+', e)[0] for e in filtered])

  def prey_organisms_string(self):
    return self.fetch_value('biological parameter', 'prey_organism_if_applicable')

  def fetch_value(self, category, attr_type):
    if category not in self.attributes or attr_type not in self.attributes[category]:
      return None
    try:
      result = str(self.attributes[category][attr_type])
    except UnicodeEncodeError:
      result = ''
    return result.lower()

  def is_prey_for(self, other_metadata):
    return self.genus() in other_metadata.prey_genus()

  def has_equal_genus_to(self, other_metadata):
    return self.has_equal_attr_to(other_metadata, 'genus')

  def has_equal_taxon_class_to(self, other_metadata):
    return self.has_equal_attr_to(other_metadata, 'taxon_class')

  def has_detected_attr(self, attr_name):
    val = getattr(self, attr_name)()
    return val and len(val) != 0 and val.lower() not in self.UNKNOWN_LEXEMS

  def has_equal_attr_to(self, other_metadata, attr_name):
    if self.has_detected_attr(attr_name) and other_metadata.has_detected_attr(attr_name):
      if getattr(self, attr_name)().strip().lower() == getattr(other_metadata, attr_name)().strip().lower():
        return True

    return False

  def prepare_attributes(self):
    self.attributes = {}

    if 'attributes' not in self.org_hash:
      return None

    for attr in self.org_hash['attributes']:
      if attr['category'] not in self.attributes:
        self.attributes[attr['category']] = {}

      self.attributes[attr['category']][attr['type']] = attr['value']

