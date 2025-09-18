import io
import zipfile
import subprocess
import pathlib
import tempfile
import logging


def add_result_to_zip(result, url, data_dir):
    """add item to zipfile. this requires extra info from url, retrieve data from data_dir"""
    # TODO Add custom log stream for invalid layers
    log_stream = io.StringIO()
    # define a handler
    layer_logger = logging.getLogger('layer-export')
    layer_logger.setLevel(logging.DEBUG)
    for handler in layer_logger.handlers:
        layer_logger.removeHandler(handler)
    # add the new handler
    handler = logging.StreamHandler(log_stream)
    layer_logger.addHandler(handler)

    zip_stream = io.BytesIO()

    shapefile_added = set()
    with zipfile.ZipFile(zip_stream, 'w') as zf:
        for row in result:
            items = row[0].split(',')
            # this is an odd format
            # ('static_information.tbl_breachlocations,shape1,static_information_geodata.infrastructuur_dijkringen,shape',)
            for item, item_type in zip(items[:-1:2], items[1::2]):
                if 'shape' in item_type:
                    table = item
                    filename = table.split('.')[-1]
                    shapefile_added.add(filename)
                    if filename in shapefile_added: # avoid duplicates
                        layer_logger.debug(f"skipping duplicate shapefile {filename}")
                        continue
                    with tempfile.TemporaryDirectory(prefix='liwo_') as tmp_dir:
                        # export table to shapefile
                        path = pathlib.Path(tmp_dir) / (filename + '.shp')
                        # Password should be available in evironment variable: PGPASSWORD
                        #pgsql2shp -f C:\tmp\test.shp -h localhost -p 5434 -u postgres -P liwo liwo static_information_geodata.evac_droge_verdiepingen_gebouwen_nederland5

                        args = [
                            "pgsql2shp",
                            "-f", str(path),
                            "-h", url.host,
                            "-p", str(url.port),
                            "-u", url.username,
                            url.database,
                            table
                        ]
                        # TODO: how to just pass args
                        cmd = " ".join(args)
                        try:
                            process = subprocess.run(cmd, shell=True, capture_output=True,timeout=600)

                        except Exception as e:
                            path_temp = pathlib.Path(tmp_dir) / "log_temp.txt"
                            with path_temp.open('w') as fout:
                                fout.write(e)

                        if process.returncode:
                            layer_logger.debug(f"error exporting {table}: {' '.join(args)}\nstdout:\n{process.stdout}\nstderr:\n {process.stderr}")
                        for f in pathlib.Path(tmp_dir).glob('*'):
                            zf.write(f, f.name)
                        layer_logger.debug(f"table {table} added")
                elif 'tif' in item_type:
                    try:
                        path = data_dir / item.lstrip('/')
                        zf.write(path, path.name)
                        layer_logger.debug(f"item {item} added")
                    except Exception as e:
                        zf.writestr('log_temp.txt', str(e))
        zf.writestr('log.txt', log_stream.getvalue())
        

    # rewind
    zip_stream.seek(0)
    return zip_stream
