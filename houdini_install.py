import sys, re, os, argparse
try:
    import requests
except ImportError:
    print('This script require requests module.\n Install: pip install requests')
    sys.exit()

username = ''
password = ''
if not username or not password:
    print('Please set username and password')
    print('Example: -u username -p password')
    sys.exit()

tmp_folder = os.path.expanduser('~/temp_houdini')

############################################################# START #############

# define OS
category = 'linux'

# create client
client = requests.session()
# Retrieve the CSRF token first
URL = 'https://www.sidefx.com/login/'
print('Login on %s ...' % URL)
client.get(URL)  # sets cookie
csrftoken = client.cookies['csrftoken']
# create login data
login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='/')
# login
r = client.post(URL, data=login_data, headers=dict(Referer=URL))

# goto daily builds page
print('Get last build version...')
page = client.get('http://www.sidefx.com/download/daily-builds/')

# get build
build_text = 'houdini-18.5.351-linux_x86_64_gcc6.3.tar.gz'
print('build is ', build_text)

# if your version is lower go to download
print('Start download...')
# download url
url = 'https://www.sidefx.com/download/download-houdini/69423/get/'
print('  DOWNLOAD URL:', url)

# create local file path
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)
local_filename = os.path.join(tmp_folder, build_text).replace('\\', '/')
print('  Local File:', local_filename)

# get content
resp = client.get(url, stream=True)
total_length = int(resp.headers.get('content-length'))
need_to_download = True
if os.path.exists(local_filename):
    # compare file size
    if not os.path.getsize(local_filename) == total_length:
        os.remove(local_filename)
    else:
        # skip downloading if file already exists
        print('Skip download')
        need_to_download = False

if need_to_download:
    # download file
    print('Total size %sMb' % int(total_length/1024.0/1024.0))
    block_size = 1024*4
    dl = 0
    with open(local_filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                f.flush()
                dl += len(chunk)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s] %sMb of %sMb" % ('=' * done,
                                                            ' ' * (50-done),
                                                            int(dl/1024.0/1024.0),
                                                            int(total_length/1024.0/1024.0)
                                                            )
                                 )
                sys.stdout.flush()
    print
    print('Download complete')
