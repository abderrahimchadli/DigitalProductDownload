#!k:\projects\digitalproductdownload\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'b2==3.4.0','console_scripts','b2'
__requires__ = 'b2==3.4.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('b2==3.4.0', 'console_scripts', 'b2')()
    )
