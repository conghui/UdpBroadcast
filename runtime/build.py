#!/usr/bin/python

import os
import sys
import getpass
import subprocess

try:
	from fabricate import *
except ImportError, e:
	print "Couldn't find the fabricate module."
	sys.exit(1)

MAXOSDIR = os.environ['MAXELEROSDIR']
MAXCOMPILERDIR = os.environ['MAXCOMPILERDIR']
DFE_MODEL = 'ISCA'

MAXFILE = 'UdpOneToMany.max'
DESIGN_NAME = MAXFILE.replace('.max', '')
sources = ['test.c']
target = 'test'
includes = []

ip1 = '172.16.50.1'
ip2 = '172.16.60.1'
tap1_ip = '172.16.50.10'
tap2_ip = '172.16.60.10'
tap1_netmask = '255.255.255.0'
init_tap1 = 'QSFP_TOP_10G_PORT1:%s:%s' % (tap1_ip, tap1_netmask)
init_tap2 = 'QSFP_BOT_10G_PORT1:%s:%s' % (tap2_ip, tap1_netmask)

def slicCompile():
	"""Compiles a maxfile in to a .o file"""
	run("%s/bin/sliccompile" % (MAXCOMPILERDIR), MAXFILE, MAXFILE.replace('.max', '.o'))

def getMaxCompilerInc():
	"""Return the includes to be used in the compilation."""
	return ['-I.', '-I%s/include' % MAXOSDIR, '-I%s/include/slic' % MAXCOMPILERDIR]

def getMaxCompilerLibs():
	"""Return the libraries to be used in linking."""
	return ['-L%s/lib' % MAXCOMPILERDIR, '-L%s/lib' % MAXOSDIR, '-lslic', '-lmaxeleros', '-lm', '-lpthread']

def getLinkerLibs():
	"""Returns the libraries to be used for linking."""
	return getMaxCompilerLibs() +  [MAXFILE.replace('.max', '.o')]


cflags = ['-ggdb', '-rdynamic',
		  '-std=gnu99', '-Wall', '-Werror',
		  '-DDESIGN_NAME=%s' % (DESIGN_NAME)] + includes + getMaxCompilerInc()

def build():
	compile()
	link()

def compile():
	slicCompile()
	for source in sources:
		run('gcc', cflags, '-c', source, '-o', source.replace('.c', '.o'))

def link():
	objects = [s.replace('.c', '.o') for s in sources]
	run('gcc', objects, getLinkerLibs(), '-o', target, '-rdynamic')

def clean():
	autoclean()

def getSimName():
	return getpass.getuser() + 'Sim'

def maxcompilersim():
	return '%s/bin/maxcompilersim' % MAXCOMPILERDIR

def run_sim():
	restart_sim()
	subprocess.call(['./' + target, ip1, ip2])

def start_sim():
	subprocess.call([maxcompilersim(), '-n', getSimName(), '-c', DFE_MODEL,
    '-e', init_tap1, '-p', 'QSFP_TOP_10G_PORT1:top1.pcap',
    '-e', init_tap2, '-p', 'QSFP_BOT_10G_PORT1:bot1.pcap', 'restart'])

def stop_sim():
	subprocess.call([maxcompilersim(), '-n', getSimName(), '-e', init_tap1, 'stop'])

def restart_sim():
	start_sim()

def sim_debug():
	subprocess.call(['maxdebug', '-g', 'graph_%s' % getSimName(), '-d',  '%s0:%s' % (getSimName(), getSimName()), MAXFILE])

if __name__ == '__main__':
	main()
