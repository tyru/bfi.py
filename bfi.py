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
				'INCPTR': '>',
				'DECPTR': '<',
				'INCVALUE': '+',
				'DECVALUE': '-',
				'OUTPUT': '.',
				'INPUT': ',',
				'LOOPBEGIN': '[',
				'LOOPEND': ']',
			}.items():
			self.tokens[key] = val
		# Set user-defined values.
		for key, val in kwargs.items():
			if key in self.tokens:
				self.tokens[key] = val
	
	def run(self):
		print "src =", repr(self.src)


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
