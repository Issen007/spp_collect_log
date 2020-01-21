from spp_cleanup import get_filelist
import subprocess



def main():
    files_list = get_filelist()
    #file = 'logs/spp_log_192.168.99.81_20191003-031515.log'
    #subprocess.call('python ./spp_collect_log.py --upload-only yes --filename {}'.format(file))
    for file in files_list:
        print(file)
        subprocess.call('python ./spp_collect_log.py --upload-only yes --filename {}'.format(file), shell=True)

if __name__ == "__main__":
    main()
