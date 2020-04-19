import os, logging, urllib.request, time, errno
from datetime import datetime, timedelta
from PyPDF2 import PdfFileReader

logger = logging.getLogger('root')

def daily_download():
	today = datetime.now().strftime("%Y-%m-%d")
	download_all(today)

def download_all(download_date):
	logger.info("Downloading Puzzles for %s" % download_date)
	for puzzle in ["crosswords", "sudoku"]:
		download_puzzle(puzzle, download_date)

def download_puzzle(puzzle, puzzle_date):
	(puzzle_links, solution_links, filename) = create_links(puzzle, puzzle_date)
	
	path = "/app/docs"
	index = 0
	for links in [puzzle_links, solution_links]:
		index+=1
		if index == 1:
			kind = "puzzle"
		elif index == 2:
			kind = "solution"

		full_filename = "%s/%s/%s/%s" % (path, puzzle, kind, filename)
		if os.path.exists(full_filename) and not validPDF(full_filename):
			logger.info("File Was Found But Was Not Valid PDF, Deleting")
			os.remove(full_filename)

		if os.path.exists(full_filename):
			logger.info("Puzzle Aleady Exists at %s" % full_filename)
		else:
			logger.info("Downloading %s %s to %s" % (puzzle, kind, full_filename))
			download_pdf(links, full_filename, puzzle)

def download_pdf(links, filename, puzzle):
	for x, link in enumerate(links):
		logger.info("Attempting to Download from %s" % link)
		success =  download_file(link, filename, puzzle)
		if success:
			logger.info("Puzzle Successfully Downloaded")
			break
		else:
			if os.path.exists(filename): os.remove(filename)
			if x + 1 == len(links):
				logger.info("Puzzle Failed to Download")
				return False

def create_links(puzzle, puzzle_date):
	puzzle_links = []
	solution_links = []
	puzzle_date = datetime.strptime(puzzle_date, "%Y-%m-%d")
	sudoku_date = datetime.strftime(puzzle_date, "%Y/%m/%Y-%m-%-d")
	crossword_format = puzzle_date.strftime('%y%m%d')
	filename = "%s.pdf" % puzzle_date.strftime('%Y-%m-%d')

	if puzzle == "crosswords":
		puzzle_links.append("http://cdn2.amuselabs.com/prints/Creators_WEB_20" + crossword_format + ".pdf")
		solution_links.append("http://cdn2.amuselabs.com/prints/Creators_WEB_20" + crossword_format +  "_solution.pdf")
		puzzle_links.append("http://www.brainsonly.com/servlets-newsday-crossword/newsdaycrosswordPDF?pm=pdf&puzzle=" + crossword_format + "1&data=%3CNAME%3E" + crossword_format + "%3C%2FNAME%3E%3CTYPE%3E1%3C%2FTYPE%3E")
		solution_links.append("http://www.brainsonly.com/servlets-newsday-crossword/newsdaycrosswordPDF?pm=pdf&puzzle=" + crossword_format + "2&data=%3CNAME%3E" + crossword_format + "%3C%2FNAME%3E%3CTYPE%3E2%3C%2FTYPE%3E")
	elif puzzle == "sudoku":
		puzzle_links.append("http://www.dailysudoku.com/sudoku//pdf/%s_S2_N1.pdf" % sudoku_date)
		solution_links.append("http://www.dailysudoku.com/sudoku//pdf/%s_S2_N1_X.pdf" % sudoku_date)

	return puzzle_links, solution_links, filename

def download_file(download_url, filename, puzzle):
	try:
		create_folder(filename)
		web_file = urllib.request.urlopen("%s" % download_url).read()
		local_file = open(filename, 'wb')
		local_file.write(web_file)
		local_file.close()
		return not os.path.getsize(filename) < 3000 if validPDF(filename) else False 
	except urllib.error.HTTPError:
		return False
	except:
		return False

def validPDF(filename):
	try:	
		PdfFileReader(filename)
		return True
	except:
		return False

def create_folder(filename):
	if not os.path.exists(os.path.dirname(filename)):
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				pass

def download_between_dates(start_date, end_date):
	start_date = datetime.strptime(start_date, "%Y-%m-%d")
	end_date = datetime.strptime(end_date, "%Y-%m-%d")
	delta = end_date - start_date

	for i in range(delta.days + 1):
		date = datetime.strftime(start_date + timedelta(days=i), "%Y-%m-%d")
		download_all(date)
		time.sleep(1)
