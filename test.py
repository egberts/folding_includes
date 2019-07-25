#!/usr/bin/env python3


import folding_includes

test = folding_includes.de_quote("   'filespec';")
print("de_quote filespec: %s" % test)
test = folding_includes.de_quote('   "filespec"  ;   ')
print("de_quote filespec: %s" % test)
test = folding_includes.de_quote("   'filespec\".txt'  ;")
print("de_quote filespec: %s" % test)
test = folding_includes.de_quote("   filespec;")
print("de_quote filespec: %s" % test)
exit(0)