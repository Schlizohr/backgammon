import requests

every_game_log_link = []


# gibt html code der gewünschten url zurück
def get_url_content(url):
    return requests.get(url).text


if __name__ == '__main__':
    i = 0
    while i < 1000:
        url = 'http://itikawa.com/kifdb/herodb.cgi?table=bg&view=M&sort=1&order=D&recpoint=' + str(i)

        content = get_url_content(url)
        # übergebe html an beautifulsoup parser
        soup = BeautifulSoup(content, "html.parser")
        for post in soup.findAll('div', {'class': 'blog-post'}):
            print(post.find('h2'))

        i += 10
