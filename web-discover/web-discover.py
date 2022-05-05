import threading as th
import requests as req
from requests_html import HTMLSession
import sys, argparse, time, signal, os

class app:
	def __init__(self, url: str, wordlist=None, method=None, use_js=False):
		self.url = url
		self.session = HTMLSession()
		self.iter_var = None
		self.method = None
		self.mode = None
		self.efficiency = 0
		self.count_ = 0
		self.threading_stat = []
		self.thread_eff_toggle = True
		self.set_thread = False
		self.threads_used = 1
		self.thread_count = 0
		self.app_running = True

		if wordlist != None:
			self.wordlist = open(wordlist).read().split('\n')
			self.jobs = len(self.wordlist)
		else:
			self.wordlist = None

	def __put_payload__(self, payload_type: str, input_payload: str) -> str:
		strings = self.url.split(payload_type)
		strings[-1] = input_payload

		return ''.join(strings)

	def __set_thread__(self):
		if self.set_thread == False:
			thread_number = []
			thread_times = []
			times = []
			for threads in self.threading_stat:
				thread_number.append(threads[0])
				thread_times.append(threads[1])

			for thread in range(20):
				times.append( thread_number[thread_times.index(min(thread_times))] )

			self.threads_used = sum(times)//len(times)
			self.set_thread = True
		else:
			return 0

	def __thread_efficiency__(self, samples=10):
		if self.thread_eff_toggle != True:
			return 0

		if len(self.threading_stat) == (samples*10):
			self.__set_thread__()
			return 0

		if self.count_ == 0:
			self.efficiency = time.time()
		end = None
		self.count_ += 1
		#print(self.count_)
		if self.count_ == samples:
			end = time.time()
			self.count_ = 0

		if end != None:
			speed = end - self.efficiency
			#print(speed)
			self.threading_stat.append((self.threads_used, speed))
			self.threads_used += 1

	def __request_methods__(self):
		return req.get #for now

	def __request_headers__(self):
		return {'User-Agent':'Web-Discover\\'+self.mode}

	def __request_cookies__(self):
		pass

	def __basic_requester__(self, url):
		method = self.__request_methods__()
		headers = self.__request_headers__()
		cookies = self.__request_cookies__()

		try:
			response = method(url, headers=headers, cookies=cookies)
		except:
			self.app_running = False
			print('Couldn\'t connect to host, Try Again...')
			exit()

		return [response.status_code,
			response.content, #for now
			response.headers,
			response.cookies,
			response.links ]
	
	def __requester__(self):
		pass #need to learn more about threading library for this

	def fuzzer(self):
		self.mode = 'Fuzzer'
		is_url = self.urlcheck(self.url)

		payload = ['!-a', '!-n']
		payload_used = None

		if is_url == True:
			for each in payload:
				result = self.url.find(each)
				if result >= 0:
					payload_used = each
					break

			if payload_used == None:
				print('No payload[ <!a> ] detected')
				exit()
		elif is_url == False:
			print('Invalid Url!')
			exit()

		if self.wordlist == None:
			print('Wordlist Needed')
			exit()
		
		job_count = self.jobs
		start = time.time()
		while True:
			if self.app_running == False:
				exit()
			word = self.wordlist[0]
			url = self.__put_payload__(payload_used, word)
			if th.active_count() <= self.threads_used:
				self.__thread_efficiency__()
				fuzz_thread = th.Thread(target=self.__basic_requester__, args=[url])
				fuzz_thread.start()
				self.wordlist.remove(word)
				job_count -= 1
			self.__progress__(self.jobs-job_count, self.jobs)
			if job_count == 0:
				break
		end = time.time()
		print('\n'+str(self.jobs), 'done in '+str(end - start))

	def fork_proxy(self):
		pass

	def scanner(self):
		pass

	def __modes__(self, mode):
		modes = ['fuzzer', 'fork-proxy', 'scanner']

		index = modes.index(mode)
		print(modes[index][0].upper() + modes[index][1:], 'Selected')

		if modes[index] == modes[0]:
			self.fuzzer()
		elif modes[index] == modes[1]:
			self.fork_proxy()
		elif modes[index] == modes[2]:
			self.scanner()

	def urlcheck(self, url):
		if url == None:
			return False

		protocols = ['http://', 'https://', 'ftp://']
		proto = None
		domain = None
		for protocol in protocols:
			result = url.find(protocol)

			if result >= 0:
				proto = protocols[result]
			else:
				continue
		try:
			domain = url.split(proto)[1]
		except:
			domain = None
		if proto == None and domain == None:
			return False
		else:
			return True

	def __progress__(self, current, max_val):
		if self.app_running == False:
			exit()
		state = 'Optimizing...'
		if self.set_thread == True:
			state = 'Optimized using '+str(self.threads_used)+' threads'
		if max_val+1-current == max_val:
			if os.name == 'nt':
				os.system('cls')
			elif os.name == 'posix':
				os.system('clear')
		width=60
		sys.stdout.write('\r')
		sys.stdout.write("\033[%d;%dH" % (1, 1))
		sys.stdout.write(state+'')
		sys.stdout.write("\033[%d;%dH" % (2, 1))
		sys.stdout.write("[%-60s] %d%%" % ('-'*int( (current/(max_val-1))*width ), (current/(max_val-1))*100 ) )
		sys.stdout.flush()

	def __call__(self):
		pass

def main():
        main_parser = argparse.ArgumentParser(prog=sys.argv[0],
                                         usage='%(prog)s [mode] [options]',
                                         description='This tool enumerates information from websites')
        main_parser.add_argument('mode',
                                choices=('fuzzer','fork-proxy','scanner'),
                                help='modes available ( fuzzer, fork-proxy, scanner )')
        main_parser.add_argument('-u',
                            metavar='',
                            type=str,
                            help='url of the website')
        main_parser.add_argument('-w',
        			metavar='',
        			type=str,
        			help='path to wordlist to be used')
        main_parser.add_argument('--run-javascript',
        			metavar='',
        			type=bool,
        			help='use this flag if you want to enable javascript')
        main_parser.add_argument('-m',
        			metavar='',
        			type=str,
        			help='request type (get, post, head, options, delete) ')

        args = main_parser.parse_args()
        return args

if __name__ == '__main__':
        args = main()
        print(args)
        app(args.u, wordlist=args.w, method=args.m, use_js=args.run_javascript).__modes__(args.mode)



        
