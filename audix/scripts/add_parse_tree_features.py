"""
Extract features from parse trees and add columns to big table.

@author: Rose Sloan
"""

import argparse
import csv
from example_config import config
from nltk.tree import Tree
import string

TABLE_NAME = config['new_table_name']
parser = argparse.ArgumentParser()
parser.add_argument('--table', help='table to add columns to', default=TABLE_NAME)
parser.add_argument('--new-table', help='name of new table', default=TABLE_NAME)

def main(table_name='', new_table_name=''):
    args = parser.parse_args()
    table_name = table_name or args.table
    new_table_name = new_table_name or args.new_table
    bigtable = open(table_name, 'r')
    reader = csv.DictReader(bigtable)

    newfields = ['tree_depth', 'tree_width', 'word_depth', 'constituent_width', 'constituent_label', 'constituent_forward_position', 'constituent_backward_position',
    'next_word_spanning_tree', 'next_word_spanning_depth', 'next_word_spanning_width', 'next_word_spanning_label',
    'coreference_spanning_tree', 'coreference_spanning_depth', 'coreference_spanning_width', 'coreference_spanning_label']
    fieldnames = reader.fieldnames + newfields
    writer = csv.DictWriter(open(new_table_name, 'w'), fieldnames=fieldnames)
    writer.writeheader()
    prevparse = None
    prevcoref = None
    prevcoreftree = None

    for row in reader:
        #print(row['utt_id'])
        parse = row['parse_tree']
        if len(parse.strip()) == 0:
            writer.writerow(row)
            continue

        if parse != prevparse:
            parsetree = Tree.fromstring(parse)
            corefs = dict()
            ind = 0
            prevparse = parse
        else:
            ind += 1
            prevind = ind
        try:
            while not (row['word'].lower()).startswith((parsetree.leaves()[ind].lower().strip('.'))):
                ind += 1
        except IndexError:
            writer.writerow(row)
            ind = prevind
            continue

        newrow = row
        newrow['tree_depth'] = parsetree.height()
        newrow['tree_width'] = len(parsetree.leaves())
        const = parsetree[parsetree.leaf_treeposition(ind)[:-2]]
        newrow['word_depth'] = len(parsetree.leaf_treeposition(ind))
        newrow['constituent_width'] = len(const.leaves())
        newrow['constituent_label'] = const.label()

        newrow['constituent_forward_position'] = 0
        if parsetree.leaf_treeposition(ind)[-2] > 0:
            for i in range(parsetree.leaf_treeposition(ind)[-2]):
                newrow['constituent_forward_position'] += len(const[i].leaves())
        newrow['constituent_backward_position'] = len(const.leaves()) - newrow['constituent_forward_position'] - 1

        if ind < len(parsetree.leaves()) - 2 and (parsetree.leaves()[ind+1][0] in string.punctuation or parsetree.leaves()[ind+1][0] == "n't"):
            spantree = parsetree[parsetree.treeposition_spanning_leaves(ind, ind+3)]
        elif ind < len(parsetree.leaves()) - 1:
            spantree = parsetree[parsetree.treeposition_spanning_leaves(ind, ind+2)]
        else:
            spantree = parsetree

        newrow['next_word_spanning_tree'] = ' '.join(str(spantree).split())
        newrow['next_word_spanning_label'] = spantree.label()
        newrow['next_word_spanning_width'] = len(spantree.leaves())
        newrow['next_word_spanning_depth'] = spantree.height()

        coref = row['Coreference_IDs']
        if len(coref.strip()) == 0:
            prevcoref = None
            prevcoreftree = None
            coreftree = None
        elif coref == prevcoref: #contiguous things with the same ID are probably the same
            coreftree = prevcoreftree
        elif coref in corefs.keys():
            prevpos = corefs[coref]
            coreftree = parsetree[parsetree.treeposition_spanning_leaves(prevpos, ind+1)]
            prevcoref = coref
            prevcoreftree = coreftree
            corefs[coref] = ind
        else:
            coreftree = None
            prevcoref = coref
            prevcoreftree = coreftree
            corefs[coref] = ind

        if coreftree:
            newrow['coreference_spanning_tree'] = coreftree.pformat(margin = 1000)
            newrow['coreference_spanning_label'] = coreftree.label()
            newrow['coreference_spanning_width'] = len(coreftree.leaves())
            newrow['coreference_spanning_depth'] = coreftree.height()
        writer.writerow(newrow)

if __name__ == '__main__':
    main()
