#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
PDB handling
2017-04-11 by Bernhard "HotKey" Slawik
"""

import struct
import time, datetime	# for strftime

def put(txt):
	print(str(txt))

def byte_append(ba, data):
	for d in data:
		ba.append(d)

PDB_MAX_NAME_SIZE = 32
PDB_TIME_OFFSET = 2082844886	#Time offset from Unix time() values ("0" = 1900 (PalmOS) VS 1970 (Unix))

PDB_HEADER_SIZE = 78
PDB_RESOURCE_ENTRY_SIZE = 10
PDB_RECORD_ENTRY_SIZE = 8

dmRecAttrDelete	= 0x80	#Delete this record on next sync
dmRecAttrDirty	= 0x40	#Archive this record on next sync
dmRecAttrBusy	= 0x20	#Record is in use
dmRecAttrSecret	= 0x10	#Secret record, protected by password

dmRecAttrCategoryMask = 0x0F	#Mask to extract category from attribute


NUL = chr(0)
def long_to_str(v):
	r = ''
	for i in xrange(4):
		r = chr(v & 0xff) + r
		v = v >> 8
	return r

def long_to_time(v):
	if v == 0: return None
	unix_timestamp = v - PDB_TIME_OFFSET
	t = datetime.datetime.fromtimestamp(unix_timestamp)
	return t
	

def time_to_str(t):
	if t == None: return 'N/A'
	return t.strftime('%Y-%m-%d %H:%M:%S')

"""
	char            name[kMaxPDBNameSize];
	unsigned short  flags;
	unsigned short  version;
	unsigned long   creationTime;
	unsigned long   modificationTime;
	unsigned long   backupTime;
	unsigned long   modificationNumber;
	unsigned long   appInfoOffset;
	unsigned long   sortInfoOffset;
	unsigned long   type;
	unsigned long   creator;
	unsigned long   uniqueID;
	unsigned long   nextRecordID;
	unsigned short  numRecords;
"""
class PDBFile:
	def __init__(self):
		self.name = ''
		self.flags = 0
		self.version = 0
		self.creationTime = 0
		self.modificationTime = 0
		self.backupTime = 0
		self.modificationNumber = 0
		self.appInfoOffset = 0
		self.sortInfoOffset = 0
		self.type = 0
		self.creator = 0
		self.uniqueID = 0
		self.nextRecordID = 0
		self.numRecords = 0
		
		self.records = []
	
	def from_file(self, data, o=0, l=-1):
		p = self
		
		# PDB files require the file size to be exact
		if l < 0: l = len(data)
		
		#o = 0
		p.name, = struct.unpack_from('%ds' % PDB_MAX_NAME_SIZE, data, o); o += PDB_MAX_NAME_SIZE
		# Truncate string at first ZERO char. Will crash if none found
		if NUL in p.name:
			p.name = p.name[:p.name.index(NUL)]
		
		p.flags, p.version = struct.unpack_from('>HH', data, o); o += 2 + 2
		
		p.creationTime, p.modificationTime, p.backupTime = struct.unpack_from('>LLL', data, o); o += 4 + 4 + 4
		p.modificationNumber, = struct.unpack_from('>L', data, o); o += 4
		p.appInfoOffset, = struct.unpack_from('>L', data, o); o += 4
		p.sortInfoOffset, = struct.unpack_from('>L', data, o); o += 4
		p.type, = struct.unpack_from('>L', data, o); o += 4
		p.creator, = struct.unpack_from('>L', data, o); o += 4
		p.uniqueID, = struct.unpack_from('>L', data, o); o += 4
		p.nextRecordID, = struct.unpack_from('>L', data, o); o += 4
		p.numRecords, = struct.unpack_from('>H', data, o); o += 2
		
		for i in xrange(p.numRecords):
			rec = PDBRecordEntry()
			rec.from_file(data, o=o)
			p.records.append(rec)
			o += PDB_RECORD_ENTRY_SIZE
		
		# first record may contain size of data in record[1]
		# I guess:
		#	unsigned short index
		#	
		
		# Load data once we know the boundaries
		data_size = l
		for i in xrange(p.numRecords):
			rec = p.records[i]
			if (i+1 < p.numRecords):
				s = p.records[i+1].offset - rec.offset
			else:
				s = data_size - rec.offset
			rec.load_data(data=data, o=0, size=s)
			
		
		return p
	
	def to_file(self):
		data = bytearray()
		
		byte_append(data, self.name)
		data.append(0)
		while (len(data) < PDB_MAX_NAME_SIZE):
			data.append(0)
		
		byte_append(data, struct.pack('>HH', self.flags, self.version))
		byte_append(data, struct.pack('>LLL', self.creationTime, self.modificationTime, self.backupTime))
		
		
		byte_append(data, struct.pack('>L', self.modificationNumber))
		byte_append(data, struct.pack('>L', self.appInfoOffset))
		byte_append(data, struct.pack('>L', self.sortInfoOffset))
		byte_append(data, struct.pack('>L', self.type))
		byte_append(data, struct.pack('>L', self.creator))
		byte_append(data, struct.pack('>L', self.uniqueID))
		byte_append(data, struct.pack('>L', self.nextRecordID))
		byte_append(data, struct.pack('>H', self.numRecords))
		
		o = len(data)
		rec_data_ofs = o + self.numRecords * 8
		for i in xrange(self.numRecords):
			rec = self.records[i]
			put('Writing record #%d header...' % (i))
			rec_data = rec.to_file(ofs=rec_data_ofs)
			byte_append(data, rec_data)
			rec_data_ofs += len(rec.data)
		
		for i in xrange(self.numRecords):
			rec = self.records[i]
			put('Writing record #%d data...' % (i))
			byte_append(data, rec.data)
		return data
	
	def set_vfs(self, name, data):
		"Updates all records for new VFS file data"
		self.name = name
		self.flags = 8
		self.version = 0
		
		t = int(time.time()) + PDB_TIME_OFFSET
		self.creationTime = t
		self.modificationTime = t
		self.backupTime = 0
		
		self.modificationNumber = t
		self.appInfoOffset = 0
		self.sortInfoOffset = 0
		self.type = 0x54455874	#'TEXt'
		self.creator = 0x52454164	#'REAd'
		self.uniqueID = 0x5F4D5255	#'_MRU'
		self.nextRecordID = 0
		self.numRecords = 2
		
		l = len(data)
		while len(self.records) < self.numRecords:
			self.records.append(PDBRecordEntry())
			
		rec = self.records[0]
		rec.attr = 0x40
		rec.uniqueID = 0x764001
		rec.offset = 0x5e
		rec.data = bytearray()
		rec.data[:16] = 0,1, 0,0,	0,0, l >> 8, l % 0x100,	0, 1, 0x10, 0,0,0,0,0
		
		rec = self.records[1]
		rec.attr = 0x40
		rec.uniqueID = 0x764001
		rec.offset = 0x5e + 16
		rec.data = data
	
	def __repr__(self):
		r = ''
		r += 'name="%s"' % (self.name)
		r += ', flags=%04X' % (self.flags)
		r += ', version=%04X' % (self.version)
		
		#r += ', creationTime=%08X' % (self.creationTime)
		r += ', creationTime=%s' % (time_to_str(long_to_time(self.creationTime)))
		#r += ', modificationTime=%08X' % (self.modificationTime)
		r += ', modificationTime=%s' % (time_to_str(long_to_time(self.modificationTime)))
		#r += ', backupTime=%08X' % (self.backupTime)
		r += ', backupTime=%s' % (time_to_str(long_to_time(self.backupTime)))
		
		r += ', modificationNumber=%08X' % (self.modificationNumber)
		
		r += ', appInfoOffset=%08X' % (self.appInfoOffset)
		r += ', sortInfoOffset=%08X' % (self.sortInfoOffset)
		r += ', type="%s" (%08X)' % (long_to_str(self.type), self.type)
		r += ', creator="%s" (%08X)' % (long_to_str(self.creator), self.creator)
		#r += ', uniqueID=%08X' % (self.uniqueID)	#r += ', uniqueID=%s' % (long_to_str(self.uniqueID))
		r += ', uniqueID="%s" (%08X)' % (long_to_str(self.uniqueID), self.uniqueID)
		r += ', nextRecordID=%08X' % (self.nextRecordID)
		r += ', numRecords=%04X' % (self.numRecords)
		
		for i in xrange(self.numRecords):
			r += '\n* #%d: ' % (i)
			rec = self.records[i]
			r += rec.__repr__()
		
		return r

"""
	unsigned long   type;
	unsigned short  id;
	unsigned long   offset;
"""
class PDBResourceEntry:
	def __init__(self):
		self.type = 0
		self.id = 0
		self.offset = 0

"""
	unsigned long   offset;
	unsigned char   attr;
	unsigned long   uniqueID:24;
"""
class PDBRecordEntry:
	def __init__(self):
		self.offset = 0
		self.attr = ''
		self.uniqueID = 0	# 24 bits
		self.data = None
	
	def from_file(self, data, o=0):
		rec = self
		#o = 0
		rec.offset, = struct.unpack_from('>L', data, o); o += 4
		rec.attr, = struct.unpack_from('>B', data, o); o += 1
		u1,u2,u3 = struct.unpack_from('>BBB', data, o); o += 3
		rec.uniqueID = (u1 << 16) + (u2 << 8) + u3
		
		#self.data = 
		self.size = -1
		
		return rec
	
	def to_file(self, ofs=None, data=None):
		if (ofs == None): ofs = self.offset
		if data == None: data = bytearray()
		
		byte_append(data, struct.pack('>L', ofs))
		byte_append(data, struct.pack('>B', self.attr))
		byte_append(data, struct.pack('>BBB', (self.uniqueID >> 16) % 0x100, (self.uniqueID >> 8) % 0x100, self.uniqueID % 0x100))
		
		return data
		
	
	def load_data(self, data, o, size=0):
		self.size = size
		self.data = data[o+self.offset:o+self.offset+size]
	
	def __repr__(self):
		r = ''
		r += 'offset=%08X' % (self.offset)
		r += ', attr=%02X "%s"' % (self.attr, chr(self.attr))
		r += ', uniqueID=%06X' % (self.uniqueID)
		r += ', size=%d bytes' % (self.size)
		#r += ', size=%04X' % (self.size)
		return r

if __name__ == '__main__':
	#file_name = 'test/t2.pas.pdb'
	filename = 'test/t300.pas.pdb'
	
	pdb = PDBFile()
	"""
	### Read a PDB file
	with open(filename, 'rb') as h:
		data = h.read()
		pdb.from_file(data)
		put(pdb)
	put(pdb.records[1].data)
	
	outfile = filename + '.pdb'
	with open(outfile, 'wb+') as h:
		h.write(pdb.to_file())
	"""
	
	### Write a PDB file (VFS format)
	name = 'hello2'
	pdb.set_vfs(name='%s.txt' % name, data='Hello!')
	outfile = 'test/%s.pdb' % name
	with open(outfile, 'wb+') as h:
		h.write(pdb.to_file())
	
