import requests
from bs4 import BeautifulSoup

every_game_log_link = []


# gibt html code der gewünschten url zurück
def get_url_content(url):
    return requests.get(url).text


if __name__ == '__main__':
    count = 1
    i = 2160
    file_count = 1
    while i <= 10000:
        url = 'http://itikawa.com/kifdb/herodb.cgi?table=bg&view=M&sort=1&order=D&recpoint=' + str(i)

        content = get_url_content(url)
        soup = BeautifulSoup(content, "html.parser")
        for a in soup.find_all('a', href=True):
            if "http://itikawa.com/bgrPHP/bg.php?" in a['href']:
                print(str(count) + " - i:"+str(i)  + ") Found the URL:", a['href'])
                # every_game_log_link.append(a['href'])

                file_dl = get_url_content(a['href'])
                file_soup = BeautifulSoup(file_dl, "html.parser")
                for a2 in file_soup.find_all('a', href=True):
                    if "/kifdb/bg/bin/" in a2['href']:
                        print("Found the File:", a2['href'])
                        file_url = a2['href'].replace("../", "http://itikawa.com/")
                        r = requests.get(file_url, allow_redirects=True)
                        open("../protocol/gamefiles/" + str(file_count) + ".txt", 'wb').write(r.content)
                        file_count += 1
                count += 1
        i += 10
