import re

if __name__ == "__main__":
    linenum = 0
    with open('mainstream.srt', 'r') as fr:
        with open('mainstream-edt.srt', 'w') as fw:
            r_all = fr.readlines()
            for i in r_all:
#00 : 00 : 15,082-> 00 : 00 : 19,621
                m = re.search('\d->\s', i) 
                if(m is not None):
                    t = re.sub(' ', '', i)
                    t = re.sub('->', ' --> ', t)
                    fw.write(t)
                    #print(t)
                else:
                    fw.write(i)
                linenum += 1
