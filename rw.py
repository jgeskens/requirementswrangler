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
        found = [l for l in frozen.splitlines() if ('#egg=%s' % package) in l or ('/%s.git@' % package) in l or ('/%s@' % package) in l]
        if found:
            version_match = re.findall(r'.*@(\S+)#egg=.*', found[0])
            if version_match:
                return version_match[0][:7]
        return None


def update_requirements():
    req_filename = sys.argv[1]
    req_file = codecs.open(req_filename, 'rt', encoding='utf-8')
    packages = sys.argv[2:]
    new_lines = []
    changed = False
    freezer = Freezer()
    for line in req_file.readlines():
        new_line = line
        for package in packages:
            if '#egg=%s' % package in line or ('/%s.git@' % package) in line or ('/%s@' % package) in line:
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


def parse_github_line(line):
    if not '.git@' in line:
        # no version specified
        line = line.replace('.git', '.git@')
    before_at, after_at = line.rsplit('@', 1)
    before_slash, package_name = before_at.rsplit('/', 1)
    if package_name[-4:] == '.git': package_name = package_name[:-4]
    version, egg_name = after_at.split('#egg=')

    return {
        'package_name': package_name,
        'version': version,
        'egg_name': egg_name
    }


def sync_requirements(req_filename, interactive):
    req_file = codecs.open(req_filename, 'rt', encoding='utf-8')
    freezer = Freezer()
    frozen_directory = {}
    req_directory = {}
    for frozen_line in freezer.get_frozen_packages().splitlines():
        if frozen_line[:1] == '#':
            # skip this line, it is a comment
            pass
        elif frozen_line[:2] == '-e':
            if 'github.com' in frozen_line:
                # editable package, get the commit as version
                parsed_line = parse_github_line(frozen_line)
                frozen_directory[parsed_line['package_name'].lower()] = parsed_line
        elif '==' in frozen_line:
            package_name, version = frozen_line.split('==', 1)
            frozen_directory[package_name.lower()] = {
                'package_name': package_name,
                'version': version.strip('\n'),
                'egg_name': package_name
            }

    for req_line in req_file.readlines():
        if req_line[:1] == '#':
            # skip this line, it is a comment
            pass
        elif req_line[:2] == '-e':
            if '@' in req_line and 'github.com' in req_line:
                # editable package, get the commit as version
                parsed_line = parse_github_line(req_line)
                parsed_line['line'] = req_line.strip()
                req_directory[parsed_line['package_name'].lower()] = parsed_line
        elif '==' in req_line:
            package_name, version = req_line.split('==', 1)
            req_directory[package_name.lower()] = {
                'package_name': package_name,
                'version': version.strip('\n'),
                'egg_name': package_name,
                'line': req_line.strip()
            }
        elif '>=' in req_line:
            package_name, version = req_line.split('>=', 1)
            req_directory[package_name.lower()] = {
                'package_name': package_name,
                'version': '>=' + version.strip('\n'),
                'egg_name': package_name,
                'line': req_line.strip()
            }

    up_to_date = []
    needs_update = []
    needs_install = []

    for package_name, package_info in req_directory.iteritems():
        if package_name in frozen_directory:
            # Already installed
            current_package = frozen_directory[package_name.lower()]
            current_version = current_package['version']
            new_version = package_info['version']

            if new_version != current_version[:len(new_version)] and new_version != current_package['egg_name'][-len(new_version):]:
                print current_package['egg_name']
                needs_update.append(package_name)
                print package_name, current_version, '->', new_version, '[needs update]'
                if interactive:
                    print package_info['line']
                    print 'Update? [y/n/q]',
                    cmd = raw_input().strip()
                    if cmd == 'q':
                        sys.exit(0)
                    elif cmd == 'y':
                        subprocess.call(['pip', 'install'] + package_info['line'].split(' '))
            else:
                up_to_date.append(package_name)
        else:
            needs_install.append(package_name)
            print package_name, package_info['version'], '[new]'
            if interactive:
                print package_info['line']
                print 'Update? [y/n/q]',
                cmd = raw_input().strip()
                if cmd == 'q':
                    sys.exit(0)
                elif cmd == 'y':
                    subprocess.call(['pip', 'install'] + package_info['line'].split(' '))

    



if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python rw.py [sync [-i]] path/to/requirements.txt [app1 [app2 ...]]')
        exit(0)
    if sys.argv[1] == 'sync':
        sync_requirements(sys.argv[2] if sys.argv[2] != '-i' else sys.argv[3], sys.argv[2] == '-i')
    else:
        update_requirements()

