#!/usr/bin/env python
# coding: utf-8
# vim: set noet:

import sys
import os





# Helper functions
def empty(list): return len(list) == 0

def isseq(value):
	return isinstance(value, list) \
		or isinstance(value, tuple) \
		or isinstance(value, dict)

def dump(*args):
	print repr(args)
	# if isseq(args):
	# 	[dump(_) for _ in args]
	# else:
	# 	return repr(args)

def reversed_dict(d):
	return dict([[d[key], key] for key in d])

def getchar():
	c = sys.stdin.read(1)
	if c == '':
		return None
	else:
		return ord(c)

def putchar(c):
	return sys.stdout.write(chr(c))

def hasidx(seq, idx):
	return 0 <= idx and idx < len(seq)

class NoLoopBeginOpError(Exception):
	def __str__(self):
		return "No op 'op_loopbegin'."

class NoLoopEndOpError(Exception):
	def __str__(self):
		return "No op 'op_loopend'."


class BF(object):
	__slots__ = ['src', 'optable', '__heap', '__heapindex', '__ops', '__opsindex']
	
	def __init__(self, src, **kwargs):
		self.src = src
		# Set user-defined values.
		for optoken in kwargs:
			if isinstance(kwargs[token], list):
				args = tuple([token] + kwargs[token])
			else:
				args = token, kwargs[token]
			apply(self.settoken, args)
		
		self.optable = self.getdefaultops()
		# TODO: Use bytearray not list
		# TODO: Make the number value customizable
		self.__heap = [0 for times in range(30)]
		self.__heapindex = 0
		self.__ops = None
		self.__opsindex = None
	
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
		# print "incptr"
		self.__heapindex += 1
		self.__opsindex += 1
	def op_decptr(self):
		# print "decptr"
		self.__heapindex -= 1
		self.__opsindex += 1
	def op_incvalue(self):
		# print "incvalue"
		self.__heap[self.__heapindex] += 1
		self.__opsindex += 1
	def op_decvalue(self):
		# print "decvalue"
		self.__heap[self.__heapindex] -= 1
		self.__opsindex += 1
	def op_output(self):
		# print "output"
		putchar(self.__heap[self.__heapindex])
		self.__opsindex += 1
	def op_input(self):
		# print "input"
		c = getchar()
		if c is None:    # EOF
			sys.exit(0)    # Is it right way?
		self.__heap[self.__heapindex] = c
		self.__opsindex += 1
	def op_loopbegin(self):
		# print "loopbegin"
		if self.__heap[self.__heapindex] == 0:
			while True:
				if not hasidx(self.__ops, self.__opsindex):
					raise NoLoopEndOpError()
				if self.__ops[self.__opsindex] == self.op_loopend:
					self.__opsindex += 1    # next op is not op_loopend(), is next op of op_loopend().
					break
				self.__opsindex += 1
		else:
			self.__opsindex += 1
	
	def op_loopend(self):
		# print "loopend"
		while True:
			if not hasidx(self.__ops, self.__opsindex):
				raise NoLoopBeginOpError()
			if self.__ops[self.__opsindex] == self.op_loopbegin:
				break
			self.__opsindex -= 1


	
	def compile(self):
		if self.__ops is None:
			self.__ops = [self.getop(c) for c in self.src if self.hasop(c)]
			self.__opsindex = 0
	
	def run(self):
		self.compile()
		while True:
			if not hasidx(self.__ops, self.__opsindex):
				break
			self.__ops[self.__opsindex]()
	
	def hasop(self, token):
		return token in self.optable
	def getop(self, token, *default):
		return apply(self.optable.get, tuple(token) + default)
	
	def settoken(self, token, opfunc):
		# Do not allow user to set new tokens.
		if token in self.optable:
			self.optable[token] = opfunc


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
