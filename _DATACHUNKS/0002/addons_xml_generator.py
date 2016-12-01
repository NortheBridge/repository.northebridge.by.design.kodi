# *
# *  Copyright (C) 2012-2013 Garrett Brown
# *  Copyright (C) 2010      j48antialias
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *  Based on code by j48antialias:
# *  https://anarchintosh-projects.googlecode.com/files/addons_xml_generator.py
# *
 
""" addons.xml generator """

import hashlib
import os
import sys
 
# Compatibility with 3.0, 3.1 and 3.2 not supporting u"" literals
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x

class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
        Also generates a md5 hash of the zip file contained in each addon folder (Krypton)
    """
    def __init__(self):
        # generate files
        self._generate_addons_file()
        self._generate_md5_file("addons.xml")
        # notify user
        print("Finished updating addons xml and md5 files")

    def _generate_addons_file(self):
        # addon list
        addons = os.listdir('.')
        # final addons text
        addons_xml = u("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n")
        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                # skip any file or .svn folder or .git folder
                if not os.path.isdir(addon) or addon == ".svn" or addon == ".git":
                    continue
                # create path
                _path = os.path.join(addon, "addon.xml")
                # split lines for stripping
                xml_lines = open(_path, "r").read().splitlines()
                # new addon
                addon_xml = ""
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if (line.find( "<?xml" ) >= 0): continue
                    # add line
                    if sys.version < '3':
                        addon_xml += unicode(line.rstrip() + "\n", "UTF-8")
                    else:
                        addon_xml += line.rstrip() + "\n"
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
                # create md5 hash for zip (Kodi Krypton)
                for addon_file in os.listdir(addon):
                    if addon_file.endswith('.zip'):
                        self._generate_md5_file(os.path.join(addon, addon_file))
            except Exception as e:
                # missing or poorly formatted addon.xml
                print("Excluding %s for %s" % (addon, e))
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u("\n</addons>\n")
        # save file
        self._save_file(addons_xml.encode("UTF-8"), file="addons.xml")

    def _generate_md5_file(self, file):
        # create a new md5 hash
        if file == "addons.xml":
            import md5
            md5_hash = md5.new(open(file, "r").read()).hexdigest()
        else: # Process any other files by binary
            BLOCKSIZE = 65536
            hasher = hashlib.md5()
            
            with open(file, 'rb') as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(BLOCKSIZE)
            md5_hash = hasher.hexdigest()
            try:
                if open(file+".md5", 'r').read() == md5_hash:
                    # Same hash, skip
                    return
            except Exception:
                pass
        # save file
        self._save_file(md5_hash, file+".md5")

    def _save_file(self, data, file):
        try:
            # write data to the file (use b for Python 3)
            open(file, "wb").write(data)
        except Exception as error:
            # oops
            print("An error occurred saving %s file!\n%s" % (file, error)) 
 
if ( __name__ == "__main__" ):
    # start
    Generator()
