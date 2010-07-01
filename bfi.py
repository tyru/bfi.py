#!/usr/bin/env python
# coding: utf-8
# vim: set noet:

import sys
import os


# TODO: JIT compilation



# Helper functions
def empty(list):
	return len(list) == 0

def isseq(value):
	return isinstance(value, list) \
		or isinstance(value, tuple) \
		or isinstance(value, dict)

def dump(args):
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
class BFBaseException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class NoLoopBeginOpError(BFBaseException):
	def __init__(self):
		BFBaseException.__init__(self, "No op 'op_loopbegin'.")

class NoLoopEndOpError(BFBaseException):
	def __init__(self):
		BFBaseException.__init__(self, "No op 'op_loopend'.")

class InternalError(BFBaseException):
	def __init__(self):
		BFBaseException.__init__(self, "Sorry, internal error.")

class FixedHeapError(BFBaseException):
	def __init__(self):
		BFBaseException.__init__(self, "op_incptr() tried to extend heap but interpreter's heap fixed.")

class MismatchParenthesis(BFBaseException):
	pass

class InvalidParameter(BFBaseException):
	pass




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
		# TODO: Do this at op_incvalue(), op_decvalue()
		# if bfm.extend_heap_on_write is true.
		if not hasidx(bfm.heap, bfm.heapindex):
			if bfm.is_fixed_heap:
				raise FixedHeapError()
			else:
				bfm.extend_heap()
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
			while ops[pc] != BFOpsTable.op_loopend:
				pc += 1
			pc += 1    # next op is not op_loopend(), is next op of op_loopend().
			return pc
		else:
			return pc + 1
	
	@staticmethod
	def op_loopend(bfm, pc):
		# print "loopend"
		ops = bfm.ops
		while ops[pc] != BFOpsTable.op_loopbegin:
			pc -= 1
		return pc

class BFMachine(object):
	__slots__ = [
		'__src',
		'__optable',
		'__defaultheaplen',
		'heap',
		'heapindex',
		'ops',
		'__pc',
		'__compile_options',
		'is_fixed_heap',
		'__extend_heap_len',
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
		
		self.__defaultheaplen = kwargs.get('heaplen', 30)
		self.clear_heap()
		
		self.ops = None
		self.__pc = None
		
		self.__compile_options = {'unroll_loop': 0}
		if 'compile_with' in kwargs:
			self.__compile_options.update(kwargs['compile_with'])
		
		self.is_fixed_heap = kwargs.get('is_fixed_heap', 0)
		self.__extend_heap_len = kwargs.get('extend_heap_len', 30)
		if self.__extend_heap_len <= 0:
			raise InvalidParameter("'extend_heap_len' must be positive number.")
	
	def clear_heap(self):
		self.heap = bytearray([0 for times in range(self.__defaultheaplen)])
		self.heapindex = 0
	
	def extend_heap(self):
		self.heap.extend([0 for times in range(self.__extend_heap_len)])
	
	def compile(self):
		# TODO: BF program which has `infinite loop` can't be unrolled.
		# Prepare threshold for `unroll_times` for such program.
		if self.ops is not None:
			return
		self.ops = []
		has_loop = 0
		loop_paren_count = 0
		for c in self.__src:
			if self.__optable.hasop(c):
				op = self.__optable.getop(c)
				self.ops.append(op)
				if op == BFOpsTable.op_loopbegin:
					has_loop = 1
					loop_paren_count += 1
				elif op == BFOpsTable.op_loopend:
					loop_paren_count -= 1
				if loop_paren_count < 0:
					raise MismatchParenthesis("No left '[' correspond to ']'.")
		if loop_paren_count != 0:
			if loop_paren_count > 0:
				raise MismatchParenthesis("No right ']' correspond to '['.")
		self.__pc = 0
		if has_loop and self.__compile_options.get('unroll_loop', 0):
			self.unroll_loop()
	
	def unroll_loop(self):
		calling_op = set([BFOpsTable.op_incptr, BFOpsTable.op_decptr, BFOpsTable.op_incvalue, BFOpsTable.op_decvalue])
		while hasidx(self.ops, self.__pc):
			op = self.ops[self.__pc]
			if op == BFOpsTable.op_output or op == BFOpsTable.op_input:
				self.__pc += 1
			elif op in calling_op:
				self.call_op()
			elif op == BFOpsTable.op_loopbegin:
				unroll_times = 0
				loopbegin_index = self.__pc
				loopend_index = -1
				while hasidx(self.ops, self.__pc):
					if self.ops[self.__pc] == BFOpsTable.op_loopbegin:
						if self.heap[self.heapindex] == 0:
							if unroll_times == 0:
								while op != BFOpsTable.op_loopend:
									self.ops.pop(self.__pc)
									op = self.ops[self.__pc]
								# Remove also `BFOpsTable.op_loopend`.
								self.ops.pop(self.__pc)
							else:
								# Remove op_loopend, op_loopbegin.
								self.ops.pop(loopend_index)
								self.ops.pop(loopbegin_index)
								# Unroll body ops.
								unroll_ops = self.ops[loopbegin_index:loopend_index-1]
								unroll_ops_num = len(unroll_ops)
								self.ops[loopbegin_index:loopend_index-1] = unroll_ops * unroll_times
								self.__pc += unroll_ops_num
								break
						else:
							unroll_times += 1
							self.call_op()    # Let `op_loopbegin` advance `self.__pc`.
					else:
						if self.ops[self.__pc] == BFOpsTable.op_loopend \
						and loopend_index == -1:
							loopend_index = self.__pc
						self.call_op()
			elif op == BFOpsTable.op_loopend:
				raise InternalError("unroll_loop(): `op` must NOT be `BFOpsTable.op_loopend`.".format(op.func_name))
			else:
				raise InternalError("Unknown method '{0}'.".format(op.func_name))
		# Initialize attributes for real `run()`!
		self.clear_heap()
		self.__pc = 0
	
	def call_op(self):
		# Do not let ops change `self.__pc` not by return value.
		self.__pc = self.ops[self.__pc](self, self.__pc)
	
	def run(self):
		self.compile()
		while hasidx(self.ops, self.__pc):
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
		except BFBaseException, e:
			print >>sys.stderr, e


if __name__ == '__main__':
	main()
