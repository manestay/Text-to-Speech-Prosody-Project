
'''
Runs coreference resolution on data and generates all coreference features:

Coreference_IDs
Most_Recent_Mention
Recent_Explicit_Mention
Recent_Implicit_Mention
Most_Recent_Mention_PoS
Recent_Explicit_Mention_PoS
Recent_Implicit_Mention_PoS
Number_Of_Coref_Mentions
Number_Of_Explicit_Mentions
Number_Of_Implicit_Mentions
Most_Recent_Mention_Syntactic_Function
Recent_Explicit_Mention_Syntactic_Function
Recent_Implicit_Mention_Syntactic_Function
Far_Back_Mention

'''
import run_stanford
import add_new_columns
import combine_session_tables
from example_config import config

DATE = config['date']
CSV_EXTENSION = '.csv'
SUFFIX = config['combine_suffix']
PREFIX = config['old_table_prefix']
NEW_PREFIX = config['new_table_prefix']

if __name__ == '__main__':

  print ("Generating xml trees and session-differentiated csv tables....." + 
         "\nStoring in directories 'xml/' and 'csv/.....'")
  run_stanford.main()

  print ("Generating mention features for each session-differentiated csv table....." + 
         "\nStoring in directory 'csv_mentions/.....'")
  add_new_columns.main(PREFIX,SUFFIX)

  print ("Combining session-csv files tables in table burnc-{}{}".format(DATE,CSV_EXTENSION))
  combine_session_tables.main(NEW_PREFIX)

  print ("Closing....." + "\nAll mention features have been generated.")