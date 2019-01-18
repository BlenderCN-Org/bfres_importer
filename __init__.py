#!/usr/bin/env python3
"""BFRES importer/decoder for Blender.

This script can also run from the command line without Blender,
in which case it just prints useful information about the BFRES.
"""

bl_info = {
    "name": "Nintendo BFRES format",
    "description": "Import-Export BFRES models",
    "author": "RenaKunisaki",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "File > Import-Export",
    "warning": "This add-on is under development.",
    "wiki_url": "https://github.com/RenaKunisaki/bfres_importer/wiki",
    "tracker_url": "https://github.com/RenaKunisaki/bfres_importer/issues",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}

# Reload the package modules when reloading add-ons in Blender with F8.
print("BFRES MAIN")
if "bpy" in locals():
    import importlib
    names = ('BinaryStruct', 'FRES', 'FMDL', 'Importer', 'YAZ0')
    for name in names:
        ls = locals()
        if name in ls:
            importlib.reload(ls[name])

# fix up import path (why is this necessary?)
import sys
import os.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# import our modules
import bpy
from bfres import Importer, YAZ0, FRES, BinaryStruct
from bfres.Importer import ImportOperator
from bfres.Importer.Preferences import BfresPreferences
from bfres.BinaryFile import BinaryFile
import tempfile


# define Blender functions
def register():
    print("BFRES REGISTER")
    bpy.utils.register_module('bfres')
    bpy.types.INFO_MT_file_import.append(
        ImportOperator.menu_func_import)


def unregister():
    print("BFRES UNREGISTER")
    bpy.utils.unregister_module('bfres')
    bpy.types.INFO_MT_file_import.remove(
        ImportOperator.menu_func_import)


# define main function, for running script outside of Blender.
# this currently doesn't work.
def main():
    if len(sys.argv) < 2:
        print("Usage: %s file" % sys.argv[0])
        return

    InPath = sys.argv[1]
    InFile = None

    # try to decompress the input to a temporary file.
    file  = BinaryFile(InPath, 'rb')
    magic = file.read(4)
    file.seek(0) # rewind
    if magic in (b'Yaz0', b'Yaz1'):
        print("Decompressing YAZ0...")

        # create temp file and write it
        InFile = tempfile.TemporaryFile()
        YAZ0.decompressFile(file, InFile)
        InFile.seek(0)
        InFile = BinaryFile(InFile)
        file.close()
        file = None

    elif magic == b'FRES':
        print("Input already decompressed")
        InFile = BinaryFile(file)

    else:
        file.close()
        file = None
        raise TypeError("Unsupported file type: "+str(magic))

    # decode decompressed file
    print("Decoding FRES...")
    fres = FRES.FRES(InFile)
    fres.decode()
    print("FRES contents:\n" + fres.dump())


if __name__ == '__main__':
    main()
