import sys
import os
import re
import struct

fec_dict = {
0x000300:	{ 0x00: 'AMI Enable / USB', 0x01: 'Gracenote DB EU'},
0x000401:	{ 0x00: 'Navigation enable'},
0x000500:	{ 0x00: 'Bluetooth enable'},
0x000601:	{ 0x00: 'Vehicle Data Interface'},
0x000602:	{ 0x00: 'Infotainment control (SAI_RSE)'},
0x000603:	{ 0x00: 'Mirror Link'},
0x000604:	{ 0x00: 'Performance monitor (Sport-HMI)'},

0x000606:	{ 0x00: 'Baidu CarLife?'},

0x000608:	{ 0x00: 'Apple Carplay'},
0x000609:	{ 0x00: 'Google Automotive Link'},
0x000701:	{ 0x00: 'SDS Speech Dialog System'},
0x000702:	{ 0x00: 'SDS Speech Dialog System with navigation'},
0x021000:   'Nav Maps EU',
0x021100:   'Nav Maps NAR',
0x023000:   'Nav Maps EU',
0x023100:   'Nav Maps NAR',
0x023D00:   'Nav Maps ROW',
0x033000:   'Nav Maps EU',
0x033100:   'Nav Maps NAR',
0x033D00:   'Nav Maps ROW',
0x061000:   'Nav Maps EU',
0x061100:   'Nav Maps NAR',
0x061D00:   'Nav Maps ROW',

}
# Do anyone know algo for Map Care FEC? 0230001E -> how long this FEC is valid for map update?
# 1E already old, for latest maps need 22 or higher
# Ok, but how to make FEC valid for example for 3 years? Lifetime will be like in BMW "FF"...
# 2F for unlimited

# 021000xx Nav Maps EU
# 021100xx Nav Maps NAR
# 021200xx ?
# 021300xx ?
# 021A00xx ?
# 021B00xx ?
# 021D00xx Nav Maps ROW
# 023000xx Nav Maps EU
# 023100xx Nav Maps NAR
# 023D00xx Nav Maps ROW
# 033000xx Nav Maps EU
# 033100xx Nav Maps NAR
# 033D00xx Nav Maps ROW
# 061000xx Nav Maps EU
# 061100xx Nav Maps NAR
# 061D00xx Nav Maps ROW
# 063000xx Nav Maps EU
# 063100xx Nav Maps NAR
# 063D00xx Nav Maps ROW
# 071000xx Nav Maps
# 073000xx Nav Maps EU
# 073D00xx Nav Maps ROW
# 081000xx Nav Maps EU
# 081100xx Nav Maps NAR
# 081400xx Nav Maps AGCC
# 081401xx Nav Maps AGCC, Turkey
# 081402xx Nav Maps AGCC, Israel
# 081403xx ?
# 081500xx Nav Maps South Africa
# 081600xx Nav Maps Australia, New Zealand
# 081700xx Nav Maps India
# 081800xx Nav Maps Mexico
# 081801xx Nav Maps Chile
# 081900xx Nav Maps Asia/Pacific
# 081D00xx Nav Maps ROW
# 081D01xx ?
# 083000xx Nav Maps EU
# 083D00xx Nav Maps ROW
# 091000xx Nav Maps EU
# 091100xx Nav Maps NAR
# 091300xx ?
# 091400xx Nav Maps Turkey
# 091401xx Nav Maps AGCC, Turkey
# 091402xx Nav Maps AGCC, Israel
# 091403xx Nav Maps AGCC
# 091500xx Nav Maps South Africa
# 091600xx Nav Maps Australia, New Zealand
# 091700xx Nav Maps India
# 091800xx Nav Maps Argentina, Brazil, Mexico
# 091801xx Nav Maps Chile
# 091900xx Nav Maps Asia/Pacific
# 091A00xx ?
# 091D00xx Nav Maps ROW
# 093000xx Nav Maps EU
# 093100xx Nav Maps NAR
# 093D00xx Nav Maps ROW
#
# Read more: http://forum.obdeleven.com/thread/6082/fec-swap-codes-list-mib#ixzz5tM682Ksd

def fec_to_string(fec):
    prim_fec = fec >> 8
    sub_fec = fec & 0xFF
    if prim_fec in fec_dict:
        fec_entry = fec_dict[prim_fec]
        if isinstance(fec_entry, dict):
            if sub_fec in fec_entry:
                return fec_entry[sub_fec]
            else:
                return fec_dict[prim_fec] + " (" + str(sub_fec) + ")"
        else:
            return fec_dict[prim_fec] + " (0x%02X)" % sub_fec
    return ""

def unpack_fec(fec_data, offset=0):
    (fsize) = struct.unpack_from("<I", fec_data, offset)
    offset += 4
    print("Size   : %d" % fsize)
    (magicHigh, magicLow) = struct.unpack_from(">HI", fec_data, offset)
    print("Magic  : %X" % ((magicHigh << 32) + magicLow))
    offset += 6
    (ver, vcrnHigh, vcrnLow) = struct.unpack_from(">BBI", fec_data, offset)
    offset += 6
    print("Version: %d" % ver)
    print("VCRN   : %X" % ((vcrnHigh << 32) + vcrnLow))
    (vin) = struct.unpack_from("18s", fec_data, offset)
    offset += 18
    print("VIN    : %s" % vin)
    # 37 - padding
    (timestamp) = struct.unpack_from("<I", fec_data, offset)
    offset += 4
    (fecCount,) = struct.unpack_from("<B", fec_data, offset)
    offset += 1
    print("FEC cnt: %d" % fecCount)
    for i in range(fecCount):
        (fec,) = struct.unpack_from(">I", fec_data, offset)
        offset += 4
        print("FEC %d  : %08X - %s" % (i, fec, fec_to_string(fec)))
    signature = struct.unpack_from("128B", fec_data, offset)
    print('Sig    :'),
    i = 0
    for sig in signature:
        print('%02X' % sig),
        i += 1
        if not (i % 16):
            print('\n        '),
    print('\r'),
    offset += 128
    (fecCount1,) = struct.unpack_from("<B", fec_data, offset)
    offset += 1
    print("FECs as little endian:")
    # skip 3 padding bytes
    offset += 3
    for i in range(fecCount1):
        (fec,) = struct.unpack_from("<I", fec_data, offset)
        offset += 4
        print("FEC %d  : %08X - %s" % (i, fec, fec_to_string(fec)))
    return offset
    
if len(sys.argv)!=2:
	print("Usage: "+sys.argv[0]+" <fec_file>")
	sys.exit()
f=open(sys.argv[1],"rb")
fec_data=f.read()
f.close()
print("File size: %d" % len(fec_data))
(fecCollectionCount,) = struct.unpack_from("<I", fec_data, 0)
print("FEC collections: %d" % fecCollectionCount)
offset = 4
for i in range(fecCollectionCount):
    offset = unpack_fec(fec_data, offset)
print('Final offset: %d' % offset)

# Bytes 00-03 01 00 00 00 # 1 FeC collections
# Bytes 04-07 B7 00 00 00 # Size of following contents (i.e. B7 = 183, 183 + 8 = 191)
# Bytes 08-13 11 07 FF FF FF FF 
# Bytes 14-19 03 61 69 DE D4 A7 # 03 + VCRN (I have no idea what 03 means)
# Bytes 20-37 VIN + 00 (18 bytes) 
# Bytes 38-42 56 4F 19 4F Epoch time 
# Byte 42: 05 #Number of FeCs
# Bytes 43-46 FeC #1 Big Endian
# Bytes 47-50 FeC #2 Big Endian
# Bytes 51-54 Fec #3 Big Endian
# Bytes 55-58 Fec #4 Big Endian
# Bytes 59-62 FeC #5 Big Endian
# # Bytes 63 ~ 190 were signature for identification. 128 bytes
# Bytes 63-79 85 18 6F 42 EA D4 9B CD B1 D8 4F E3 F0 64 7E 13 
# Bytes 80 - 95 A3 84 37 24 B3 05 34 67 DD 05 DB A5 DC 18 97 5B 
# Bytes 96 - 111 A3 F5 C9 74 29 4D 55 23 E4 85 8D B0 81 AB CB 9D 
# Bytes 112 -127 AC 95 39 6F 46 39 7A E5 00 88 E3 7B 24 C9 69 D5 
# Bytes 128 - 143 30 8B BD D2 9A A8 05 A4 01 A2 09 6F 92 30 87 69 
# Bytes 144- 159 0B 59 F0 44 33 6C B2 8E 99 20 3B 8E 4B FE F7 EC 
# Bytes 160 - 175 B3 6C 7B 3D 79 DA B7 FE 9A ED 97 B0 D0 DD 60 25 
# Bytes 176 - 190 73 16 BB 40 3F A4 5C 4F E2 75 B1 6E 39 F8 6E 
# Bytes 191 - 194 05 00 00 00 # Counts of FeC
# Bytes 195-198 FeC #1 Little Endian
# Bytes 199-202 FeC #2 Little Endian
# Bytes 203-206 Fec #3 Little Endian
# Bytes 207-210 Fec #4 Little Endian
# Bytes 211-214 FeC #5 Little Endian
# Bytes 215 -226 01 00 00 00 03 00 00 00 FF 00 00 00 # These are identify flags