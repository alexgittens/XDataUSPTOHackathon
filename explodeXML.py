import re

def explodeXML(origfname):
  """ Split an original file made of concatenated xml files into its constituent files:
  fname.xml becomes fname-1.xml ... fname-n.xml"""  

basefname = origfname[:-4]
cursubfileidx = 1
fout = None

with open(origfname, "r") as fin:
    for line in fin:
        if re.match('^<\?xml', line):
            cursubfileidx = cursubfileidx + 1
            if fout is not None:
                fout.close()
            cursubfileidx = cursubfileidx + 1
            curoutfname = basefname + '-' + str(cursubfileidx) + '.xml'
            fout = open(curoutfname, "w")
            fout.write(line)
        else:
            fout.write(line)    
            
explodeXML("ipgb20051227.xml")
