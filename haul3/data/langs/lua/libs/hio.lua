-- HAUL I/O for LUA
function put(data)
	print(data)
end

function shout(data)
	print('!! '..data)
end

function fetch()
	return io.read()
end

-- function str(v)
-- 	return ''..v
-- end