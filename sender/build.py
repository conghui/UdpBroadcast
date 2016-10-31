#!/usr/bin/python

import os
import sys

try:
	from fabricate import *
except ImportError, e:
	print "Couldn't find the fabricate module."
	sys.exit(1)

sources = ['sender.c', 'receiver.c']
target = ['sender', 'receiver']
includes = []

cflags = ['-O2', '-std=gnu99'] + includes

def build():
	compile()
	link()

def compile():
	for source in sources:
		run('gcc', cflags, '-c', source, '-o', source.replace('.c', '.o'))

def link():
  for obj in [s.replace('.c', '.o') for s in sources]:
    run('gcc', obj, '-o', obj.replace('.o', ''))

def clean():
  for obj in [s.replace('.c', '.o') for s in sources]:
    run('rm', '-f', obj)
    run('rm', '-f', obj.replace('.o',''))

if __name__ == '__main__':
	main()
