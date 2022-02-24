import os
import flask
from markupsafe import escape
import requests
import database
import models
import werkzeug.utils
import valoStore


UPLOAD_FOLDER = '/Users/pptide/Programming/lineupServer/static/usercontent'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'gif', "png"}

app = flask.Flask(__name__)
app.secret_key = "NGjehngsrkhgjsezjkgbjzFG"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
  return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def mapChoice():
  output = ""
  r = requests.get('https://valorant-api.com/v1/maps')
  #r = requests.get('https://valorant-api.com/v1/maps', params={"language": "de-DE"})
  maps = r.json()
  for map in maps["data"]:
    output += "<a href='{}'>{}</a>; ".format(flask.url_for(".agentChoice", map=map["uuid"]), map["displayName"])
  return output

@app.route("/<map>")
def agentChoice(map):
  mapData = getMap(map)
  output = "<h1>agent Choice for map {}</h1>".format(mapData["data"]["displayName"])
  r = requests.get('https://valorant-api.com/v1/agents')
  #r = requests.get('https://valorant-api.com/v1/agents', params={"language": "de-DE"})
  agents = r.json()
  for agent in agents["data"]:
    output += "<a href='{}'>{}</a>; ".format(flask.url_for(".lineups", map=map, agent=agent["uuid"]), agent["displayName"])
  return output

@app.route("/<map>/<agent>")
def lineups(map, agent):
  #return "lineups für {} auf {}".format(getAgent(agent)["data"]["displayName"], getMap(map)["data"]["displayName"])
  #return str(models.Lineup.query.filter(models.Lineup.map == map and models.Lineup.agent == agent).first())
  output = ""
  lineupsis = models.Lineup.query.filter(models.Lineup.map == map).filter(models.Lineup.agent == agent).all()
  print(lineupsis)
  if not lineupsis:
    return flask.redirect(flask.url_for(".addLineups", map=map, agent=agent))
  for stf in lineupsis:
    output += "<a href='{}'>{}</a>; ".format(flask.url_for(".lineup", name=str(stf)), str(stf)) #str(stf) + "; "
  return output


@app.route("/<map>/<agent>/add", methods=("GET", "POST"))
def addLineups(map, agent):
  if flask.request.method == "POST":
    name = flask.request.form["name"]
    error = None

    if not name:
      error = "Name benötigt"

    print("Ja" if 'file' not in flask.request.files else "Nein")
    if 'file' not in flask.request.files:
      flask.flash('No file part')
      return flask.redirect(flask.request.url)
    file = flask.request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
      flask.flash('No selected file')
      return flask.redirect(flask.request.url)
    if file and allowed_file(file.filename):
      safeName = werkzeug.utils.secure_filename(name)
      filename = werkzeug.utils.secure_filename(file.filename)
      os.mkdir(os.path.join(app.config["UPLOAD_FOLDER"], safeName))
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], safeName, filename))

    if error == None:
      print(name)
      #try:
      l = models.Lineup(name, map, agent)
      database.db_session.add(l)
      print(name)
      i = models.Image(name, os.path.join("usercontent", safeName, filename))
      database.db_session.add(i)
      database.db_session.commit()
      #except database.db_session.IntegrityError:
      #  error = f"Lineup {name} already exists."
      #else:
      return flask.redirect(flask.url_for(".lineups", map=map, agent=agent))

    flask.flash(error)
  
  return flask.render_template("lineup/add.html")
  #return "lineups für {} auf {} hinzufügen".format(getAgent(agent)["data"]["displayName"], getMap(map)["data"]["displayName"])
  #return str(models.Lineup.query.filter(models.Lineup.map == map and models.Lineup.agent == agent).first())

@app.route("/lineup/<name>")
def lineup(name):
  image_paths = [image.path for image in models.Image.query.filter(models.Image.lineup_name == name)]
  return flask.render_template("lineup/show.html", name=name, image_paths=image_paths)

@app.route("/store")
def store():
  return valoStore.getStore()

def getMap(uuid):
  r = requests.get('https://valorant-api.com/v1/maps/{}'.format(uuid))
  return r.json()

def getAgent(uuid):
  r = requests.get('https://valorant-api.com/v1/agents/{}'.format(uuid))
  return r.json()


@app.teardown_appcontext
def shutdown_session(exception=None):
  database.db_session.remove()