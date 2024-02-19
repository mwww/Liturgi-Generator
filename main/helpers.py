from bs4 import BeautifulSoup
import requests
import os
import json
base_dir = 'D:\\Data Hansen\\Data Programming\\Projects\\Liturgi Generator\\src\\'
delimiter = '~*~'


""" GET LYRICS FROM WEB """
def GetLyricsWeb(songDict):
    # book, bookNumber, verseNumberList
    book = songDict['songBook']
    bookNumber = songDict['songBook_number']
    verseNumber = songDict['songBook_verse']
    verseNumberList = []
    temp = ''; temp2 = ''
    dashMode = False
    for c in verseNumber:
        if not dashMode and c not in ',-':
            temp += c
        if dashMode and c not in ',-':
            temp2 += c

        if c == ',':
            if not dashMode:
                verseNumberList.append(temp)
                temp = ''
            else:
                dashMode = False
                for i in range(int(temp), int(temp2)+1):
                    verseNumberList.append(str(i))
                temp = ''
        elif c == '-':
            dashMode = True
    if dashMode:
        for i in range(int(temp), int(temp2)+1):
            verseNumberList.append(str(i))
    else:
        verseNumberList.append(temp)

    url = f'https://alkitab.app/{book}/{bookNumber}'
    response = requests.get(url).text

    if 'no such song' in response:
        return ''
    else:
        doc = BeautifulSoup(response, "html.parser")
        
        # Get lyrics
        verseLyricsList = []
        for verseNumber in verseNumberList:
            verseLyricsList.append(getVerseWeb(doc, verseNumber))
        
        reffLyrics = ''
        if doc.find('div', class_='bait reff'):
            reffLyrics = getReffWeb(doc)

        # Return lyrics
        lyrics = ''
        # if reff exist
        if reffLyrics: 
            bait_tag = doc.find('div', class_='bait')
            classNameList = bait_tag['class']
            className = ' '.join(classNameList)

            # if reff is sung before verse
            if className == 'bait reff':
                lyrics += (f'Reff:\n{reffLyrics}')
                for index, verseLyrics in enumerate(verseLyricsList):
                    lyrics += (f'\n\n{verseNumberList[index]}. {verseLyrics}')
                    lyrics += ('\n(Kembali ke Reff)')
            # if reff is sung after verse
            else:
                for index, verseLyrics in enumerate(verseLyricsList):
                    if index == 0:
                        lyrics += (f'{verseNumberList[index]}. {verseLyrics}\n\n')
                        lyrics += (f'Reff:\n{reffLyrics}')
                    else:
                        lyrics += (f'\n\n{verseNumberList[index]}. {verseLyrics}')
        # if reff doesn't exist
        else:
            for index, verseLyrics in enumerate(verseLyricsList):
                if index != len(verseLyricsList)-1:
                    lyrics += (f'{verseNumberList[index]}. {verseLyrics}\n\n')
                else:
                    lyrics += (f'{verseNumberList[index]}. {verseLyrics}')

        return lyrics


def getVerseWeb(doc, verseNumber):
    bait_tag = doc.find_all('div', class_="bait")
    verseLyrics = ''
    for bait in bait_tag:
        bait_no_tag = bait.css.select('.bait-no')
        for bait_no in bait_no_tag:
            if bait_no.text == verseNumber:
                baris_tag = bait.css.select('.baris')
                for index, baris in enumerate(baris_tag):
                    if index != len(baris_tag)-1:
                        verseLyrics += f'{baris.text}\n'
                    else:
                        verseLyrics += baris.text
    return verseLyrics


def getReffWeb(doc):
    reff_lyrics = ''
    reff_tag = doc.find('div', class_="bait reff")
    baris_tag = reff_tag.css.select('.baris')
    for index, baris in enumerate(baris_tag):
        if index != len(baris_tag)-1:
            reff_lyrics += f'{baris.text}\n'
        else:
            reff_lyrics += baris.text
    return reff_lyrics


""" GET LYRICS FROM FILE """
def GetLyricsFile(songDict):
    book = songDict['songBook']
    bookNumber = songDict['songBook_number']
    verseNumber = songDict['songBook_verse']
    # Convert verseNumber text into a list of verseNumber
    verseNumberList = []
    temp = ''; temp2 = ''
    dashMode = False
    for c in verseNumber:
        if not dashMode and c not in ',-':
            temp += c
        if dashMode and c not in ',-':
            temp2 += c

        if c == ',':
            if not dashMode:
                verseNumberList.append(temp)
                temp = ''
            else:
                dashMode = False
                for i in range(int(temp), int(temp2)+1):
                    verseNumberList.append(str(i))
                temp = ''
        elif c == '-':
            dashMode = True
    if dashMode:
        for i in range(int(temp), int(temp2)+1):
            verseNumberList.append(str(i))
    else:
        verseNumberList.append(temp)

    # Search for the file
    dir = os.path.join(base_dir, 'song book', str.upper(book))
    os.chdir(dir)
    try:
        f = open(f'{bookNumber}.txt', 'r')
        lyrics = ''
        
        # Read verses
        verseDict = getVerseFile(f, verseNumberList) #key:value = verseNum:verseLyrics

        # Read reff
        f.seek(0)
        reffExist = 'Reff:\n' in f.readlines()
        reffLyrics = ''
        if reffExist:
            reffLyrics = getReffFile(f)
        
        # Read title
        title = getTitleFile(f)

        # Make full lyrics
        if reffExist:
            f.seek(0)
            line = f.readline()
            while delimiter not in line:
                line = f.readline()
            if 'Reff:' in f.readline():
                lyrics += (reffLyrics)
                for verse in verseNumberList:
                    if verseDict[verse]:
                        lyrics += (f'\n\n{verseDict[verse]}'
                                    '\n(Kembali ke Reff)')
            else:
                for index, verse in enumerate(verseNumberList):
                    if verseDict[verse]:
                        if index == 0:
                            lyrics += (f'{verseDict[verse]}\n\n'
                                f'{reffLyrics}')
                        else:
                            lyrics += (f'\n\n{verseDict[verse]}')
        else:
            for index, verse in enumerate(verseNumberList):
                if verseDict[verse]:
                    if index == 0:
                        lyrics += (f'{verseDict[verse]}')
                    else:
                        lyrics += (f'\n\n{verseDict[verse]}')
        
        return lyrics
    except:
        return 'Lirik lagu tidak ditemukan'


def getVerseFile(f, verseNumberList):
    verseDict = {} #key:value = verseNum:verseLyrics

    f.seek(0)
    line = f.readline()
    for verse in verseNumberList:
        verseLyrics = ''
        while f'{verse}.' not in line:
            line = f.readline()
            if line == '':
                break
        if line != '':
            while delimiter not in line:
                verseLyrics += line
                line = f.readline()

        verseLyrics = verseLyrics[:-1]

        verseDict[verse] = verseLyrics
    return verseDict


def getReffFile(f):
    reffLyrics = ''

    f.seek(0)
    line = f.readline()
    while 'Reff:' not in line:
        line = f.readline()

    while delimiter not in line:
        reffLyrics += line
        line = f.readline()

    reffLyrics = reffLyrics[:-1]

    return reffLyrics

def getTitleFile(f):
    f.seek(0)
    title = f.readline()[:-1]
    return title


""" GET VERSE """
def GetVerse(text):
    os.chdir(base_dir)
    with open('passageList.json') as f:
        passageList = json.load(f)['data']

    # Convert text into book, chapter, and verse
    book = ''
    chapter = ''
    verse = ''

    spaceCountLimit = 0
    if text[0].isnumeric():     #if chapter begins with a number
        spaceCountLimit = 2
    else:                       #if chapter begins with a letter
        spaceCountLimit = 1

    index = 0
    spaceCount = 0
    while spaceCount < spaceCountLimit: #add to book
        book += text[index]
        index += 1

        if text[index] == ' ':
            spaceCount += 1
    index += 1

    while text[index] != ':': #add to chapter
        chapter += text[index]
        index += 1
    index += 1

    while index != len(text): #add to verse
        verse += text[index]
        index += 1

    try:
        url = f'https://beeble.vercel.app/api/v1/passage/{book}/{chapter}?ver=tb'
        response = requests.get(url).text
        data = json.loads(response)['data']

        # Check if chapter exist in the book
        bookNum = data['book']['no']
        maxLimit = passageList[bookNum-1]['chapter']
        if int(chapter) <= maxLimit:
            # Convert verse text into verse list
            verseList = []
            temp = ''; temp2 = ''
            dashMode = False
            for c in verse:
                if not dashMode and c not in ',-':
                    temp += c
                if dashMode and c not in ',-':
                    temp2 += c

                if c == ',':
                    if not dashMode:
                        verseList.append(temp)
                        temp = ''
                    else:
                        dashMode = False
                        for i in range(int(temp), int(temp2)+1):
                            verseList.append(str(i))
                        temp = ''
                elif c == '-':
                    dashMode = True
            if dashMode:
                for i in range(int(temp), int(temp2)+1):
                    verseList.append(str(i))
            else:
                verseList.append(temp)

            # Get verse
            """ METHOD 2 """
            content = ''
            verses = data['verses']
            verseListIndex = 0; versesIndex = 0
            count = 0
            while verseListIndex < len(verseList):
                versesIndex = int(verseList[verseListIndex]) - 1 + count
                if str(verses[versesIndex]['verse']) == verseList[verseListIndex]:
                    content += f'{verses[versesIndex]['content']} '
                    verseListIndex += 1
                    count = 0
                else:
                    count += 1
            content = content[:-1]

            # Check whether content is empty
            if content:
                return content
            else:
                return 'Ayat tidak ditemukan'
        else:
            return 'Ayat tidak ditemukan'
    except:
        return 'Ayat tidak ditemukan'