""" String Utility functions """
import re


def append_re_line_sequence(filename, linepattern, newline):
	""" Detects the re 'linepattern' in the file. After its last occurrence,
	paste 'newline'. If the pattern does not exist, append the new line
	to the file. Then, write. """
	with open(filename, 'r') as f:
		oldfile = f.read()
	lines = re.findall(linepattern, oldfile, flags=re.MULTILINE)
	if len(lines) == 0:
		with open(filename, 'a') as f:
			f.write(newline)
		return
	last_line = lines[-1]
	newfile = oldfile.replace(last_line, last_line + newline + '\n')
	with open(filename, 'w') as f:
		f.write(newfile)

def remove_pattern_from_file(filename, pattern):
	""" Remove all occurrences of a given pattern from a file. """
	with open(filename, 'r') as f:
		oldfile = f.read()
	pattern = re.compile(pattern, re.MULTILINE)
	with open(filename, 'w') as f:
		f.write(pattern.sub('', oldfile))

def str_to_fancyc_comment(text):
	""" Return a string as a C formatted comment. """
	l_lines = text.splitlines()
	if len(l_lines[0]) == 0:
		outstr = "/*\n"
	else:
		outstr = "/* " + l_lines[0] + "\n"
	for line in l_lines[1:]:
		if len(line) == 0:
			outstr += " *\n"
		else:
			outstr += " * " + line + "\n"
	outstr += " */\n"
	return outstr

def str_to_python_comment(text):
	""" Return a string as a Python formatted comment. """
	l_lines = text.splitlines()
	if len(l_lines[0]) == 0:
		outstr = "#\n"
	else:
		outstr = "# " + l_lines[0] + "\n"
	for line in l_lines[1:]:
		if len(line) == 0:
			outstr += "#\n"
		else:
			outstr += "# " + line + "\n"
	outstr += "#\n"
	return outstr

def strip_default_values(string):
	""" Strip default values from a C++ argument list. """
	return re.sub(' *=[^,)]*', '', string)

def strip_arg_types(string):
	""""
	Strip the argument types from a list of arguments.
	Example: "int arg1, double arg2" -> "arg1, arg2"
	Note that some types have qualifiers, which also are part of
	the type, e.g. "const std::string &name" -> "name", or
	"const char *str" -> "str".
	"""
	string = strip_default_values(string)
	return ", ".join(
				[part.strip().split(' ')[-1] for part in string.split(',')]
			).replace('*','').replace('&','')

def strip_arg_types_grc(string):
	"""" Strip the argument types from a list of arguments for GRC make tag.
	Example: "int arg1, double arg2" -> "$arg1, $arg2" """
	if len(string) == 0:
		return ""
	else:
		string = strip_default_values(string)
		return ", ".join(['${' + part.strip().split(' ')[-1] + '}' for part in string.split(',')])

def is_number(s):
	""" Return True if the string s contains a number. """
	try:
		float(s)
		return True
	except ValueError:
		return False

def strcmpi(str1,str2):
	"""
	string comparison case-insensitive
	@str1: Base string
	@str2: Second string to compare with basestring
	@return: True is strings match, False if they don'tell
	"""
	try:
		
		if(not isinstance(str1,str) or not isinstance(str2,str)):
			return False
		
		return (str1.lower() == str2.lower())
	except Exception as e:
		print('Exception in strcmpi(): %s' %e)
		return False

def str_to_type(string,num_type='float'):
	"""
	This method attempts to cast a string to either a float if it's a number
	or a bool is the string is either True or False
	
	Args:
		string (str):  string to be cast
		num_type (str [optional]): default cast type to use if the string is a number.
			must be a valid python number type - int or float.
		
	Returns:
		val (int,float,bool,str): string value as a float if it's numeric, a bool
			if its True/False or a string if those casts fail
	"""
	if type(string) is type(str()):
		if string.lower() == 'true':
			return bool(1)
		elif string.lower() == 'false':
			return bool(0)
		else:
			return string
	else:
		if num_type.lower() == 'float':
			try:
				return float(string)
			except:
				return string
		elif num_type.lower() == 'int':
			try:
				return int(string)
			except:
				return string

def str_to_list(string, dlmtr = ';'):
	""" Takes a dlmtr-separated string and returns a parsed list of strings. """
	return string.split(dlmtr)

def list_to_str(lst, dlmtr = ','):
	"""	Converts a list to a comma separated string """
	raw_str = "".join(str(elem) + dlmtr for elem in lst)
	s = raw_str[:-1]	#trim off the trailing ','
	return s

def params_str_to_dict(string):
	""" Takes a 'params' string and returns a parsed dictionary. 
		@string (str): A string of semi-colon-separated 'key=value' substrings. 
			In addition, the value may be a comma-separated list of numbers. 
			For example, for a subelement containing:
			   'param1=val;param2=val2;param3=1,2,3;param4=4'
			this function returns the following dict:
				{'param1':'val', 'param2':'val2', 'param3':[1,2,3], 'param4':'4'}
		@return (dict): dictionary of parsed strings
	"""
	plist = string.split(';')   #semi-colon splits key/value pairs\
	k = []
	v = []
	for p in plist:
		kvList = p.split('=')   #split key/value pair by =
		if len(kvList) == 2:
			k.append(kvList[0])
			v.append(kvList[1])
		else:
			raise Exception('params_str_to_dict invalid string format: %s'%string)
				
	tmpDict = dict(zip(k,v))
	pDict = {}

	# iterate through dict and see if any strings are comma separated 
	# and split into lists, then repack dict
	for key,val in tmpDict.iteritems():
		tmpLst = []
		if isinstance(val,str):
			tmpLst = val.split(',')
			if len(tmpLst) > 1:
				pDict[key] = map(float,tmpLst)
			else:
				pDict[key] = tmpDict[key]
		else:
			pDict[key] = tmpDict[key]

	return pDict

def ask_yes_no(question, default=False):
	""" Asks a binary question. Returns True for yes, False for no.
	default is given as a boolean. """
	question += {True: ' [Y/n] ', False: ' [y/N] '}[default]
	if input(question).lower() != {True: 'n', False: 'y'}[default]:
		return default
	else:
		return not default
