#!/usr/bin/python

import sys
import fnmatch
import os
from clean_file import *


if not '.mb' in sys.argv[1]:
    print "Scanning for matching files:"
    matches = []
    for root, dirnames, filenames in os.walk(sys.argv[1]):
        for filename in fnmatch.filter(filenames, '*.mb'):
            matches.append(os.path.join(root, filename))

    total_warnings = 0
    for mb_file in matches:
        print "Parsing file " + mb_file

        try:
            os.remove(mb_file + '.cleaned')
        except:
            pass

        warnings, changed_lines = cleanFile(mb_file, mb_file + '.cleaned')
        if changed_lines > 0:
            os.remove(mb_file)
            os.rename(mb_file + '.cleaned', mb_file)
        else:
            os.remove(mb_file + '.cleaned')

        total_warnings += warnings

    print "\n\n----------------------\nTotal warnings: " + str(total_warnings)

else:
    mb_file = sys.argv[1]
    print "Parsing file " + mb_file

    try:
        os.remove(mb_file + '.cleaned')
    except:
        pass

    warnings, changed_lines = cleanFile(mb_file, mb_file + '.cleaned')
    if changed_lines > 0:
        os.remove(mb_file)
        os.rename(mb_file + '.cleaned', mb_file)
    else:
        os.remove(mb_file + '.cleaned')
