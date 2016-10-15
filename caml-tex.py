#! /usr/bin/env python

import re
from optparse import OptionParser
import os
import subprocess

def read_options():

	parser = OptionParser()

	parser.add_option('-n', '--length', dest="linelength",
						default = 72,
						help="set the line length.")
	parser.add_option('-o', '--outfile', dest='outfile', 
						default = "",
						help='set the output .tex file')
	parser.add_option('-w' , '--cut', dest='cut_at_blanks', 
						default = 0,
						help='set the cut at blanks value.')

	return parser.parse_args()

START_REGEX = r'\\begin{caml_(example|example\*|eval)}\s*'
END_REGEX = r'\\end{caml_(example|example\*|eval)}\s*'

def read_ml_block(filepointer):
	ml = ""

	while True:
		l = filepointer.readline()

		# unexpected EOF
		if l is None:
			print "Opened ML expression never closed."
			exit(1)

		# if end of an ML embedding, move on
		if re.search(END_REGEX, l):
			return ml
		# seeing more ML
		else:
			ml = ml + l

OUTFILE = 'input.ml'

def extract_ml(filename):
	try:
		with open(filename, 'r') as infile:
			while True:
				l = infile.readline()

				if not l:
					break

				if re.search(START_REGEX, l):
					ml = read_ml_block(infile)

					with open(OUTFILE, 'a') as outfile:
						outfile.write(ml)

	except Exception as e:
		print e
		exit(1)

def eval_output():

	with open(OUTFILE, 'r') as mlfile:
		with open('evaled.txt', 'w') as outfile:
			try:
				
				toplevel = subprocess.check_output('ocaml', stdin = mlfile) 

				return toplevel

			except subprocess.CalledProcessError as e:
				print e
				exit(2)

def build_outfile(optional, infile):
	if optional is "":
		return infile + '.tex'

			
def swap_eval(infilename, outfilename, evaled_output):
	try:
		infile = open(infilename, 'r')
	except:
		print "Could not open infile."
		exit(3)

	try:
		outfile = open(outfilename, 'w')
	except:
		print "Could not open output .tex file."
		exit(3)


if __name__ == '__main__':
	(options, args) = read_options()

	try:
		os.remove(OUTFILE)
	except OSError:
		pass

	for arg in args:
		
		extract_ml(arg)
		
		output = eval_output()

		outfile = build_outfile(options.outfile, arg)

		swap_eval(arg, outfile, output)

		break






