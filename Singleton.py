class OnlyOne:
	class __OnlyOne:
		def __init__(self, arg):
			self.val = arg
            
		def info(self):
			print(self, self.val)
            
	instance = None
	def __init__(self, arg):
		if not OnlyOne.instance:
			OnlyOne.instance = OnlyOne.__OnlyOne(arg)
		else:
			OnlyOne.instance.val = arg
	def __getattr__(self, name):
		return getattr(self.instance, name)

x = OnlyOne('sausage')
x.info()
y = OnlyOne('eggs')
y.info()
z = OnlyOne('spam')
z.info()
y.info()
x.info()