import os
import shutil
import subprocess

data_dir = 'data_annotation'
flat_dir = 'raw_data'
# if os.path.exists(flat_dir):
#     shutil.rmtree(flat_dir)
os.makedirs(flat_dir, exist_ok=True)
flat_dir_44100 = 'raw_data_44100'
# if os.path.exists(flat_dir_44100):
#     shutil.rmtree(flat_dir_44100)
os.makedirs(flat_dir_44100, exist_ok=True)

f = open('./flat_to_orig_path.txt', 'w')

# basenames = {}
for root, dirnames, filenames in os.walk(data_dir):
    for filename in filenames:
        if not (filename.endswith('TextGrid') or filename.endswith('wav')):
            continue
        source = os.path.join(root, filename)
        file_id, ext = os.path.splitext(filename)
        recording_no, spk_str = file_id.split('_', 1)
        session = root.rsplit('/')[-2]
        if spk_str.startswith('有控制') or spk_str.startswith('无控制'):
            spk_str1 = spk_str
            control, rest = spk_str.split('_', 1)
            spk_str = '{}_{}'.format(rest, control)
        key = '{}--{}--{}{}'.format(spk_str, recording_no, session, ext)
        f.write('{}\t{}\n'.format(key, source))
        # dest_44100 = os.path.join(flat_dir_44100, key)
        # dest_8000 = os.path.join(flat_dir, key)
        # shutil.copy(source, dest_44100)
        # if filename.endswith('wav'):
        #     cmd = 'sox {} {} rate -L -s 8000'.format(dest_44100, dest_8000)
        #     print(cmd)
        #     subprocess.Popen(cmd, shell=True)
        # if not key in basenames:
        #     basenames[key] = []
        # basenames[key].append(root)
        # if len(basenames[key]) > 1:
        #     print(key, basenames[key])
f.close()
