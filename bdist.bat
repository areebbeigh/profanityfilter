@echo off
REM Probably specific to only my system py - python2 ; python - python3
py setup.py bdist --formats=msi,wininst,zip
python setup.py bdist --formats=msi,wininst,zip
python setup.py sdist bdist_wheel
