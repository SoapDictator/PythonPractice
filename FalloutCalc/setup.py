from distutils.core import setup
import py2exe, sys, shutil

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 3}},
    windows = [{'script': "calc.py"}], 
    zipfile = None,
)

shutil.rmtree('build', ignore_errors=True)           #Remove the build folder  