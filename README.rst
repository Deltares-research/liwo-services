=============
LIWO Services
=============


.. image:: https://img.shields.io/pypi/v/liwo_services.svg
        :target: https://pypi.python.org/pypi/liwo_services

.. image:: https://img.shields.io/travis/Deltares/liwo_services.svg
        :target: https://travis-ci.com/Deltares/liwo_services

.. image:: https://readthedocs.org/projects/liwo-services/badge/?version=latest
        :target: https://liwo-services.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/Deltares/liwo_services/shield.svg
     :target: https://pyup.io/repos/github/Deltares/liwo_services/
     :alt: Updates



LIWO Backend Services


* Free software: GNU General Public License v3
* Documentation: https://liwo-services.readthedocs.io.


Features
--------

* Start the services using `FLASK_APP=liwo_services.app:app flask run`.
* Or using a wsgi host using the app `liwo_services.app:app`.
* Or after running `pip install -e .` in the source directory, using the cli `liwo_services run`.

Routes
-----

The following url's should be available:
* download_zip: /liwo.ws/Maps.asmx/DownloadZipFileDataLayers               
* getFeatureIdByScenarioId: /liwo.ws/Maps.asmx/GetBreachLocationId                                          
* home: /                                                                                      
* loadBreachLayer: /liwo.ws/Tools/FloodImage.asmx/GetScenariosPerBreachGeneric 
* loadLayerSetById: /liwo.ws/Maps.asmx/GetLayerSet        
* loadLayerSets: /liwo.ws/Authentication.asmx/Login                          

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
