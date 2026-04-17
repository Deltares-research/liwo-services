import os
import io
import zipfile
import subprocess
import pathlib
import tempfile
import logging


def add_result_to_zip(result, url, data_dir):
    """Build a zip of requested layers on disk and return its path.

    Caller is responsible for removing the returned file after sending.
    """
    log_stream = io.StringIO()
    layer_logger = logging.getLogger("layer-export")
    layer_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(log_stream)
    layer_logger.addHandler(handler)

    # Disk-backed zip — no RAM blowup for large TIFFs/shapefiles.
    tmp_zip = tempfile.NamedTemporaryFile(prefix="liwo_", suffix=".zip", delete=False)
    tmp_zip.close()

    shapefile_added = set()
    try:
        with zipfile.ZipFile(tmp_zip.name, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for row in result:
                items = row[0].split(",")
                for item, item_type in zip(items[:-1:2], items[1::2]):
                    if "shape" in item_type:
                        table = item
                        filename = table.split(".")[-1]
                        if filename in shapefile_added:
                            layer_logger.debug(f"skipping duplicate shapefile {filename}")
                            continue
                        with tempfile.TemporaryDirectory(prefix="liwo_") as tmp_dir:
                            path = pathlib.Path(tmp_dir) / (filename + ".shp")
                            args = [
                                "pgsql2shp",
                                "-f", str(path),
                                "-h", url.host,
                                "-p", str(url.port),
                                "-u", url.username,
                                url.database,
                                table,
                            ]
                            try:
                                process = subprocess.run(
                                    args, capture_output=True, timeout=600
                                )
                            except Exception as e:
                                layer_logger.exception(f"pgsql2shp crashed for {table}: {e}")
                                continue

                            if process.returncode:
                                layer_logger.debug(
                                    f"error exporting {table}: {' '.join(args)}\n"
                                    f"stdout:\n{process.stdout!r}\nstderr:\n{process.stderr!r}"
                                )
                                continue

                            for f in pathlib.Path(tmp_dir).glob("*"):
                                zf.write(f, f.name)
                            layer_logger.debug(f"table {table} added")
                            shapefile_added.add(filename)

                    elif "tif" in item_type:
                        try:
                            path = data_dir / item.lstrip("/")
                            zf.write(path, path.name)
                            layer_logger.debug(f"item {item} added")
                        except Exception as e:
                            layer_logger.exception(f"error adding tif {item}: {e}")

            zf.writestr("log.txt", log_stream.getvalue())
    except Exception:
        os.unlink(tmp_zip.name)
        raise
    finally:
        layer_logger.removeHandler(handler)

    return tmp_zip.name