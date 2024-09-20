from django.shortcuts import render

from musicbeats.models import Song, Playlist, History, Channel
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.db.models import Case, When
from .forms import SearchForm


def history(request):
    if request.method == "POST":
        user = request.user
        music_id = request.POST['music_id']
        history = History(user=user, music_id=music_id)
        history.save()

        return redirect(f"/songs/{music_id}")

    history = History.objects.filter(user=request.user)
    ids = []
    for i in history:
        ids.append(i.music_id)

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, 'musicbeats/history.html', {"history": song})


def playlist(request):
    if request.method == "POST":
        user = request.user
        video_id = request.POST['video_id']

        play = Playlist.objects.filter(user=user)

        for i in play:
            if video_id == i.video_id:
                message = "Your Song is Already Added"
                break
        else:
            playlist = Playlist(user=user, video_id=video_id)
            playlist.save()
            message = "Your Song is Succesfully Added"

        song = Song.objects.filter(song_id=video_id).first()
        return render(request, f"musicbeats/songpost.html", {'song': song, "message": message})

    wl = Playlist.objects.filter(user=request.user)
    ids = []
    for i in wl:
        ids.append(i.video_id)

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, "musicbeats/Playlist.html", {'song': song})


def songs(request):
    song = Song.objects.all()
    return render(request, 'musicbeats/songs.html', {'song': song})


def songpost(request, id):
    song = Song.objects.filter(song_id=id).first()
    return render(request, 'musicbeats/songpost.html', {'song': song})


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            message = 'Please fill in both fields.'
            return render(request, f'musicbeats/login.html', {"message": message})
        user = authenticate(username=username, password=password)
        if user is not None:
            from django.contrib.auth import login
            login(request, user)
            return redirect("/")
        else:
            message = 'Invalid username or password.'
            return render(request, f'musicbeats/login.html', {"message": message})
    return render(request, 'musicbeats/login.html')


def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if not email or not username or not first_name or not last_name or not pass1 or not pass2:
            message = "Error! Please, fill the forms correctly!"
            return render(request, f'musicbeats/signup.html', {"message": message})
        elif User.objects.filter(username=username).exists():
            message = "This account is already exists"
            return render(request, f'musicbeats/signup.html', {"message": message})
        elif pass1 != pass2:
            message = "Passwords don't match"
            return render(request, f'musicbeats/signup.html', {"message": message})

        else:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.first_name = first_name
            myuser.last_name = last_name
            myuser.save()
            user = authenticate(username=username, password=pass1)
            from django.contrib.auth import login
            login(request, user)

            channel = Channel(name=username)
            channel.save()

        return redirect('/')

    return render(request, 'musicbeats/signup.html')


def logout_user(request):
    logout(request)
    return redirect("/")


def channel(request, channel):
    chan = Channel.objects.filter(name=channel).first()
    video_ids = str(chan.music).split(" ")[1:]

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(video_ids)])
    song = Song.objects.filter(song_id__in=video_ids).order_by(preserved)

    return render(request, "musicbeats/channel.html", {"channel": chan, "song": song})


def upload(request):
    if request.method == "POST":
        name = request.POST['name']
        singer = request.POST['singer']
        tag = request.POST['tag']
        image = request.POST['image']
        credit = request.POST['credit']
        song1 = request.FILES['file']

        if not name or not singer or not tag or not image or not credit or not song1:
            message = "Error! Please, fill the forms correctly!"
            return render(request, f'musicbeats/upload.html', {"message": message})
        elif User.objects.filter(name=name,singer=singer).exists():
            message = "This song already exists"
            return render(request, f'musicbeats/upload.html', {"message": message})
        else:
            song_model = Song(name=name, singer=singer, tags=tag, image=image, credit=credit, song=song1)
            song_model.save()

            music_id = song_model.song_id
            channel_find = Channel.objects.filter(name=str(request.user))
            print(channel_find)

        for i in channel_find:
            i.music += f" {music_id}"
            i.save()
        return redirect("channel", request.user)

    return render(request, "musicbeats/upload.html")


def song_search(request):
    search_text = request.GET.get("search", "")
    print(search_text)
    form = SearchForm(request.GET)

    songs = set()

    if form.is_valid() and form.cleaned_data["search"]:
        search = form.cleaned_data["search"]
        search_in = form.cleaned_data.get("search_in") or "name"
        if search_in == "name":
            songs = Song.objects.filter(name__icontains=search)

        else:
            singers = Song.objects.filter(singer__icontains=search)

            for singer in singers:
                songs.add(singer)

    return render(request, "musicbeats/song-search.html", {"form": form, "search_text": search_text, "songs": songs})
