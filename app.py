import logging, os, sys, puzzles
from flask import Flask, request, abort, redirect, render_template, send_file
from datetime import datetime, date
from calendar import Calendar
from logging.handlers import RotatingFileHandler
from flask_apscheduler import APScheduler

class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': puzzles.daily_download,
            'trigger': 'interval',
            'hours': 1
        }
    ]

app = Flask(__name__)
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

logger = logging.getLogger('root')
filename, file_extension = os.path.splitext(os.path.basename(__file__))
formatter = logging.Formatter('%(asctime)s - %(levelname)10s - %(module)15s:%(funcName)30s:%(lineno)5s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
logging.getLogger("requests").setLevel(logging.WARNING)
logger.setLevel("DEBUG")
fileHandler = RotatingFileHandler('/app/logs/puzzles.log', maxBytes=1024 * 1024 * 2, backupCount=1)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

@app.route(os.environ['WEB_ROOT'], defaults={'req_path': None}, strict_slashes=False)
@app.route(os.environ['WEB_ROOT'] + '<path:req_path>')
def puzzle_year(req_path):
	if request.path  != '/' and request.path.endswith('/'): return redirect("%s" % request.path[:-1])
	puzzle_path = os.path.join('/app/docs/',str(req_path))
	try:
		if not req_path:
			return redirect("%s/%s" % (os.environ['WEB_ROOT'], date.today().year))
		elif req_path.isnumeric():
			return render_template('cal.html', year=int(req_path), cal=get_cal_list(int(req_path)))
		else:
			if os.path.isfile(puzzle_path):	
				return send_file(puzzle_path)
			else:
				if  "crosswords" in req_path:
					tmp_url = "http://cdn2.amuselabs.com/pmm/crossword-pdf?id=Creators_WEB_%s&set=creatorsweb" % (str(req_path[-14:-4]).replace("-",""))
					return redirect(tmp_url)
				else:
					return redirect("%s/%s" % (os.environ['WEB_ROOT'], date.today().year))
	except:
		raise
		return redirect("%s/%s" % (os.environ['WEB_ROOT'], date.today().year))



def get_cal_list(year):
	cal = Calendar(6)
	cal_list = [
		cal.monthdatescalendar(year, i+1)
		for i in range(12)
	]
	return cal_list
	

