@mkdir imageformats
@copy C:\Python26\lib\site-packages\PyQt4\plugins\imageformats\* imageformats

# bdist_wininst requires Python?
# c:\Python26\python setup.py bdist_wininst

# bdist_msi implemented by cx_Freeze
c:\Python26\python setup.py bdist_msi
