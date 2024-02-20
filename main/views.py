from django.shortcuts import render, HttpResponse
from .handler import NewDocument

def index(response):
    return render(response, "index.html", {})

def aboutUs(response):
    return render(response, "aboutUs.html", {})

def generator(response):
    songLabels = ['Votum', 'Kata Pembuka', 'Pengakuan Dosa', 'Berita Anugerah', 'Persembahan', 'Pengutusan']
    context = {
        'songLabels': songLabels,
    }

    if response.method == 'POST':
        # Get all data
        data = {
            'date' : response.POST.get("date"),
            'theme' : response.POST.get("theme", ""),
            'pdt' : response.POST.get("pdt", ""),
            'pnt' : response.POST.get("pnt", ""),
            'verseFirman' : response.POST.get("verseFirman", ""),
            'verseKataPembuka' : response.POST.get("verseKataPembuka", ""),
            'verseBeritaAnugerah' : response.POST.get("verseBeritaAnugerah", ""),
            'versePersembahan' : response.POST.get("versePersembahan", ""),
            'pelayananPujian' : response.POST.get("pelayananPujian", "")
        }
            # Get the songs
                # Format:
                    # songBook = ['a', 'b', 'c']
                    # songBook_number = ['1', '2', '3']
                    # ...
                    # songTitle = ['x', 'y', 'z']
                    # songDict = {
                    #     'songZip': zip(songBook, songBook_number, ..., songTitle)
                    # }
        songBook = response.POST.getlist('songBook')
        songBook_number = response.POST.getlist('songBook_number')
        songBook_verse = response.POST.getlist('songBook_verse')
        songTitle = response.POST.getlist('songTitle')
        songLyrics = response.POST.getlist('songLyrics')

        songDict = {
            'songZip': zip(songLabels, songBook, songBook_number, songBook_verse, songTitle, songLyrics)
        }
        
        data.update(songDict)
        context.update(data)

        # Song Validation
        validate = True
        for book, lyrics in zip(songBook, songLyrics):
            if not book and not lyrics:
                validate = False
        
        if validate:
            # Make New Document
            NewDocument(data)

            fileName = f'Liturgi Remaja - {response.POST["date"]}.docx'

            # Send The Document to User
            with open('New_Liturgi.docx', 'rb') as document_file:
                doc = HttpResponse(document_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                doc['Content-Disposition'] = f'attachment; filename={fileName}'
                return doc
        else:
            return render(response, 'generator.html', context)

    return render(response, "generator.html", context)