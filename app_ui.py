import cytosponge

testCase = 1
oesophagusLength = 30

COMport = 'COM3'

if __name__ == '__main__':
	app = cytosponge.CytospongeApp(COMport, None, title="Cytosponge Training", size=(1000,600))
	
	