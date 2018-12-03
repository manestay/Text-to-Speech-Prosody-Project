import datetime
import os

core_nlp_path = 'stanford-corenlp-full-2018-02-27'
input_table = 'games-data-orig.csv'
old_date = os.path.splitext(input_table)[0][-8:]
date = datetime.date.today().strftime("%Y%m%d")

config = {
  # files
  'core_nlp_path': core_nlp_path,
  'core_nlp_parser':'/stanford-corenlp-3.9.1-sources.jar',
  'core_nlp_model':'/stanford-corenlp-3.9.1-models.jar',
  'java_class_path': "{}*:.".format(core_nlp_path),
  'input_table': input_table,
  'old_table_prefix': 'games-data-{}'.format(old_date),
  'new_table_prefix': 'games-data-{}'.format(date),
  'new_table_name': 'games-data-{}.csv'.format(date),

  # directories
  'glove_dir':'glove/',
  'deps_dir':'deps/deps.words',

  # big table info
  'date': date,

  # embedding features
  'num_clusters':5,
  'emb_dim':200,

  # select column names
  'games_trained_200d':'games_200d',
  'pretrained_deps_300d':'pt_deps_300d'

}
