#!k:\projects\digitalproductdownload\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'cloudflare==2.11.1','console_scripts','cli4'
__requires__ = 'cloudflare==2.11.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('cloudflare==2.11.1', 'console_scripts', 'cli4')()
    )
