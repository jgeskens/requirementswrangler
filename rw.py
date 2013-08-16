#!/usr/bin/env python

import sys
import codecs
import re
import subprocess


__author__ = 'Jef Geskens'


class Freezer:
    frozen = None

    def get_frozen_packages(self):
        if not self.frozen:
            self.frozen = subprocess.check_output(('pip', 'freeze'))
        return self.frozen

    def find_frozen_package_version(self, package):
        frozen = self.get_frozen_packages()
        found = [l for l in frozen.splitlines() if ('#egg=%s' % package) in l]
        if found:
            version_match = re.findall(r'.*@(\S+)#egg=.*', found[0])
            if version_match:
                return version_match[0][:7]
        return None


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python rw.py path/to/requirements.txt [app1 [app2 ...]]')
        exit(0)

    req_filename = sys.argv[1]

    req_file = codecs.open(req_filename, 'rt', encoding='utf-8')
    packages = sys.argv[2:]
    new_lines = []
    changed = False
    freezer = Freezer()
    for line in req_file.readlines():
        new_line = line
        for package in packages:
            if '#egg=%s' % package in line:
                match = re.findall(r'.*@(\S+)#egg=.*', line)
                if match:
                    current_version = match[0]
                    print package, current_version,

                    new_version = freezer.find_frozen_package_version(package)
                    if new_version:
                        if new_version != current_version:
                            print '->', new_version
                            new_line = new_line.replace('@%s#egg=' % current_version,
                                                        '@%s#egg=' % new_version)
                            changed = True
                        else:
                            print '[up to date]'
                    else:
                        print '[not found in pip freeze]'
        new_lines.append(new_line)
    req_file.close()

    if changed:
        req_file = codecs.open(req_filename, 'wt', encoding='utf-8')
        req_file.writelines(new_lines)
        req_file.close()
        print u'Wrote changes to %s.' % req_filename
    else:
        print u'Left %s untouched.' % req_filename
