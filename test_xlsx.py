from xlsx import workbook

Workbook = workbook("C:\\Users\\Arif\\workspace\\PyWRFChemEmiss\\src\\res\\Data_Argis.xlsx")

s = Workbook.Sheets.Sheet1
#print "Total Formulas Tested: %s"%len(s.keys())
#print "CELL:\tFunction,\t\tEval,\t\tOrig"
print 'OK'
for i in xrange(1,9):
    cell = "A{0}".format(i)
    print cell, ": ", s[cell]

print s.interpolate("A1:A9")

#for c in s:
#    cell = s[c]
#    orig = cell.val
#    cell.evaluate()
#    if cell.fn:
#        print "%s:\t%s,\t\t%s,\t\t%s"%(c,cell.fn if hasattr(cell, "fn") else "", cell.val, orig)
        