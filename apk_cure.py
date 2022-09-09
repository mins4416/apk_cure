import zipfile
import argparse

# argparse init
parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, help="Source apk file name.", required=True)
parser.add_argument('-o', type=str, help="Destination apk file name.", required=True)
args = parser.parse_args()
source_apk = args.i
target_apk = args.o

source = zipfile.ZipFile(source_apk, 'r')
target = zipfile.ZipFile(target_apk, 'w', zipfile.ZIP_DEFLATED)
bytes_content = ''
barray_content = ''

# android manifest.xml init
for inzipinfo in source.infolist():
    with source.open(inzipinfo) as infile:
        if inzipinfo.filename == 'AndroidManifest.xml':
            bytes_content = infile.read()

int_magicnumber = int.from_bytes(bytes_content[0:4], 'little')
int_scStringCount = int.from_bytes(bytes_content[0x10:0x10+0x4], 'little')
int_scStringPoolOffset = int.from_bytes(bytes_content[0x1c:0x1c+4], 'little')
real_scStringCount = int((int_scStringPoolOffset+0x8-0x24)/4)

# You can modify data now.
barray_content = bytearray(bytes_content)

print("Checking... magicnumber")
real_magicnumber = b'\x03\x00\x08\x00'
if barray_content[0:4] is not real_magicnumber:
    print("Source's magicnumber has a problem. Fixing...")
    barray_content[0:4] = real_magicnumber
    print("Source's magicnumber has Fixed.")
else:
    print("Source's magicnumber looks good.")

print("Checking... scStringCount")
if int_scStringCount is not real_scStringCount:
    print("Source's scStringCount was modified. Fixing...")
    barray_content[0x10:0x10+0x4] = real_scStringCount.to_bytes(4, 'little')
    print("Source's scStringCount value has Fixed.")
else:
    print("Source's scSringCount looks good.")

bytes_content = bytes(barray_content)

# Making a new apk with fixed things.
for file in source.filelist:
    if (len(file.filename) < 100) and (file.filename != 'AndroidManifest.xml'):
        target.writestr(file.filename, source.read(file.filename))
    if file.filename == 'AndroidManifest.xml':
        target.writestr(file.filename, bytes_content)
target.close()
source.close()