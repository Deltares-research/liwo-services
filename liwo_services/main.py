import json
import logging
import os
import pathlib

import flask
import sqlalchemy.engine.url
from sqlalchemy import text
from flask import Blueprint, Flask, request
from flask_caching import Cache
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# side effect loads the env
import sys
sys.path.append('.')
import liwo_services
import liwo_services.export
import liwo_services.settings
from liwo_services.utils import _post_request_cache_key

logger = logging.getLogger(__name__)


def create_app_db():
    """load the dot env values"""
    liwo_services.settings.load_env()

    # Create the application instance
    app = Flask(__name__)

    # add db settings
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["DATA_DIR"] = os.environ.get("DATA_DIR", "")

    # Add cache
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = os.environ.get(
        "CACHE_DEFAULT_TIMEOUT", 0
    )  # infinite
    cache = Cache(app)

    # add cors headers
    CORS(app)

    # load the database
    db = SQLAlchemy(app)
    logger.info(
        "loaded database %s, files from %s",
        app.config["SQLALCHEMY_DATABASE_URI"],
        app.config["DATA_DIR"],
    )
    return app, db, cache


app, db, cache = create_app_db()

v1 = Blueprint("version1", "version1")
v2 = Blueprint("version2", "version2")


# Create a URL route in our application for "/"
@v1.route("/")
@v2.route("/")
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    return {"liwo_service": "Hello World"}

@v1.route("/liwo.ws/Authentication.asmx/Login", methods=["OPTIONS", "POST"])
@v2.route("/liwo.ws/Authentication.asmx/Login", methods=["OPTIONS", "POST"])
@cache.cached()
def loadLayerSets():
    """
    returns maplayersets. Login is not used anymore, but frontend still expects this.
    frontend will send body {
    username: 'anonymous@rws.nl',
    password: '',
    mode: ''}

    TODO: remove Login part and only return json generated by postgresql function
    """
    qLayerSet = text("SELECT website.sp_selectjson_maplayersets_groupedby_mapcategories()")
    rs = db.session.execute(
        qLayerSet
    )

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
            "webserviceURL": os.environ["WEBSERVICE_URL"],
            "administrator": "false",
        },
    }

    layersets_string = json.dumps(layersets_dict)

    return {"d": layersets_string}

@v1.route(
    "/liwo.ws/Tools/FloodImage.asmx/GetScenariosPerBreachGeneric", methods=["POST"]
)
@cache.cached(make_cache_key=_post_request_cache_key)
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

    body = request.json

    # Set names according to c-sharp backend
    set_names = {
        "waterdiepte": "Waterdiepte_flood_scenario_set",
        "stroomsnelheid": "Stroomsnelheid_flood_scenario_set",
        "stijgsnelheid": "Stijgsnelheid_flood_scenario_set",
        "schade": "Schade_flood_scenario_set",
        "slachtoffers": "Slachtoffers_flood_scenario_set",
        "getroffenen": "Getroffenen_flood_scenario_set",
        "aankomsttijd": "Aankomsttijd_flood_scenario_set",
    }

    # Default value for setname
    default_set_name = "Waterdiepte_flood_scenario_set"
    set_name = set_names.get(body.get("layername", ""), default_set_name)
    breach_id = body["breachid"]

    # define query with parameters
    query = text("SELECT website.sp_selectjson_maplayerset_floodscen_breachlocation_id_generic(:breach_id, :set_name)")

    rs = db.session.execute(query, {"breach_id": breach_id, "set_name": set_name})
    result = rs.fetchone()
    return {"d": json.dumps(result[0])}

@v2.route("/load_breach_layer", methods=["POST"])
@cache.cached(make_cache_key=_post_request_cache_key)
def load_breach_layer():
    """
    Return scanarios for a breachlocation.

    body: {
        breachid: breachid
    }
    """

    body = request.json
    breach_id = body["breachid"]

    query = text("SELECT website.load_breach_layer(:breach_id)")

    rs = db.session.execute(query, {"breach_id": breach_id})
    result = rs.fetchone()
    return json.dumps(result[0])

@v2.route("/filter_variants", methods=["GET"])
def filter_variants():
    """
    Return list of filter properties for variants
    """

    properties = ["Overschrijdingsfrequentie", "Status SVK", "Bres", "Moment van falen", "Toestand SVK", "Waterstandsverloop"
    , "Bresvorming dijk", "Bresvorming kunstwerk", "Standzekerheid achterliggende lijnelementen", "Ingrepen in watersysteem", "Klimaatscenario"
    , "VariantKeuze_1", "VariantKeuze_2", "VariantKeuze_3", "VariantKeuze_4", "VariantKeuze_5", "VariantKeuze_6"]

    return json.dumps(properties)


@v1.route("/liwo.ws/Maps.asmx/GetLayerSet", methods=["POST"])
@v2.route("/liwo.ws/Maps.asmx/GetLayerSet", methods=["POST"])
@cache.cached(make_cache_key=_post_request_cache_key)
def loadLayerSetById():
    """
    body: { id }
    """
    body = request.json
    layerset_id = body["id"]

    # TODO: use params option in execute.
    query = text("SELECT website.sp_selectjson_layerset_layerset_id(:layerset_id)")

    rs = db.session.execute(query, {"layerset_id": layerset_id})
    result = rs.fetchone()

    return {"d": json.dumps(result[0])}


@v1.route("/liwo.ws/Maps.asmx/GetBreachLocationId", methods=["POST"])
@v2.route("/liwo.ws/Maps.asmx/GetBreachLocationId", methods=["POST"])
@cache.cached(make_cache_key=_post_request_cache_key)
def getFeatureIdByScenarioId():
    """
    body:{ floodsimulationid: scenarioId }
    """
    body = request.json

    flood_simulation_id = body["floodsimulationid"]

    # TODO: use params option in execute
    query = text(
        "SELECT static_information.sp_selectjson_breachlocationid(:flood_simulation_id)"
    )

    rs = db.session.execute(query, {"flood_simulation_id": flood_simulation_id})
    result = rs.fetchone()

    return {"d": json.dumps(result[0])}


@v1.route("/liwo.ws/Maps.asmx/DownloadZipFileDataLayers", methods=["POST"])
@v2.route("/liwo.ws/Maps.asmx/DownloadZipFileDataLayers", methods=["POST"])
def download_zip():
    """
    body: {"layers":"scenario_18734,gebiedsindeling_doorbraaklocaties_buitendijks","name":"test"}
    """
    body = request.json
    layers = body.get("layers", "").split(",")
    layers_str = body.get("layers", "")
    name = body.get("name", "").strip()
    if not name:
        name = "DownloadLIWO"

    data_dir = pathlib.Path(app.config["DATA_DIR"])

    # security check
    for layer in layers:
        if ".." in layer or layer.startswith("/"):
            raise ValueError("Security issue: layer name not valid")

    query = text("SELECT website.sp_select_filepaths_maplayers(:map_layers)")
    rs = db.session.execute(query, dict(map_layers=layers_str))
    # Results in the comma seperated list
    # [('static_information.tbl_breachlocations,shape1,static_information_geodata.infrastructuur_dijkringen,shape',)]
    result = rs.fetchall()

    # lookup relevant parts for cli script
    url = sqlalchemy.engine.url.make_url(app.config["SQLALCHEMY_DATABASE_URI"])

    # load datasets in a zip file
    zip_stream = liwo_services.export.add_result_to_zip(result, url, data_dir)

    resp = flask.send_file(
        path_or_file=zip_stream,
        mimetype="application/zip",
        download_name="{}.zip".format(name),
        as_attachment=True,
    )
    return resp

app.register_blueprint(v1, name="api_v1", url_prefix="/api/v1")
app.register_blueprint(v2, name="api_v2", url_prefix="/api/v2")
app.register_blueprint(v1, name="root", url_prefix="/")
app.register_blueprint(v1, name="api", url_prefix="/api")

if __name__ == "__main__":
    # Only for debugging while developing
    portnumber = 80
    if os.environ.get("PORT") is not None:
        portnumber = os.environ.get("PORT")
    
    app.run(host="0.0.0.0", debug=True, port=portnumber, threaded=True)
