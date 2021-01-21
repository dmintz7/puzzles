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
	rp = request.path 
	if rp != '/' and rp.endswith('/'): return redirect("%s" % rp[:-1])
	cal = Calendar(6)
	year = None
	try:
		if not req_path:
			puzzle_path = ""
			year = date.today().year
			if rp.endswith('/'):
				return redirect("%s%s" % (rp, year))
			else:
				return redirect("%s/%s" % (rp, year))
		else:
			try:
				if req_path.split('/')[1] == "today":
					puzzle = req_path.split('/')[0]
					if len(req_path.split('/')) > 2:
						type = req_path.split('/')[2]
					else:
						type = "puzzle"

					return redirect("/%s/%s/%s.pdf" % (puzzle, type, datetime.today().strftime('%Y-%m-%d')))
			except:
				pass
		
			if req_path.isnumeric():
				puzzle_path = ""
				year = int(req_path)
			else:
				puzzle_path = os.path.join('/app/docs/',req_path)

		if os.path.isfile(puzzle_path):	
			return send_file(puzzle_path)
		elif year:
			cal_list = [
				cal.monthdatescalendar(year, i+1)
				for i in range(12)
			]
			return render_template('cal.html', year=year, cal=cal_list)
		else:
			if  "crosswords" in req_path:
				new_url = "http://cdn2.amuselabs.com/pmm/crossword-pdf?id=Creators_WEB_%s&set=creatorsweb" % (str(req_path[-14:-4]).replace("-",""))
				return redirect(new_url)
			else:
				return "No File Found"
	except:
		abort(404)