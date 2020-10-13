from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker

from flask_sqlalchemy import SQLAlchemy

import json

import liwo_services.settings

def create_app_db():
    env = liwo_services.settings.dotenv_values()
    # Create the application instance
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = env['SQLALCHEMY_DATABASE_URI']
    db = SQLAlchemy(app)
    CORS(app)
    return app, db


app, db = create_app_db()

# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    return {'test': 'hoi'}


@app.route('/liwo.ws/Authentication.asmx/Login', methods=["OPTIONS", "POST"])
def loadLayerSets():
    """
    returns maplayersets. Login is not used anymore, but frontend still expects this.
    frontend will send body {
    username: 'anonymous@rws.nl',
    password: '',
    mode: ''}

    TODO: remove Login part and only return json generated by postgresql function
    """


    con = engine.connect()
    rs = con.execute('SELECT website.sp_selectjson_maplayersets_groupedby_mapcategories()')

    result = rs.fetchall()

    layersets_dict = {
        "mode": "open",
        "layersets": result[0][0],
        "loggedIn": False,
        "liwokey": "-1",
        "error": "",
        "user": {
            "email": "",
            "message": "",
            "role": "Guest",
            "name": "",
            "organisation": "",
            "tools": [],
            "mymaps": [],
            "mapextent": "",
            "webserviceURL": "http://localhost:5000/liwo.ws/",
            "administrator": "false"
        }
    }

    layersets_string = json.dumps(layersets_dict)

    return {"d": layersets_string}

@app.route('/liwo.ws/Tools/FloodImage.asmx/GetScenariosPerBreachGeneric', methods=["POST"])
def loadBreachLayer():
    """
    Return Scenarios for a breachlocation.

    body: {
      breachid: breachId,
      layername: layerName
    })

     Based on layername a setname is defined.
     In the database function this is directly converted back to the layername.
     TODO: remove setname directly use layerName.
    """

    body = request.get_json()

    # Setnames according to c-sharp backend
    setnames = {
        "waterdiepte": "Waterdiepte_flood_scenario_set",
        "stroomsnelheid": "Stroomsnelheid_flood_scenario_set",
        "stijgsnelheid": "Stijgsnelheid_flood_scenario_set",
        "schade": "Schade_flood_scenario_set",
        "slachtoffers": "Slachtoffers_flood_scenario_set",
        "getroffenen": "Getroffenen_flood_scenario_set",
        "aankomsttijd": "Aankomsttijd_flood_scenario_set"
    }

    # Default value for setname
    default_setname = "Waterdiepte_flood_scenario_set"
    setname = setnames.get(body['layername'], default_setname)
    breachid = body['breachid']

    Session = sessionmaker(bind=engine)
    session = Session()

    query = "SELECT website.sp_selectjson_maplayerset_floodscen_breachlocation_id_generic({}, '{}')".format(breachid, setname)

    con = engine.connect()
    rs = con.execute(query)
    result = rs.fetchall()
    return {"d": json.dumps(result[0][0])}


@app.route('/liwo.ws/Maps.asmx/GetLayerSet', methods=["POST"])
def loadLayerSetById():
    """
    body: { id }
    """

    body = request.get_json()
    id = body['id']

    Session = sessionmaker(bind=engine)
    session = Session()

    query = "SELECT website.sp_selectjson_layerset_layerset_id({})".format(id)

    con = engine.connect()
    rs = con.execute(query)
    result = rs.fetchall()
    return {"d": json.dumps(result[0][0])}

@app.route('/liwo.ws/Maps.asmx/GetBreachLocationId', methods=["POST"])
def getFeatureIdByScenarioId():
    """
    body:{ mapid: scenarioId }
    """
    body = request.get_json()
    floodsimulationid = body['floodsimulationid']

    Session = sessionmaker(bind=engine)
    session = Session()

    query = "SELECT static_information.sp_selectjson_breachlocationid({})".format(floodsimulationid)

    con = engine.connect()
    rs = con.execute(query)
    result = rs.fetchall()

    return {"d": json.dumps(result[0][0])}


# @app.route('/Maps.asmx/DownloadZipFileDataLayers')
# def ():
#   return {}


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0')
