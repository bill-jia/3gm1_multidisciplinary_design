import serial
import argparse

parser = argparse.ArgumentParser(description ='Get serial data from Arduino')
parser.add_argument('comport', nargs=1, type=str)
parser.add_argument('--outputpath', '-o', nargs='?', default='output.txt')
parser.add_argument('--time', '-t', nargs='?', type=int, default=2)

args = parser.parse_args()
COMport = args.comport[0]
opath = args.outputpath
t_max = args.time

print(COMport)
print(opath)
print(t_max)
ser = serial.Serial(COMport, 9600, timeout=1)
f = open(opath, "w+")
for i in range(0, int(t_max/0.02)):
	l = ser.readline()
	f.write(l.decode("utf-8"))
ser.close()
f.close()