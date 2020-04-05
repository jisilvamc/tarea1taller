from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from requests import get

heroku = "http://127.0.0.1:8000/"


class Lista:
    def __init__(self, tipo, id, *args):
        if tipo == "episode":
            self.url = heroku + "episodio/" + str(id)
        elif tipo == "character":
            self.url = heroku + "personaje/" + str(id)
        elif tipo == "location":
            self.url = heroku + "lugar/" + str(id)
        self.texto = paragraph(*args)


api = 'https://rickandmortyapi.com/api/'
cha, loc, epi = api + 'character', api + 'location', api + 'episode'


def paragraph(*args):
    ans = str(args[0])
    if len(args) > 1:
        for a in args[1:]:
            ans += ", " + str(a)
    return ans


def index(request):
    iterador = get(epi).json()
    episodes = iterador["results"]
    while iterador["info"]["next"]:
        iterador = get(iterador["info"]["next"]).json()
        episodes.extend(iterador["results"])
    answer = []
    for e in episodes:
        answer.append(Lista("episode", e["id"], e["name"], e["air_date"], e["episode"]))
    context = {'answer': answer}
    return render(request, 'polls/index.html', context)


def episodio(request, epi_id):
    e = get(epi + "/" + epi_id).json()
    texto = [e["name"], e["air_date"], e["episode"]]
    ids = [int(c.split("/")[-1]) for c in e["characters"]]
    answer = []
    answer.extend([Lista("character", c["id"], c["name"]) for c in get(cha + "/" + str(ids)).json()])
    if len(ids) > 20:
        while len(ids) > 20:
            ids = ids[20:]
            answer.extend([Lista("character", c["id"], c["name"]) for c in get(cha + "/" + str(ids)).json()])
    context = {'texto': texto, 'answer': answer}
    return render(request, 'polls/episodio.html', context)


def personaje(request, char_id):
    c = get(cha + "/" + char_id).json()
    texto = [c["name"], c["status"], c["species"], c["type"], c["gender"],
             c["location"]["name"], heroku + "lugar/" + c["location"]["url"].split("/")[-1]]
    origen_nombre = c["origin"]["name"]
    origen_url = heroku + "lugar/" + c["origin"]["url"].split("/")[-1]
    foto = c["image"]
    ids = [int(e.split("/")[-1]) for e in c["episode"]]
    episodes = [[e["id"], e["name"]] for e in get(epi + "/" + str(ids)).json()]
    if len(ids) > 20:
        while len(ids) > 20:
            ids = ids[20:]
            episodes.extend([[e["id"], e["name"]] for e in get(epi + "/" + str(ids)).json()])
    answer = []
    for e in episodes:
        answer.append(Lista("episode", e[0], e[1]))
    context = {'texto': texto, 'answer': answer, 'origen': origen_nombre, 'origen_url': origen_url, 'foto': foto}
    return render(request, 'polls/personaje.html', context)


def lugar(request, loc_id):  # CAMBIAR ordenar
    l = get(loc + "/" + loc_id).json()
    texto = [l["name"], l["type"], l["dimension"]]
    iterador = get(cha).json()
    characters = [[i["id"], i["name"]] for i in iterador["results"] if i["origin"]["name"] == l["name"]]
    while iterador["info"]["next"]:
        iterador = get(iterador["info"]["next"]).json()
        characters.extend([[i["id"], i["name"]] for i in iterador["results"] if i["origin"]["name"] == l["name"]])
    answer = []
    for c in characters:
        answer.append(Lista("character", c[0], c[1]))
    context = {'texto': texto, 'answer': answer}
    return render(request, 'polls/lugar.html', context)


def busqueda(request, bus):
    bus = bus.replace("+", " ")
    # buscar episodio
    iterador = get(epi, params={"name": bus}).json()
    if "error" not in iterador.keys():
        episodes = [[heroku + "episodio/" + i["url"].split("/")[-1], i["name"]] for i in iterador["results"]]
        if iterador["info"]["pages"] > 1:
            iterador = get(iterador["info"]["next"]).json()
            episodes.extend([[heroku + "episodio/" + i["url"].split("/")[-1], i["name"]] for i in iterador["results"]])
    else:
        episodes = ""
    context = {"episodios": episodes}
    # buscar personaje
    iterador = get(cha, params={"name": bus}).json()
    if "error" not in iterador.keys():
        personajes = [[heroku + "personaje/" + i["url"].split("/")[-1], i["name"]] for i in iterador["results"]]
        if iterador["info"]["pages"] > 1:
            iterador = get(iterador["info"]["next"]).json()
            personajes.extend([[heroku + "personaje/" + i["url"].split("/")[-1], i["name"]] for i in iterador["results"]])
    else:
        personajes = ""
    context["personajes"] = personajes
    # buscar lugar
    iterador = get(loc, params={"name": bus}).json()
    if "error" not in iterador.keys():
        lugares = [[heroku + "lugar/" + i["url"].split("/")[-1], i["name"]] for i in iterador["results"]]
        if iterador["info"]["pages"] > 1:
            iterador = get(iterador["info"]["next"]).json()
            lugares.extend([[heroku + "lugar/" + i["url"].split("/")[-1], i["name"]] for i in iterador["results"]])
    else:
        lugares = ""
    context["lugares"] = lugares
    return render(request, 'polls/busqueda.html', context)
