import requests, json, re, argparse, os
from pprint import pprint
from bs4 import BeautifulSoup
from sys import argv

os.system("clear")

TORRENTS = []

def get_torrents(url, t):
	try:
		r = requests.get(url, timeout=7)
	except requests.Timeout:
		print('Request timeout')
		return None
	else:
		torrents = {}
		torrents.update({'url':url})
		torrents.update({'title':t})
		torrents.update({'year': url[-4:]})
		soup = BeautifulSoup(r.text, 'html.parser')
		links = soup.find_all('a');
		for link in links:
			title = link.get('title')
			if title:
				if t in title and 'Torrent' in title and not 'BluRay' in title: 
					tor = link.get('href')[link.get('href').rfind("/")+1:]
					res = re.search(r"(\d+)p", title)
					if res:
						res = res.group(1)
						torrents.update({res:{}})
						torrents[res].update({'link': tor})
						torrents[res].update({'url': link.get('href')})
		return torrents

def addTorrent(torrent):
	keys = list(torrent.keys())

	if '1080' in keys:
		return torrent['1080']['link']
	elif '720' in keys:	
		return torrent['720']['link']
	else:
		return ""

def doSomething(torrents):
	for i,movie in enumerate(torrents):
		print("{0} : {1} - {2}".format(len(torrents)-i, movie['title'], movie['year']))
	
	choices = []
	if len(torrents) == 1:
		choices = [0]
	else:
		numbers = input("please select films to add (numbers separated by a space ex: 1 2 4) : ")
		if numbers:
			if numbers == 'data':
				pprint(torrents)
				doSomething(torrents)
				return None
			else:	
				choices = [len(torrents)-int(s) for s in numbers.split(" ")]
	names_to_add = []
	torrents_to_add = []
	for i in choices:
		# print("added {}".format(torrents[i]['title']))
		names_to_add.append(torrents[i]['title'])
		torrents_to_add.append(addTorrent(torrents[i]))
	#addNames(names_to_add)
	#addTorrents(torrents_to_add)
	for t in torrents_to_add: TORRENTS.append(t)

def search(name):
	print("searching for: ", name)
	torrents = []
	movie_name = name.replace(' ', '+')
	URL = "https://yts.mx/ajax/search?query="+movie_name
	try:
		r = requests.get(URL, timeout=7)
	except requests.Timeout:
		print("request timeout")
	else:
		data = json.loads(r.text)
		if "data" in data.keys():
			for film in data["data"]:
				torrents.append(get_torrents(film["url"], film["title"]))	
			doSomething(torrents)
			print("")
		else:
			print("no result for ", name)

def files(movies):
	films = open(movies, "r").read().splitlines() 
	for f in films:
		if f != "":
			if f[0] != '"':
				search(f)

def show_search(data):
	for film in data:
		print(film["title"], film["year"], film["url"])
		pprint(get_torrents(film["url"], film["title"]))


# Uncomment this for testing
if __name__ == "__main__":
	if len(argv) > 1:
		for i in range(1, len(argv), 2):
			if argv[i] == '-s':
				search(argv[i+1])
			if argv[i] == '-f':
				print("reading file:",argv[i+1])
				files(argv[i+1])
	else:
		while True:
			i = input("Film: ")
			if i == "exit":
				break	
			search(i)

	for t in TORRENTS:
		print(t)

# vim:tabstop=4:shiftwidth=4:noexpandtab
