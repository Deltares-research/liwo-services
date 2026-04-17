
import requests
from pathlib import Path

def test_download(url, name, data):
    res = requests.post(url, json=data)
    code = res.status_code
    assert code == 200
    download = res.content
    path = Path(__file__).parent / name
    output_path = str(path)
    assert not path.exists()

    with open(output_path, "wb") as file_obj:
        file_obj.write(download)
    print(f"Saved {len(download) / (1024 * 1024):.2f} megabytes to {output_path}")
    assert path.exists()
    path.unlink()
    print(f'downloaded {name}')

def test_download_small():
    print('testing download_small')
    base = "http://localhost:5001/"
    url = base + "liwo.ws/Maps.asmx/DownloadZipFileDataLayers_v2"
    name =  "test_download_small.zip"
    data = {'layers': 'MaximaleWaterdiepteNederland_Kaart1', 'name': name}
    test_download(url, name, data)

def test_download_large():
    print('testing download_large')
    base = "http://localhost:5001/"
    url = base + "liwo.ws/Maps.asmx/DownloadZipFileDataLayers_v2"
    name =  "test_download_large.zip"
    data = {'layers': 'MaximaleWaterdiepteNederland_Kaart5', 'name': name}
    test_download(url, name, data)

if __name__ == "__main__":
    test_download_small()
    test_download_large()




