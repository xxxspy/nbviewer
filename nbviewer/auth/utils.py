def json_bytes_serializer(way):

	def to_json(pyobj):
		if isinstance(pyobj,bytes):
			return {'__class__':'bytes',
					'__value__':list(pyobj)}
		raise TypeError(repr(pyobj) + ' is not Json serializable')
	def from_json(jsobj):
		if '__class__' in jsobj:
			if jsobj['__class__']=='bytes':
				return bytes(jsobj['__value__'])
		return jsobj
	return locals()[way]
