import os
import sys
sys.path.insert(0, '..')          # import local sppclient, not global under user site package
import time
import traceback

def get_filelist():
    list_path = (os.getcwd() + '/logs/')
    list = []
    for root, dirs, files in os.walk(r'{list_path}'.format(**locals())):
        for file in files:
            if file.endswith('.log'):
                list.append(list_path + file)

    return(list)

def inplace_change(filename, old_string, new_string):
    with open(filename, 'r') as f:
        s = f.read()
        if old_string not in s:
            print('{old_string} not found in {filename}.'.format(**locals()))
            return

    with open(filename, 'r+') as f:
         f.read()
         print('Changing {old_string} to {new_string} in {filename}'.format(**locals()))
         s = s.replace(old_string, new_string)
         f.write(s)

    with open(filename, 'r+') as f:
         f.read()
         old_string = '""' + s + '""'
         print('Changing {old_string} to {new_string} in {filename}'.format(**locals()))
         s = s.replace(old_string, new_string)
         f.write(s)

def cleanup_log(filename):
    # tr "'" '"' <spp_log_192.168.99.81_20190919-133113.log > outfile.log
    # None was without double quotes
    # cat outfile.log | sed 's/None/"None"/g' > outfile2.log
    # True was without double quotes
    # cat outfile2.log | sed 's/True/"True"/g' > outfile3.log
    # False was without double quotes
    # cat outfile3.log | sed 's/False/"False"/g' > outfile4.log
    #string = [None]
    inplace_change(filename, 'None', '"None"')
    inplace_change(filename, 'True', '"True"')
    inplace_change(filename, 'False', '"False"')

def main():
    saved_files = get_filelist()
    for file in saved_files:
        print('Start cleaning up log {file}'.format(**locals()))
        cleanup_log(file)


if __name__ == "__main__":
    main()
