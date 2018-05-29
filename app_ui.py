import cytosponge

testCase = 1
oesophagusLength = 30

comfile = open("com.txt")
COMport = comfile.readline().rstrip()
comfile.close()
if __name__ == '__main__':
	app = cytosponge.CytospongeApp(COMport, None, title="Cytosponge Training")
	
	
