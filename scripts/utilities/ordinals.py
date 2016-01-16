import math

suffixes = ['dummy', 'st', 'nd', 'rd', 'th']

ordinals = ['', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 
	'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth',
	'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth']

ones = ['dummy', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
	'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'sventeen',
	'eighteen', 'nineteen']

teens = ['eleven', 'twelve']

tens = ['dummy', 'ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

powers = ['dummy', 'ten', 'hundred', 'thousand', 'million', 'billion', 'trillion', 'quadrillion', 
'quintillion', 'sextillion', 'septillion', 'octillion', 'nontillion', 'decillion', 'centillion']

def parse_ones(digit, suffix=True):
	return ordinals[digit] if suffix else ones[digit]

def parse_tens(digit, suffix=True):
	if suffix:
		return tens[digit/10].replace('y', 'ie') + suffixes[-1]
	else:
		return tens[digit/10]

def parse_tens_mixed(digit, suffix=True):
	if(digit%10==0):
		return parse_tens(digit, suffix)
	else:
		if digit <= 20:
			return ordinals[digit] if suffix else ones[digit]
		else:
			return tens[digit/10] + '-' + parse_ones(digit%10, suffix)

def parse_hundreds(digit, suffix=True):
	if suffix:
		return ones[int(str(digit)[0])] + ' ' + powers[int(math.log(digit, 10))] + suffixes[-1]
	else:
		return ones[int(str(digit)[0])] + ' ' + powers[int(math.log(digit, 10))]

def parse_hundreds_mixed(digit,suffix=True):
	if(digit%100==0):
		return parse_hundreds(digit, suffix=True)
	else:
		return parse_hundreds(digit, suffix=False) + ' and ' + parse_tens_mixed(digit%100, suffix)

def parse_chunks(chunks):
	if len(chunks) > len(powers)-3:
		return "Idk, %s?" % powers[-1]

	ordinal = ''
	for i in xrange(len(chunks)):
		suffix = False if i != len(chunks)-1 else True
		ordinal += ' ' if i != 0 else ''
		if(len(str(int(chunks[i])))==3):
			ordinal += parse_hundreds_mixed(int(chunks[i]), suffix)
		elif(len(str(int(chunks[i])))==2):
			ordinal += parse_tens_mixed(int(chunks[i]), suffix)
		elif(len(str(int(chunks[i])))==1):
			ordinal += parse_ones(int(chunks[i]), suffix)
		ordinal += ' ' + powers[len(chunks)+1-i] if i != len(chunks)-1 else ''
	return ordinal

def ordinal_string(digit):
	ordinal = ''
	digit_str = str(digit)
	trailing_digits = digit_str[len(digit_str)%3:]
	leading_digits = digit_str[:len(digit_str)%3] if len(digit_str)%3 != 0 else 0

	chunks = [trailing_digits[i:i+3] for i in xrange(0, len(trailing_digits), 3)]
	if leading_digits != 0:
		chunks = [leading_digits] + chunks
	ordinal =  parse_chunks(chunks)

	return ordinal
