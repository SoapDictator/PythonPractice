import re

class Main(object):
	def __init__(self):
		self.process("2 * 2")
		
	def process(self, expression):
		#pattern = re.compile(r'(\?+)/\d+ + (\?+)/\d+')
		pattern = re.compile(r'(\d+)\s+([*/\//+/-])\s+(\d+)')
		
		match = pattern.search(expression)
		if match != None:
			number1 = OperandNumeric(match.group(1))
			number2 = OperandNumeric(match.group(3))
			operator = OperandArifmetic(match.group(2))
			
			operator.linkFirst = number1
			operator.linkSecond = number2
			
			result = None
			if operator.value == "*":
				result = int(operator.linkFirst.value)*int(operator.linkSecond.value)
			elif operator.value == "/":
				result = int(operator.linkFirst.value)/int(operator.linkSecond.value)
			elif operator.value == "+":
				result = int(operator.linkFirst.value)+int(operator.linkSecond.value)
			elif operator.value == "-":
				result = int(operator.linkFirst.value)-int(operator.linkSecond.value)
			
			print(result)
									
	
class Composite(object):
	linkFirst = None
	linkSecond = None
		
class OperandArifmetic(Composite):
	value = None
	
	def __init__(self, value):
		self.value = value

class OperandNumeric(Composite):
	value = None
	
	def __init__(self, value):
		self.value = value
	
Start = Main()