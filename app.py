from flask import Flask, render_template, request, session, redirect, url_for
import requests

from db import get_db_connection
from tournament import *
from player import *
from pokemon import *

app = Flask(__name__)

app.secret_key = "randomkey"

@app.route('/tournament/<int:t_tourneyid>', methods=["GET", "POST"])
def tournament(t_tourneyid):
    selectedTournament = selectTournament(t_tourneyid)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Pokemon WHERE (po_tourneyID = %s) ORDER BY po_k DESC LIMIT 10;", (t_tourneyid,))
    session["killrankings"] = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("tournament.html", tournament = selectedTournament, rankings = session["killrankings"])

@app.route('/players/ <int:pl_tourneyid>', methods=["GET", "POST"])
def players(pl_tourneyid):
    player_results = getPlayerList(pl_tourneyid)
    return render_template("players.html", player_results = player_results, tourneyid = pl_tourneyid)

@app.route('/playerdetails/ <int:pl_tourneyid>/ <int:pl_playerid>', methods=["GET", "POST"])
def playerdetails(pl_tourneyid, pl_playerid):
    selectedplayer, playername = selectPlayer(pl_tourneyid, pl_playerid)
    pokemonteam = pokemonTeamFromPlayer(pl_tourneyid, playername)
    return render_template("playerdetails.html", selectedplayer = selectedplayer, pokemonteam = pokemonteam
                           ,tourneyid = pl_tourneyid, playerid = pl_playerid)

@app.route('/pokemondetails/ <int:pl_tourneyid>/ <int:po_pokeid>', methods=["GET", "POST"])
def pokemondetails(pl_tourneyid, po_pokeid):
    selectedpokemon = selectPokemon(pl_tourneyid, po_pokeid)
    po_name = selectedpokemon[3].strip().lower()
    pokemon_api = pokeAPICall(po_name)
    return render_template("pokemondetails.html", selectedpokemon = selectedpokemon, tourneyid = pl_tourneyid, po_pokeid = po_pokeid,
                           pokemon_api = pokemon_api)

@app.route('/pokemon/ <int:po_tourneyid>', methods=["GET", "POST"])
def pokemon(po_tourneyid):
    if "reset_poke" in request.form:
        session["poke_results"] = getPokemonList(po_tourneyid)

    elif "pokemon" in request.form:
        keyword = request.form.get("pokemon")
        tier = request.form.get("tier")
        type = request.form.get("type")
        session["poke_results"] = pokemonFilter(po_tourneyid, keyword, tier, type)

    else:
        session["poke_results"] = getPokemonList(po_tourneyid)

    return render_template('pokemon.html', poke_results = session["poke_results"], tourneyid = po_tourneyid)

@app.route("/newtournament", methods=["GET","POST"])
def newtournament():
    if request.method == "POST":
        name = request.form.get("t_name")
        tformat = request.form.get("t_format")
        newTournament(name, tformat)
        return redirect(url_for("index"))

    return render_template("newtournament.html")

@app.route("/newplayer/ <int:pl_tourneyid>", methods=["GET","POST"])
def newplayer(pl_tourneyid):
    name = request.form.get("pl_name")
    constraint = request.form.get("pl_type")
    url = request.form.get("pl_pokepaste")

    newPlayer(pl_tourneyid, name, constraint, url)
    playerTeam = pokepasteParser(url)

    for pokemon in playerTeam:
        newPokemon(pl_tourneyid, name, pokemon)

    return redirect(url_for("players", pl_tourneyid = pl_tourneyid))

@app.route("/edittournament/  <int:t_tourneyid>", methods=["GET","POST"])
def edittournament(t_tourneyid):
    if "edittournament" in request.form:
        name = request.form.get("t_name")
        tformat = request.form.get("t_format")
        updateTournament(t_tourneyid, name, tformat)
        return redirect(url_for("tournament", t_tourneyid=t_tourneyid))

    elif "deletetournament" in request.form:
        deleteTournament(t_tourneyid)
        tournamentresults = getTournamentList()
        return render_template("index.html", tournament_results = tournamentresults)

    return redirect(url_for("tournament", t_tourneyid = t_tourneyid))

@app.route("/editpokemon/  <int:po_tourneyid>/ <int:po_pokeid>", methods=["GET","POST"])
def editpokemon(po_tourneyid, po_pokeid):
    if "editpokemon" in request.form:
        name = request.form.get("p_name")
        editPokemon(po_tourneyid, po_pokeid, name)
        return redirect(url_for("pokemondetails", pl_tourneyid = po_tourneyid, po_pokeid = po_pokeid))

    elif "deletepokemon" in request.form:
        #ADD DELETE FUNCTION LATER
        poke_results = getPokemonList(po_tourneyid)
        return render_template('pokemon.html', poke_results = poke_results, tourneyid = po_tourneyid)

    return redirect(url_for("pokemondetails", pl_tourneyid = po_tourneyid, po_pokeid = po_pokeid))

@app.route("/editplayer/  <int:pl_tourneyid>/ <int:pl_playerid>", methods=["GET","POST"])
def editplayer(pl_tourneyid, pl_playerid):
    if "editplayer" in request.form:
        name = request.form.get("pl_name")
        url = request.form.get("pl_pokepaste")
        editPlayer(pl_tourneyid, pl_playerid, name)

        if url is not None:
            playerTeam = pokepasteParser(url)

            for pokemon in playerTeam:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT po_pokeid FROM Pokemon WHERE (po_tourneyid = %s AND po_name = %s AND po_playername = %s);", (pl_tourneyid, pokemon["name"].strip(), name,))
                selectedpokemonid = cursor.fetchone()
                cursor.close()
                conn.close()

                if selectedpokemonid is not None:
                    selectedpokemonid = selectedpokemonid[0]
                    editPokemonfromPaste(pl_tourneyid, selectedpokemonid, pokemon)

        return redirect(url_for("playerdetails", pl_tourneyid = pl_tourneyid, pl_playerid = pl_playerid))

    elif "deleteplayer" in request.form:
        deletePlayer(pl_tourneyid, pl_playerid)
        player_results = getPlayerList(pl_tourneyid)
        return render_template("players.html", player_results = player_results, tourneyid = pl_tourneyid)

    return redirect(url_for("playerdetails", pl_tourneyid=pl_tourneyid, pl_playerid=pl_playerid))

@app.route("/pokemontoplayer <int:po_tourneyid>/ <po_playername>", methods=["GET","POST"])
def pokemontoplayer(po_tourneyid, po_playername):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Player WHERE (pl_tourneyid = %s AND pl_name = %s);", (po_tourneyid,po_playername,))
    selectedplayer = cursor.fetchone()
    cursor.close()
    conn.close()

    return redirect(url_for("playerdetails", pl_tourneyid = po_tourneyid, pl_playerid = selectedplayer[0]))

@app.route("/", methods=["GET"])
def index():
    tournamentresults = getTournamentList()
    return render_template("index.html", tournament_results = tournamentresults )

if __name__ == "__main__":
    app.run(debug=True)