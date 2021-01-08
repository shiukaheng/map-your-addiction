from bs4 import BeautifulSoup

#def extractHistoryFromTakeout(takeoutPath, newHistoryPath="./watch-history.html"):
#    return

#Parsing takeout
def parse_history_file(path):
    historyDictList = {}

    with open(path, "r", encoding="utf-8") as history:

        contents = history.read()

        soup = BeautifulSoup(contents, 'lxml')

        for index, text in enumerate(soup.find_all('div', class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")):

            vid_str = text.get_text(separator=",").split(' ',1)[1].split(',')

            # Videos missing any attributes are not indexed
            if len(vid_str) == 5:
                videoDict = {'title': vid_str[0],
                             'channel': vid_str[1],
                             'month_day': vid_str[2],
                             'year': vid_str[3],
                             'access_date': vid_str[4]}

                for link in text.find_all('a'):
                    if text.index(link) == 1:
                        name = 'vid_url'
                        videoDict['vid_id'] = link.get('href').split('=')[1]
                    else:
                        name = 'channel_url'

                    videoDict[name] = link.get('href')

                historyDictList[index] = videoDict

        return historyDictList


def parse_history_file_altered(path):
    history_list = []
    with open(path, "r", encoding="utf-8") as history:
        contents = history.read()
        soup = BeautifulSoup(contents, 'lxml')
        for div in soup.find_all('div', class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1"):
            subelems = div.find_all(recursive=False)
            text = div.find_all(text=True, recursive=False)
            if len(subelems) == 4 and len(text) == 2:
                video_dict = {'video_title': subelems[0].get_text(),
                                'video_id': subelems[0].get('href')[32:],
                                'channel_title': subelems[2].get_text(),
                                'channel_id': subelems[2].get('href')[32:],
                                'access_time': str(text[1].encode('utf-8'))}
            else:
                continue
            history_list.append(video_dict)
    return history_list


#def saveHistoryCSV(historyDictList, outputPath):
#    return

#def readHistoryCSV(path):
#    return historyDictList

#=======
#def extractHistoryFromTakeout(takeoutPath, newHistoryPath="./watch-history.html"):
#    return

#def parseHistoryFile(path):
#    historyDictList = "penis"
#    return historyDictList
#>>>>>>> parent of f79fad8... hehehe

#def saveHistoryCSV(historyDictList, outputPath):
#    return

#def readHistoryCSV(path):
#    return historyDictList


