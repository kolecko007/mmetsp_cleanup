import csv, os

class PredefinedTypesManager:
  types_dict = None

  @staticmethod
  def load(file_path):
    if PredefinedTypesManager.types_dict:
      return True

    if not os.path.exists(file_path):
      return True

    with open(file_path, 'r') as f:
      print 'Loading predefined types...'
      result = {}

      for row in csv.reader(f):
        val = row[8].upper()

        if val == 'SAME':
          val = 'NO'

        key = tuple(sorted([row[0], row[1]]))

        if key in result:
          if result[key] == 'CLOSE' and val == 'NO':
            result[key] = val

          elif [result[key], val].count('REGULAR') == 1:
            if val != 'REGULAR':
              result[key] = val
        else:
          result[key] = val

    PredefinedTypesManager.types_dict = result
    print 'Loaded'

    return True

  @staticmethod
  def get_type(left, right):
    key = tuple(sorted([left, right]))

    if key in PredefinedTypesManager.types_dict:
      return PredefinedTypesManager.types_dict[key]
