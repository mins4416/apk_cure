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


# parse header
int_headerSize = int.from_bytes(bytes_content[0x2:0x4], 'little')
int_fileSize = int.from_bytes(bytes_content[0x4:0x8], 'little')

# parse string chunk
offset_sc = int_headerSize
int_scSize = int.from_bytes(bytes_content[offset_sc+0x4:offset_sc+0x4+0x4], 'little')

# parse resource chunk
offset_rc = int_headerSize + int_scSize
int_rcSize = int.from_bytes(bytes_content[offset_rc+0x4:offset_rc+0x4+0x4], 'little')

# parse namespace chunk
offset_nsc_start = int_headerSize + int_scSize + int_rcSize
int_nameSpaceChunk_start = int.from_bytes(bytes_content[offset_nsc_start+0x4:offset_nsc_start+0x4+0x14], 'little')

offset_nsc_end = int_fileSize - 0x18
int_nameSpaceChunk_end = int.from_bytes(bytes_content[offset_nsc_end+0x4:offset_nsc_end+0x4+0x14], 'little')


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

print("Checking... chunk")

# check namespace type
real_nameSpace_start_type = b'\x00\x01\x10\x00'
real_nameSpace_end_type   = b'\x01\x01\x10\x00'
byte_nameSpace_start_type = bytes_content[offset_nsc_start:offset_nsc_start+0x4]
byte_nameSpace_end_type = bytes_content[offset_nsc_end:offset_nsc_end+0x4]
if byte_nameSpace_start_type != real_nameSpace_start_type or byte_nameSpace_end_type != real_nameSpace_end_type:
    print("Source's nameSpaceChunk type has a problem. Fixing...")
    barray_content[offset_nsc_start:offset_nsc_start+0x2] = real_nameSpace_start_type
    barray_content[offset_nsc_end:offset_nsc_end+0x2] = real_nameSpace_end_type
    print("Source's nameSpaceChunk type has Fixed.")
else:
    print("Source's nameSpaceChunk type looks good.")

# compare start & end
if int_nameSpaceChunk_start != int_nameSpaceChunk_end:
    print("Source's nameSpaceChunk has a problem. Fixing...")
    barray_content[offset_nsc_end+0x4:offset_nsc_end+0x4+0x14] = int_nameSpaceChunk_start.to_bytes(0x14, 'little')
    print("Source's nameSpaceChunk has Fixed.")
else:
    print("Source's nameSpaceChunk looks good.")
    
bytes_content = bytes(barray_content)

# Making a new apk with fixed things.
for file in source.filelist:
    if (len(file.filename) < 100) and (file.filename != 'AndroidManifest.xml'):
        target.writestr(file.filename, source.read(file.filename))
    if file.filename == 'AndroidManifest.xml':
        target.writestr(file.filename, bytes_content)
target.close()
source.close()