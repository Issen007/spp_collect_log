#!/usr/bin/env python
import argparse
import boto3 as boto3

def set_configuration():
    # Get Access Key and Secret Key
    if a.access_key and a.secret_key:
        access_key = a.access_key
        secret_key = a.secret_key
    else:
        try:
            from config import access_key, secret_key
        except:
            problem('access_key or secret_key')
            raise SystemExit()

    # Get Communcation Method https or http
    try:
        commMethod = a.commMethod + '://'
    except:
        commMethod = 'https://'

    # Get URL and set full URL
    if a.url:
        url = commMethod + a.url
    else:
        try:
            from config import address
            url = commMethod + address
        except:
            problem('URL (--url s3.company.com)')
            raise SystemExit()

    # Get Bucket Name
    if a.bucket:
        bucket = a.bucket
    else:
        try:
            from config import bucket
        except:
            problem('bucket')
            raise SystemExit()

    if a.remote:
        remote_directory = a.remote
    else:
        remote_directory = None

    if a.local:
        local_directory = a.local
    else:
        local_directory = None

    return (access_key, secret_key, url, bucket, remote_directory, local_directory)

def download_file(access_key, secret_key, filename, url, bucket, remote_directory, local_directory):
    s3_client = s3_client_connect(access_key, secret_key, url)
    if local_directory is not None:
        local_filename = local_directory + '/' + filename
    else:
        local_filename = filename

    if remote_directory is not None:
        remote_filename = remote_directory + '/' + filename
    else:
        remote_filename = filename

    try:
        with open('{}'.format(local_filename), 'wb') as f:
            s3_client.download_fileobj(bucket, remote_filename, f)
        print('Download finished of file {filename}'.format(**locals()))
    except:
        print('Download failed to download {filename}'.format(**locals()))

def delete_file(access_key, secret_key, filename, url, bucket, remote_directory):
    s3 = s3_connect(access_key, secret_key, url)

    if remote_directory is not None:
        remote_filename = remote_directory + '/' + filename
    else:
        remote_filename = filename
    #try:
    s3obj = s3.Object(bucket, remote_filename).delete()
    print('Deleted file ' + remote_filename)
    #except:
    #    print('Failed to delete file ' + remote_filename)

def upload_file(access_key, secret_key, url, filename, bucket, remote_directory, local_directory):
    s3 = s3_connect(access_key, secret_key, url)
    if local_directory is not None:
        local_filename = local_directory + '/' + filename
    else:
        local_filename = filename

    if remote_directory is not None:
        remote_filename = remote_directory + '/' + filename
    else:
        remote_filename = filename

    try:
        s3.meta.client.upload_file(local_filename, bucket, remote_filename)
        print('Upload finised for file {filename}'.format(**locals()))
    except:
        print('Unable to upload file {filename}'.format(**locals()))

def list_file(access_key, secret_key, url, bucket,directory):
    s3 = s3_connect(access_key, secret_key, url)
    s3_bucket = s3.Bucket(name = bucket)
    for file in s3_bucket.objects.all():
        print(file)

def s3_client_connect(access_key, secret_key, url):
    return(boto3.client('s3', aws_access_key_id = access_key, aws_secret_access_key = secret_key, endpoint_url = url))

def s3_connect(access_key, secret_key, url):
    return (boto3.resource('s3', aws_access_key_id = access_key, aws_secret_access_key = secret_key, endpoint_url = url))

def problem(error):
    print("You haven't specify {error}".format(**locals()))
    print("Please you the --help for more information")

def main():
    access_key, secret_key, url, bucket, remote_directory, local_directory = set_configuration()
    if a.filename and a.download:
        download_file(access_key, secret_key, a.filename, url, bucket, remote_directory, local_directory)
    elif a.filename and a.delete:
        delete_file(access_key, secret_key, a.filename, url, bucket, remote_directory)
    elif a.filename and a.upload:
        upload_file(access_key, secret_key, url,a.filename, bucket, remote_directory, local_directory)
    else:
        list_file(access_key, secret_key, url, bucket, remote_directory)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description='''Upload and download files from a COS server''',
        epilog='''Contact support@cristie.se'''
    )
    g = p.add_mutually_exclusive_group(required = False)
    p.add_argument("--access-key", help = "Your access key")
    p.add_argument("--secret-key", help = "Your secret key")
    p.add_argument("--bucket", help="The bucket name. Default: CristieFTP")
    g.add_argument("--upload", action="store_true")
    g.add_argument("--download", action = "store_true")
    g.add_argument("--delete", action = "store_true")
    p.add_argument("--commMethod", default="https", help="Change this value if not https, by typing --commMethod=http")
    p.add_argument("--url", help = "The URL to the COS e.g. s3.company.com")
    #g.add_argument("--list", action = "store_true")
    p.add_argument("--remote", "-D", help = "Remote directory at the S3 Storage")
    p.add_argument("--local", "-d", help = "Local directory on your host")
    p.add_argument("--filename", help = "The filename to upload or download")
    a = p.parse_args()
    main()
