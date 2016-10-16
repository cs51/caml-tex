#! /usr/bin/env python

"""
A python version of caml-tex.

Known problems: 
	- Trailing comments are not handled properly 
		(anything after ;; is treated as output)
	- -n, -w arguments do nothing (need to understand what they did previously)
"""

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

def process_inline(line):
	joined = '\\?{' + line + '}\n'
	return joined

def process_outline(line):
	return '\\:{' + line + '}\n'

END_REGEX = "\\end{caml_(example|example\*|eval)}\s*"

START_ECHO_EXAMPLE = r'\\begin{caml_example}\s*'

START_NOECHO_EXAMPLE = r'\\begin{caml_example*}\s*'

START_EVAL = r'\\begin{caml_eval}\s*'

def read_ml_block(filepointer, ocaml_session, echo_eval=True):
	total_eval = ''

	ml = ""

	while True:
		l = filepointer.readline()

		# unexpected EOF
		if l is None:
			print "Opened ML expression never closed."
			exit(1)

		# found the end of the block
		elif re.search(END_REGEX, l):
			break

		# if an ocaml expression ends here
		elif ";;" in l:
			ml = ml + l

			# send the ML to the ocaml shell
			ocaml_session.sendline(ml)

			# wait for the command to finish evaluating
			ocaml_session.expect('#')

			# get back what we just sent and evaluated
			evaled = ocaml_session.before

			# getting a bit hacky here...
			# find where to split input and output
			indx =  evaled.find(';;')
			
			# input is before the ;;
			inputted = evaled[:indx + 2]
			# output is after the 
			outputted = evaled[indx + 2:]

			clean_input = map(process_inline,
				 	filter(lambda s : len(s) > 0, 
						map(lambda s : s.strip(), inputted.split('\r\n'))))

			clean_output = map(process_outline, 
					filter(lambda s : len(s) > 0,
						map( lambda s : s.strip(), outputted.split('\r\n'))))

			if echo_eval:
				total_eval += ''.join(clean_input) + ''.join(clean_output)
			else:
				total_eval += ''.join(clean_input)

			ml = ""

		# seeing more ML

		else:
			ml = ml + l

	return total_eval

import pexpect

def convert_to_ml(filename, outfilename):

	# start up and wait for the shell to be ready 
	ocaml_session = pexpect.spawn('ocaml')
	ocaml_session.expect("#")

	# get the source file and the output file
	try:
		infile = open(filename, 'r')
	except Exception as e:
		print "Input file error: {}".format(e)
		exit(1)
	
	try:
		outfile = open(outfilename, 'w')
	except Exception as e:
		print "Output file error: {}".format(e)
		exit(1)

	while True:

		l = infile.readline()

		# if we've hit end of line, get out of here
		if not l:
			infile.close()
			outfile.close()
			exit(0)

		if re.search(START_ECHO_EXAMPLE, l):
			evaled = read_ml_block(infile, ocaml_session)

			outfile.write('\\begin{caml}\n')
			outfile.write(evaled)
			outfile.write('\\end{caml}\n')

		elif re.search(START_NOECHO_EXAMPLE, l):
			evaled = read_ml_block(infile, ocaml_session, add_eval = False)

			outfile.write('\\begin{caml}\n')
			outfile.write(evaled)
			outfile.write('\\end{caml}\n')

		# add the evaled block through the session
		# but don't echo the output
		elif re.search(START_EVAL, l):
			read_ml_block(infile, ocaml_session)

		# otherwise, this line is just .tex and should be echoed
		else:
			outfile.write(l)


if __name__ == '__main__':
	(options, args) = read_options()

	for arg in args:
		
		if options.outfile is "":
			options.outfile = arg + '.tex'	

		convert_to_ml(arg, options.outfile)

		break






