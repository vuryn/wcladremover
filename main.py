import os
import sys
import requests
from requests_html import HTMLSession
from dataclasses import dataclass

WCL_DOWNLOAD_PAGE = 'https://classic.warcraftlogs.com/client/download'
APPIMAGE_BUILDER_DOWNLOAD_URL = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"

APPIMAGE_BUILDER_PATH = "/app/AppImg.AppImage"
WCL_PATH = "/app/WCL.AppImage"
TMP_DIR = '/app/tmp'


class WCLOS:
    _LINUX = 'Linux'
    _MAC = 'Mac OS X'
    _WINDOWS = 'Windows'

    def __init__(self, os_name):
        assert WCLOS.validate(os_name)
        self.os_name = os_name

    @staticmethod
    def validate(s):
        return s in (WCLOS._LINUX, WCLOS._MAC, WCLOS._WINDOWS)

    @staticmethod
    def LINUX():
        return WCLOS(WCLOS._LINUX)

    @staticmethod
    def MACOS():
        return WCLOS(WCLOS._MAC)

    @staticmethod
    def WINDOWS():
        return WCLOS(WCLOS._WINDOWS)


@dataclass
class Client:
    url: str = ''
    os: WCLOS = None

    @property
    def version(self):
        return self.url.split('/')[-2].strip().lstrip('v')

    @property
    def version_tuple(self):
        return tuple(map(int, self.version.split('.')))


class WCLClient:
    def __init__(self):
        self.os_name_to_client = self.get_current_WCL_version_url()

    def get_current_WCL_version_url(self):
        session = HTMLSession()
        r = session.get(WCL_DOWNLOAD_PAGE)

        output = {}
        for anchor in r.html.find('div.uploader-box > p > a.uploader-link'):
            url = anchor.attrs['href']
            if 'releases' in url:
                _os = WCLOS(anchor.text)
                output[_os.os_name] = Client(url=url, os=_os)
        return output

    def get_client(self, os: WCLOS):
        return self.os_name_to_client[os.os_name]


def main():
    wcl = WCLClient()
    linux_client = wcl.get_client(WCLOS.LINUX())

    print(f"Fetching client from {linux_client.url}")
    sys.stdout.flush()

    # Download WCL client and app-image builder tool
    with open(WCL_PATH, 'wb+') as f:
        r = requests.get(linux_client.url)
        f.write(r.content)

    with open(APPIMAGE_BUILDER_PATH, 'wb+') as f:
        r = requests.get(APPIMAGE_BUILDER_DOWNLOAD_URL)
        f.write(r.content)

    # Make them executable
    os.system(f'chmod +x {APPIMAGE_BUILDER_PATH}')
    os.system(f'chmod +x {WCL_PATH}')

    # Extract WCL
    os.system(f"""{WCL_PATH} --appimage-extract""")

    # Extract ASAR file to folder
    os.system("""cd squashfs-root/resources && npm install asar -y""")
    os.system("""cd squashfs-root/resources && npx asar extract app.asar extracted_folder """)

    # Disable ad service by providing empty stub
    if linux_client.version_tuple < (5, 9, 0):
        ad_service = """class AdService { ensureAdIsLoaded(){/**/} showAd(){/**/} hideAd(){/**/} }\nmodule.exports = { AdService }"""
    else:
        with open('ad-service-stub-since-5.9.0.js', 'r') as f:
            ad_service = f.read()
    with open("/app/squashfs-root/resources/extracted_folder/scripts/services/ad-service.js", 'w+') as f:
        f.write(ad_service)

    # Repack folder to ASAR file and clean up
    os.system("""cd squashfs-root/resources && npx asar pack extracted_folder app.asar""")
    os.system("""cd squashfs-root/resources && rm -rf node_modules package-lock.json extracted_folder""")

    # Run the app-image builder to generate output .AppImage file
    os.system(f"""mkdir {TMP_DIR} && cd tmp && {APPIMAGE_BUILDER_PATH} --appimage-extract""")
    os.system(f"""{TMP_DIR}/squashfs-root/AppRun -n squashfs-root""")

    # Rename to correct version and move
    os.system(f"""mv ./Warcraft* ./Warcraft-Logs-Uploader-{linux_client.version}.AppImage""")
    os.system("""(mkdir /output || true) && cp ./Warcraft* /output """)
    os.system(f"""cp ./Warcraft-Logs-Uploader-{linux_client.version}.AppImage /output/Warcraft-Logs-Uploader-latest.AppImage""")


if __name__ == '__main__':
    main()
