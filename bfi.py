#!/usr/bin/env python
# coding: utf-8
# vim: set noet:

import sys
import os





# Helper functions
def empty(list): return len(list) == 0

def dump(*args):
	print repr(args)



class BF(object):
	__slots__ = [
		'src',
		'tokens',
	]
	
	def __init__(self, src, **kwargs):
		self.src = src
		self.tokens = {}
		# Set default values.
		for key, val in {
				'incptr': '>',
				'decptr': '<',
				'incvalue': '+',
				'decvalue': '-',
				'output': '.',
				'input': ',',
				'loopbegin': '[',
				'loopend': ']',
			}.items():
			self.tokens[key] = val
		# Set user-defined values.
		for key, val in kwargs.items():
			if key in self.tokens:
				self.tokens[key] = val
		# Reverse dictionary.
		self.tokens = dict([[val, key] for key, val in self.tokens.items()])
	
	def op_incptr(self):
		print 'op_incptr'
	def op_decptr(self):
		print 'op_decptr'
	def op_incvalue(self):
		print 'op_incvalue'
	def op_decvalue(self):
		print 'op_decvalue'
	def op_output(self):
		print 'op_output'
	def op_input(self):
		print 'op_input'
	def op_loopbegin(self):
		print 'op_loopbegin'
	def op_loopend(self):
		print 'op_loopend'
	
	def compile(self):
		return [getattr(self, 'op_' + self.tokens[c]) for c in self.src if c in self.tokens]
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
