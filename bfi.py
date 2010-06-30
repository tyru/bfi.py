#!/usr/bin/env python
# coding: utf-8
# vim: set noet:

import sys
import os





# Helper functions
def empty(list):
	return len(list) == 0

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



# Exceptions
class NoLoopBeginOpError(Exception):
	def __str__(self):
		return "No op 'op_loopbegin'."

class NoLoopEndOpError(Exception):
	def __str__(self):
		return "No op 'op_loopend'."




class BFOpsTable(object):
	__slots__ = ['__optable']
	
	def __init__(self):
		self.__optable = BFOpsTable.getdefaultops()

	def hasop(self, token):
		return token in self.__optable
	def getop(self, token, *default):
		return apply(self.__optable.get, tuple(token) + default)
	
	def settoken(self, token, opfunc):
		# Do not allow user to set new tokens.
		if token in self.__optable:
			self.__optable[token] = opfunc
	
	@staticmethod
	def getdefaultops():
		return {
			'>': BFOpsTable.op_incptr,
			'<': BFOpsTable.op_decptr,
			'+': BFOpsTable.op_incvalue,
			'-': BFOpsTable.op_decvalue,
			'.': BFOpsTable.op_output,
			',': BFOpsTable.op_input,
			'[': BFOpsTable.op_loopbegin,
			']': BFOpsTable.op_loopend,
		}
	
	@staticmethod
	def op_incptr(bfm, pc):
		# print "incptr"
		bfm.heapindex += 1
		return pc + 1
	
	@staticmethod
	def op_decptr(bfm, pc):
		# print "decptr"
		bfm.heapindex -= 1
		return pc + 1
	
	@staticmethod
	def op_incvalue(bfm, pc):
		# print "incvalue"
		bfm.heap[bfm.heapindex] += 1
		return pc + 1
	
	@staticmethod
	def op_decvalue(bfm, pc):
		# print "decvalue"
		bfm.heap[bfm.heapindex] -= 1
		return pc + 1
	
	@staticmethod
	def op_output(bfm, pc):
		# print "output"
		putchar(bfm.heap[bfm.heapindex])
		return pc + 1
	
	@staticmethod
	def op_input(bfm, pc):
		# print "input"
		c = getchar()
		if c is None:    # EOF
			sys.exit(0)    # Is it right way?
		bfm.heap[bfm.heapindex] = c
		return pc + 1
	
	@staticmethod
	def op_loopbegin(bfm, pc):
		# print "loopbegin"
		if bfm.heap[bfm.heapindex] == 0:
			ops = bfm.ops
			while True:
				if not hasidx(ops, pc):
					raise NoLoopEndOpError()
				if ops[pc] == BFOpsTable.op_loopend:
					pc += 1    # next op is not op_loopend(), is next op of op_loopend().
					break
				pc += 1
			return pc
		else:
			return pc + 1
	
	@staticmethod
	def op_loopend(bfm, pc):
		# print "loopend"
		ops = bfm.ops
		while True:
			if not hasidx(ops, pc):
				raise NoLoopBeginOpError()
			if ops[pc] == BFOpsTable.op_loopbegin:
				break
			pc -= 1
		return pc

class BFMachine(object):
	__slots__ = [
		'__src',
		'__optable',
		'heap',
		'heapindex',
		'ops',
		'__opsindex',
		'__compile_options',
	]
	
	def __init__(self, file, **kwargs):
		self.__src = ''.join(file.readlines())
		# Set user-defined values.
		for optoken in kwargs.get('tokens', []):
			if isinstance(kwargs[token], list):
				args = tuple([token] + kwargs[token])
			else:
				args = token, kwargs[token]
			apply(self.__optable.settoken, args)
		
		self.__optable = BFOpsTable()
		# TODO: Use bytearray not list
		self.heap = [0 for times in range(kwargs.get('heaplen', 30))]
		self.heapindex = 0
		self.ops = None
		self.__opsindex = None
		self.__compile_options = {'unroll_loop': 0}
		if 'compile_with' in kwargs:
			self.__compile_options.update(kwargs['compile_with'])
	
	def compile(self):
		if self.ops is not None:
			return
		self.ops = [self.__optable.getop(c) for c in self.__src if self.__optable.hasop(c)]
		if self.__compile_options.get('unroll_loop', 0):
			self.unroll_loop()
		self.__opsindex = 0
	
	def unroll_loop(self):
		for op in self.ops:
			if op == BFOpsTable.op_output or op == BFOpsTable.op_input:
				self.__opsindex += 1
			elif op == BFOpsTable.op_loopbegin:
				pass    # TODO
			elif op == BFOpsTable.op_loopend:
				pass    # TODO
			else:
				self.call_op()
	
	def call_op(self):
		# Do not let ops change `self.__opsindex` not by return value.
		self.__opsindex = self.ops[self.__opsindex](self, self.__opsindex)
	
	def run(self):
		self.compile()
		while hasidx(self.ops, self.__opsindex):
			self.call_op()


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
			BFMachine(f).run()
		except IOError, e:
			print >>sys.stderr, e


if __name__ == '__main__':
	main()
