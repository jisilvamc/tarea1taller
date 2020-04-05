from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from requests import get


class Lista:
    def __init__(self, tipo, id, *args):
        if tipo == "episode":
            self.url = "http://127.0.0.1:8000/episodio/" + str(id)
        elif tipo == "character":
            self.url = "http://127.0.0.1:8000/personaje/" + str(id)
        elif tipo == "location":
            self.url = "http://127.0.0.1:8000/lugar/" + str(id)
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
             c["location"]["name"], "http://127.0.0.1:8000/lugar/" + c["location"]["url"].split("/")[-1]]
    origen_nombre = c["origin"]["name"]
    origen_url = "http://127.0.0.1:8000/lugar/" + c["origin"]["url"].split("/")[-1]
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
    nombre = "Earth"
    # buscar episodio
    ans = paragraph("Episodios: ")
    iterador = get(epi, params={"name": nombre}).json()
    if "error" not in iterador.keys():
        episodes = [e["name"] for e in iterador["results"]]
        if iterador["info"]["pages"] > 1:
            iterador = get(iterador["info"]["next"]).json()
            episodes.extend([i["name"] for i in iterador["results"]])
        for e in episodes:
            ans += paragraph(e)
    else:
        ans += paragraph("---")
    # buscar personaje
    ans += paragraph("Personajes: ")
    iterador = get(cha, params={"name": nombre}).json()
    if "error" not in iterador.keys():
        characters = [c["name"] for c in iterador["results"]]
        if iterador["info"]["pages"] > 1:
            iterador = get(iterador["info"]["next"]).json()
            characters.extend([c["name"] for c in iterador["results"]])
        for c in characters:
            ans += paragraph(c)
    else:
        ans += paragraph("---")
    # buscar lugar
    ans += paragraph("Lugares: ")
    iterador = get(loc, params={"name": nombre}).json()
    if "error" not in iterador.keys():
        locations = [l["name"] for l in iterador["results"]]
        if iterador["info"]["pages"] > 1:
            iterador = get(iterador["info"]["next"]).json()
            locations.extend([i["name"] for i in iterador["results"]])
        for l in locations:
            ans += paragraph(l)
    else:
        ans += paragraph("---")
    return HttpResponse(ans)
    # return render(request, 'polls/busqueda.html', context)
