
import asyncio
import re
from trans import *

FILE_NAME = '/home/utylee/utylee/saul.txt'



phase_num = 1

def get_current_phase():
	global phase_num
	return phase_num

def proceed_phase():
	global phase_num
	phase_num = phase_num + 1
	if phase_num > 3:
		phase_num = 1
	print('phase_num : {}'.format(phase_num))

async def main():
	lines = []
	with open(FILE_NAME, 'r') as f:
		lines = f.readlines()
		
	with open(FILE_NAME + '.translate', 'w') as w:

		cur_order = 1
		text = ''
		result_lines = []
		for line in lines:
			#if cur_order == 50:
				#break
			if get_current_phase() == 1:
				w.write(line)
				#result_lines.append(line)
				key_text = '{}\\n'.format(cur_order)
				found = re.search(key_text, line)
				if found.group(0) is not None:
					print('{} : {} {}'.format('1-order', cur_order, found.group(0)))
					proceed_phase()
					cur_order = cur_order + 1
			elif get_current_phase() == 2:
				w.write(line)
				#result_lines.append(line)
				key_text = '\d\d:\d\d:\d\d,'
				found = re.search(key_text, line)
				if found.group(0) is not None:
					print('{} : {} {}'.format('2-time', cur_order, found.group(0)))
					proceed_phase()
			elif get_current_phase() == 3:
				if line != '\n':
					text = text + ' ' + line.strip()
					#lines.remove(line)
				else:
					korean = translate(text, 'ko')
					#result_lines.append(text + '\n' + korean)
					w.write(text + '\n' + korean +'\n\n')
					print('{} : {} {}\n{}'.format('3-text', cur_order, text, korean))
					#print('{} : {} {}'.format('3-text', cur_order, korean))
					text = ''
					proceed_phase()

	#with open(FILE_NAME + '.translate', 'wb') as w:
		#w.writelines(result_lines)


	#print(result_lines)


loop = asyncio.get_event_loop()

loop.run_until_complete(main())

