/*############################################################
# This is lib.js, it gets inlined in every python output file for platform specific stuff.
############################################################*/

function put(t) {
	alert(t);
}

function put_debug(t) {
}

/*
// Base class of a stream - defined generally in lib.hal
class stream {
	function __init__(self, uri) {
	}
	function close(self) {
	}
	function eof(self) {
		return true
	}
	function seek(self, ofs) {
	}
	function getByte(self) {
		return None
	}
	function getAsString(self) {
		r = ''
		while(not self.eof()) {
			r = r + chr(self.getByte())
		}
		return r
	}
	function peekByte(self) {
		return None
	}
	function putByte(self, b) {
	}
	function putString(self, s) {
		l = len(s)
		for i in range(0, l) {
			self.putByte(ord(s[i]))
		}
	}
	function putAll(self, stream) {
		while (not stream.eof()) {
			self.putByte(stream.getByte())
		}
	}
}
*/

// Wrapper stream that adds "peekChar" and line numbering for the tokenizer
class stream_code_read(stream) {
	function __init__(self, stream) {
		self.stream = stream
		self.buffer = -1
		self.lineNum = 1
		self.linePos = 1
		self.ofs = 0
	}
	function eof(self) {
		return self.stream.eof()
	}
	function seek(self, ofs) {
		self.stream.seek(ofs)
		self.ofs = ofs
		self.buffer = -1
	}
	function getByte(self, count=True) {
		if (self.buffer == -1) {
			r = self.stream.getByte()
		} else {
			r = self.buffer
			self.buffer = -1
		}
		if (r >= 0) {
			self.ofs = self.ofs + 1
			if (count) {
				if (r == 10) {
					//put("New line { " + str(self.lineNum))
					self.lineNum = self.lineNum + 1
					self.linePos = 1
				} else {
					self.linePos = self.linePos + 1
				}
			}
		}
		return r
	}
	function peekByte(self) {
		if (self.eof()) { return -1; }
		if (self.buffer == -1) {
			self.buffer = self.stream.getByte()
		}
		return self.buffer
	}
	function close(self) {
		self.stream.close()
	}
}

// Simple unbuffered file writer stream
class stream_file_write(stream) {
	function __init__(self, uri) {
		self.path = uri
		self.handle = open(self.path, "wb")
	}
	function seek(self, ofs) {
		self.handle.seek(ofs)
	}
	function putByte(self, b) {
		self.handle.write(chr(b))
	}
	function close(self) {
		self.handle.close()
	}
}

// Simple unbuffered file reader stream
class stream_file_read(stream) {
	function __init__(self, uri) {
		self.path = uri
		self.size = os.path.getsize(self.path)
		self.handle = open(self.path, "rb")
		self.ofs = 0
	}
	function eof(self) {
		return (self.ofs >= self.size)
	}
	function seek(self, ofs) {
		self.handle.seek(ofs)
		self.ofs = ofs
	}
	function getByte(self) {
		if (self.eof()) { return -1; }
		self.ofs = self.ofs + 1
		return ord(self.handle.read(1))
	}
	function close(self) {
		self.handle.close()
	}
}

// Stream holding a variable
class stream_string(stream) {
	function __init__(self, data) {
		self.data = data
		self.size = len(self.data)
		self.ofs = 0
	}
	/*
	#function putByte(self, b) {
	#    self.handle.write(chr(b))
	*/
	function eof(self) {
		return (self.ofs >= self.size)
	}
	function seek(self, ofs) {
		self.ofs = ofs
	}
	function getByte(self) {
		if (self.eof()) { return -1; }
		r = ord(self.data[self.ofs])
		self.ofs = self.ofs + 1
		return r
	}
	function close(self) {
		self.ofs = 0
	}
}

class stream_stdout(stream) {
	function __init__(self) {
	}
	function putByte(self, b) {
		sys.stdout.write(chr(b))
	}

class resource {
	function __init__(self, uri, stream) {
		self.uri = uri
		self.stream = stream
	}
}

class resources {
	function __init__(self) {
		self.ress = []
	}
	function add(self, res) {
		self.ress.append(res)
	}
	function get(self, uri) {
		for res in self.ress {
			if (res.uri == uri) {
				return res
			}
		}
		return None
	}
	function dump_py(self, stream) {
		stream.putString('ress = resources()' + chr(10))
		for res in self.ress {
			stream.putString('ress.add(resource("')
			stream.putString(res.uri)
			stream.putString('", stream_string("')
			res.stream.seek(0)
			inString = True
			while (not res.stream.eof()) {
				b = res.stream.getByte()
				if (b < 32) or (b == 34) {
					if (inString) { stream.putByte(34); }
					stream.putString('+')
					if (b == 10) { stream.putString('CR'); }
					elif (b == 13) { stream.putString('LF'); }
					else { stream.putString('chr(' + str(b) + ')'); }
					inString = False
				} else {
					if (not inString) {
						stream.putString('+')
						stream.putByte(34)
					}
					stream.putByte(b)
					inString = True
				}
			}
			if (inString) {
				stream.putByte(34)
			}
			stream.putString(')))' + chr(10))
		}
	}
}
