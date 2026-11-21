"""Build this battle's page (index.html). The work is done by tools/build.py, which builds all the playbacks the same way."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tools'))
import build
build.main(['luzon1899'])
