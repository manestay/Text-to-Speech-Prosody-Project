#  phons2words.py

import sys,re,glob

out_name = "./tri3_cleaned_tongji_all/pron_alignment.txt"
pron_ali=open(out_name,'w')
pron=[]

filename = "./tri3_cleaned_tongji_all/final_alignment.txt"

with open(filename) as f:
    header = True
    pron_ali.write('\n')
    for line in f:
        if header:
            header = False
            continue
        line=line.split("\t")
        file= line[1]
        file = file.strip()
        phone = line[6]

        if phone in set(['spn', 'sil']):
            start=line[9]
            end=line[10]
            pron.append(phone)
            pron_ali.write(file + '\t' + ' '.join(pron) +'\t'+ str(start) + '\t' + str(end))
            pron=[]
        elif len(phone) > 2 and phone[-2] == '_': # final
            end=line[10]
            pron.append(phone)
            pron_ali.write(file + '\t' + ' '.join(pron) +'\t'+ str(start) + '\t' + str(end))
            pron=[]
        else: # initial
            end = sys.maxsize # should never write this
            start=line[9]
            pron.append(phone)
        if float(start) > float(end):
            import pdb; pdb.set_trace()

print('wrote to', out_name)
