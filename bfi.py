#!/usr/bin/env python
# coding: utf-8
# vim: set noet:

import sys
import os





# Helper functions
def empty(list): return len(list) == 0

def dump(*args):
	print repr(args)

def reversed_dict(d):
	return dict([[d[key], key] for key in d])

def getchar():
	return ord(sys.stdin.read(1))

def putchar(c):
	return sys.stdout.write(chr(c))


class BFOpTable(object):
	__slots__ = ['optable', '__heap', '__index']
	
	def __init__(self, heaplen=30):
		self.optable = self.getdefaultops()
		# TODO: Use str not list
		self.__heap = [0 for times in range(heaplen)]
		self.__index = 0
	
	def getdefaultops(self):
		return {
			'>': self.op_incptr,
			'<': self.op_decptr,
			'+': self.op_incvalue,
			'-': self.op_decvalue,
			'.': self.op_output,
			',': self.op_input,
			'[': self.op_loopbegin,
			']': self.op_loopend,
		}
	
	def op_incptr(self):
		self.__index += 1
	def op_decptr(self):
		self.__index -= 1
	def op_incvalue(self):
		self.__heap[self.__index] += 1
	def op_decvalue(self):
		self.__heap[self.__index] -= 1
	def op_output(self):
		putchar(self.__heap[self.__index])
	def op_input(self):
		self.__heap[self.__index] = getchar()
	def op_loopbegin(self):
		pass    # TODO
	def op_loopend(self):
		pass    # TODO
	
	def hasop(self, token):
		return token in self.optable
	def getop(self, token, *default):
		return apply(self.optable.get, tuple(token) + default)
	
	def settoken(self, token, opfunc):
		# Do not allow user to set new tokens.
		if token in self.optable:
			self.optable[token] = opfunc

class BF(object):
	__slots__ = [
		'src',
		'optable',
	]
	
	def __init__(self, src, **kwargs):
		self.src = src
		self.optable = BFOpTable()
		# Set user-defined values.
		for optoken in kwargs:
			if isinstance(kwargs[token], list):
				args = tuple([token] + kwargs[token])
			else:
				args = token, kwargs[token]
			apply(optable.settoken, args)
	
	def compile(self):
		return [self.optable.getop(c) for c in self.src if self.optable.hasop(c)]
	def run(self):
		[op() for op in self.compile()]


def help():
	progname = os.path.basename(sys.argv[0])
	print "  Usage: {0} filename [filename2 ...]".format(progname)

def main():
	if empty(sys.argv[1:]):
		help()
		# TODO
		# Show help if '-h' supplied.
		# If no arguments, run interpreter.
	for file in sys.argv[1:]:
		try:
			if file == '-':
				f = sys.stdin
			else:
				f = open(file, 'r')
			src = ''.join(f.readlines())
			BF(src).run()
		except IOError, e:
			print >>sys.stderr, e


if __name__ == '__main__':
	main()
