# LIWO Services

LIWO Backend Services

* Free software: GNU General Public License v3
* Documentation: [https://liwo-services.readthedocs.io](https://liwo-services.readthedocs.io)

## Update dependencies

### docker uses pip

Install from requirements:
`pip install --upgrade -r requirements.txt`

Update requirements.txt:
`pip list --format=freeze > requirements.txt`

### pixi is easier

`pixi install` (default includes dev)

or

`pixi install -e prod`

to run the backend:

`pixi run start`

This will open teh backend on [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Features

* Start the services using `FLASK_APP=liwo_services.app:app flask run`.
* Or using a wsgi host using the app `liwo_services.app:app`.
* Or after running `pip install -e .` in the source directory, using the cli `liwo_services run`.

## Routes

The following url's are available:

* home: /
* download_zip: /liwo.ws/Maps.asmx/DownloadZipFileDataLayers
* getFeatureIdByScenarioId: /liwo.ws/Maps.asmx/GetBreachLocationId
* loadBreachLayer: /liwo.ws/Tools/FloodImage.asmx/GetScenariosPerBreachGeneric
* loadLayerSetById: /liwo.ws/Maps.asmx/GetLayerSet
* loadLayerSets: /liwo.ws/Authentication.asmx/Login

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
