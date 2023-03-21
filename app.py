import requests
import click
import os
import cgi

class Downloader:
    def __init__(self, sessionCookie, maxrange):
        os.makedirs("downloads", exist_ok=True)
        self.cookies = {"PHPSESSID": sessionCookie}
        self.headers = {"User-Agent": r"""Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"""}
        self.collectedFiles = [int(x.split("_")[0]) for x in os.listdir("downloads")]
        self.maxrange = maxrange

    def request(self, url, method=requests.get, attempts=10, timeout=10, *args, **kwargs):
        for attempt in range(attempts):
            try:
                r = method(url=url, timeout=timeout, *args, **kwargs)
                print(f"[{r.url}] (status_code:{r.status_code} len:{len(r.content)})")
                if r.cookies:
                    self.cookies = {**self.cookies, **dict(r.cookies)}
                if r.status_code == 404:
                    return None
                elif not r.ok:
                    continue
                return r

            except requests.RequestException as error:
                print(error)
        print("Could not recover from error")
        return None

    def start(self):
        for fileId in [x for x in range(self.maxrange) if x not in self.collectedFiles]:
            r = self.request("https://presetshare.com/download/index",
                             params={"id": fileId},
                             cookies=self.cookies,
                             allow_redirects=False)
            if r is None:
                continue
            value, params = cgi.parse_header(r.headers["Content-Disposition"])
            filename = str(fileId) + "_" + params["filename"]
            path = f"downloads/{filename}"
            if os.path.exists(path):
                continue
            with open(path, "wb") as f:
                f.write(r.content)


@click.command()
@click.option('--phpsessid', required=True, help="enter your phpsessid cookie here (you can find it in your browser in presetshare.com)")
@click.option('--maxrange', default=10000, help="number of preset ID's to check")
def start(phpsessid, maxrange):
    if len(phpsessid) != 26:
        print("Invalid PHPSESSID cookie, collect your login cookie and run the program with: `python app.py <PHPSESSID>`")
        return
    Downloader(sessionCookie=phpsessid, maxrange=maxrange).start()

if __name__ == "__main__":
    start()