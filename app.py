from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
from datetime import date

from db import get_db_connection
from tournament import *
from player import *
from pokemon import *
from match import *
from set import *
from user import *

app = Flask(__name__)

app.secret_key = "randomkey"
type_api = pokeAPIAllTypes()

#----------USER FUNCTIONS---------------------------------------------------------#
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/user', methods=["GET", "POST"])
def user():
    username = request.form.get("u_username")
    password = request.form.get("u_password")

    if "newuser" in request.form:
        user = newUser(username, password)
        session["user"] = user
        return redirect(url_for("tournamentlist"))

    elif "userlogin" in request.form:
        validation, selecteduser = selectUser(username, password)
        session["user"] = selecteduser

        if validation[0] is True:
            return redirect(url_for("tournamentlist"))

    return render_template("index.html")

#----------TOURNAMENT FUNCTIONS---------------------------------------------------------#
@app.route('/tournamentlist', methods=["GET", "POST"])
def tournamentlist():
    tournament_results = getTournamentList()
    return render_template("tournamentlist.html", tournament_results=tournament_results, user = session["user"])

@app.route('/tournament/<int:t_tourneyid>', methods=["GET", "POST"])
def tournament(t_tourneyid):
    selectedTournament = selectTournament(t_tourneyid)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
            SELECT po_pokeid, po_name, po_isteracaptain, pl_name, po_tier, COALESCE(SUM(ps_k),0) AS po_k, COALESCE(SUM(ps_d),0) AS po_d,
            COALESCE(MAX(ps_streak),0) FROM \"Pokemon\" JOIN \"Player\" ON pl_playerid = po_playerid LEFT JOIN \"PokemonSet\" ON po_pokeid = ps_pokeid
            WHERE (po_tourneyID = %s) GROUP BY po_pokeid, pl_name ORDER BY po_k DESC LIMIT 10;
            """, (t_tourneyid,))
    session["killrankings"] = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("tournament.html", tournament = selectedTournament, rankings = session["killrankings"], user = session["user"])

@app.route("/newtournament", methods=["GET","POST"])
def newtournament():
    if request.method == "POST":
        name = request.form.get("t_name")
        tformat = request.form.get("t_format")
        playercount = request.form.get("t_playercount")
        newTournament(name, tformat, playercount)
        return redirect(url_for("tournamentlist"))

    return render_template("newtournament.html")

@app.route("/edittournament/  <int:t_tourneyid>", methods=["GET","POST"])
def edittournament(t_tourneyid):
    if "edittournament" in request.form:
        name = request.form.get("t_name")
        tformat = request.form.get("t_format")
        playercount = request.form.get("t_playercount")
        updateTournament(t_tourneyid, name, tformat, playercount)
        return redirect(url_for("tournament", t_tourneyid=t_tourneyid))

    elif "deletetournament" in request.form:
        deleteTournament(t_tourneyid)
        tournamentresults = getTournamentList()
        return render_template("index.html", tournament_results = tournamentresults)

    return redirect(url_for("tournament", t_tourneyid = t_tourneyid))

#----------------------PLAYER FUNCTIONS-------------------------------------------#
@app.route('/players/ <int:pl_tourneyid>', methods=["GET", "POST"])
def players(pl_tourneyid):
    player_results = getPlayerList(pl_tourneyid)
    return render_template("players.html", player_results = player_results, tourneyid = pl_tourneyid, user = session["user"])

@app.route('/playerdetails/ <int:pl_tourneyid>/ <int:pl_playerid>', methods=["GET", "POST"])
def playerdetails(pl_tourneyid, pl_playerid):
    selectedplayer = selectPlayer(pl_tourneyid, pl_playerid)
    pokemonteam = pokemonTeamFromPlayer(pl_tourneyid, pl_playerid)
    return render_template("playerdetails.html", selectedplayer = selectedplayer, pokemonteam = pokemonteam
                           ,tourneyid = pl_tourneyid, playerid = pl_playerid, user = session["user"])

@app.route("/newplayer/ <int:pl_tourneyid>", methods=["GET","POST"])
def newplayer(pl_tourneyid):
    name = request.form.get("pl_name")
    constraint = request.form.get("pl_type")
    url = request.form.get("pl_pokepaste")

    pl_playerid = newPlayer(pl_tourneyid, name, constraint, url)
    playerTeam = pokepasteParser(url)

    for pokemon in playerTeam:
        pokemon_api = pokeAPICall(pokemon["name"].strip())
        type1 = pokemon_api["types"][0]
        if len(pokemon_api["types"]) > 1:
            type2 = pokemon_api["types"][1]
        else:
            type2 = "N/A"
        newPokemon(pl_tourneyid, pl_playerid, pokemon, type1, type2)

    return redirect(url_for("players", pl_tourneyid = pl_tourneyid))

@app.route("/editplayer/  <int:pl_tourneyid>/ <int:pl_playerid>", methods=["GET","POST"])
def editplayer(pl_tourneyid, pl_playerid):
    if "editplayer" in request.form:
        name = request.form.get("pl_name")
        url = request.form.get("pl_pokepaste")
        editPlayer(pl_tourneyid, pl_playerid, name, url)

        if url is not None:
            playerTeam = pokepasteParser(url)

            for pokemon in playerTeam:
                selectedpokemonid = selectPokemonByName(pl_tourneyid, pokemon["name"].strip(), pl_playerid)

                pokemon_api = pokeAPICall(pokemon["name"].strip())
                type1 = pokemon_api["types"][0]
                if len(pokemon_api["types"]) > 1:
                    type2 = pokemon_api["types"][1]
                else:
                    type2 = "N/A"

                if selectedpokemonid is not None:
                    selectedpokemonid = selectedpokemonid[0]
                    editPokemonfromPaste(pl_tourneyid, selectedpokemonid, pokemon, type1, type2)
                else:
                    newPokemon(pl_tourneyid, pl_playerid, pokemon, type1, type2)

        return redirect(url_for("playerdetails", pl_tourneyid = pl_tourneyid, pl_playerid = pl_playerid))

    elif "deleteplayer" in request.form:
        deletePlayer(pl_tourneyid, pl_playerid)
        player_results = getPlayerList(pl_tourneyid)
        return render_template("players.html", player_results = player_results, tourneyid = pl_tourneyid, user = session["user"])

    return redirect(url_for("playerdetails", pl_tourneyid=pl_tourneyid, pl_playerid=pl_playerid))

#-----------------------POKEMON FUNCTIONS-----------------------------------#
@app.route('/pokemon/ <int:po_tourneyid>', methods=["GET", "POST"])
def pokemon(po_tourneyid):
    if "reset_poke" in request.form:
        poke_results = getPokemonList(po_tourneyid)

    elif "pokemon" in request.form:
        keyword = request.form.get("pokemon")
        tier = request.form.get("tier")
        type = request.form.get("type")
        tera = request.form.get("tera")
        poke_results = pokemonFilter(po_tourneyid, keyword, tier, type, tera)

    else:
        poke_results = getPokemonList(po_tourneyid)

    return render_template('pokemon.html', poke_results = poke_results, type_api = type_api, tourneyid = po_tourneyid, user = session["user"])

@app.route('/pokemondetails/ <int:pl_tourneyid>/ <int:po_pokeid>', methods=["GET", "POST"])
def pokemondetails(pl_tourneyid, po_pokeid):
    selectedpokemon, best_sets = selectPokemon(pl_tourneyid, po_pokeid)
    po_name = selectedpokemon[1].strip()
    pokemon_api = pokeAPICall(po_name)
    nature_map = natureMapping(selectedpokemon[18])
    selectedStats = statCalculation(selectedpokemon[21], selectedpokemon[22], pokemon_api, nature_map)
    return render_template("pokemondetails.html", selectedpokemon = selectedpokemon, best_sets = best_sets, tourneyid = pl_tourneyid, po_pokeid = po_pokeid,
                           pokemon_api = pokemon_api, type_api = type_api, selectedStats = selectedStats, nature_map = nature_map, user = session["user"])

@app.route("/editpokemon/  <int:po_tourneyid>/ <int:po_pokeid>", methods=["GET","POST"])
def editpokemon(po_tourneyid, po_pokeid):
    if "editpokemon" in request.form:
        name = request.form.get("p_name")
        editPokemon(po_tourneyid, po_pokeid, name)
        return redirect(url_for("pokemondetails", pl_tourneyid = po_tourneyid, po_pokeid = po_pokeid))

    elif "deletepokemon" in request.form:
        deletePokemon(po_tourneyid, po_pokeid)
        return redirect(url_for("pokemon", po_tourneyid = po_tourneyid))

    return redirect(url_for("pokemondetails", pl_tourneyid = po_tourneyid, po_pokeid = po_pokeid))

@app.route("/pokemontoplayer <int:po_tourneyid>/ <po_playername>", methods=["GET","POST"])
def pokemontoplayer(po_tourneyid, po_playername):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM \"Player\" WHERE (pl_tourneyid = %s AND pl_name = %s);", (po_tourneyid,po_playername,))
    selectedplayer = cursor.fetchone()
    cursor.close()
    conn.close()

    return redirect(url_for("playerdetails", pl_tourneyid = po_tourneyid, pl_playerid = selectedplayer[0]))

#----------------MATCH FUNCTIONS-----------------------------------#
@app.route("/matches <int:m_tourneyid>", methods=["GET","POST"])
def matches(m_tourneyid):
    if "reset_match" in request.form:
        match_results = getMatchList(m_tourneyid)
    elif "match" in request.form:
        keyword = request.form.get("match")
        match_results = matchFilter(m_tourneyid, keyword)
    else:
        match_results = getMatchList(m_tourneyid)

    playerlist = getPlayerList(m_tourneyid)
    return render_template("match.html", match_results = match_results, playerlist = playerlist, tourneyid = m_tourneyid, user = session["user"])

@app.route("/newmatch <int:m_tourneyid>", methods=["GET","POST"])
def newmatch(m_tourneyid):
    name = request.form.get("m_name")
    player1 = request.form.get("m_player1")
    player1id = selectPlayerByName(m_tourneyid, player1)

    player2 = request.form.get("m_player2")
    player2id = selectPlayerByName(m_tourneyid, player2)

    newMatch(m_tourneyid, name, player1id, player2id)
    return redirect(url_for("matches", m_tourneyid = m_tourneyid))

@app.route("/matchdetails <int:m_matchid>/ <int:m_tourneyid>", methods=["POST","GET"])
def matchdetails(m_matchid, m_tourneyid):
    selectedmatch = selectMatch(m_matchid, m_tourneyid)
    set_list, setwins = getSetList(m_matchid)
    return render_template("matchdetails.html", matchid = m_matchid, set_list = set_list, setwins = setwins, selectedmatch = selectedmatch
                           , tourneyid = m_tourneyid, todayDate = date.today().isoformat(), user = session["user"])

#---------------SET FUNCTIONS----------------------------------------------------#
@app.route("/get_player_pokemon/<int:tourneyid>/<playername>")
def get_player_pokemon(tourneyid, playername):
    playerid = selectPlayerByName(tourneyid, playername)
    pokemonteam = pokemonTeamFromPlayer(tourneyid, playerid)
    pokemon_names = [row[1] for row in pokemonteam]

    return jsonify(pokemon_names)

@app.route("/newset <int:m_tourneyid>/ <int:s_matchid>/ <int:player1id>/ <int:player2id>", methods=["GET","POST"])
def newset(m_tourneyid, s_matchid, player1id, player2id):
    setNumber = request.form.get("m_setnum")

    p1mons = request.form.getlist("m_player1_name[]")
    p1kills = request.form.getlist("m_player1kills[]")
    p1deaths = request.form.getlist("m_player1deaths[]")
    p1streak= request.form.getlist("m_player1streak[]")
    p1tera = request.form.get("m_player1tera", type = int)
    p1teratypes = request.form.get("m_player1_tera_type")
    p1points = request.form.get("m_player1_points", type = int)

    p2mons = request.form.getlist("m_player2_name[]")
    p2kills = request.form.getlist("m_player2kills[]")
    p2deaths = request.form.getlist("m_player2deaths[]")
    p2streak = request.form.getlist("m_player2streak[]")
    p2tera = request.form.get("m_player2tera", type = int)
    p2teratypes = request.form.get("m_player2_tera_type")
    p2points = request.form.get("m_player2_points", type = int)

    link = request.form.get("m_link")
    date = request.form.get("m_date")

    if p1points > p2points:
        winid = player1id
        setpoints = p1points
    else:
        winid = player2id
        setpoints = p2points

    setid = newSet(s_matchid, player1id, player2id, winid, link, date, setpoints, setNumber)

    p1roster = []
    for i in range(len(p1mons)):
        if p1mons[i] != "":
            print(p1mons[i])
            is_tera = (p1tera == i + 1)
            pokemonid = selectPokemonByName(m_tourneyid, p1mons[i].strip(), player1id)
            print(pokemonid)
            p1roster.append({
                "id": pokemonid,
                "kills": p1kills[i],
                "deaths": p1deaths[i],
                "streak": p1streak[i],
                "tera": p1teratypes if is_tera else None
            })
    registerPokemonInSet(setid, p1roster, player1id)

    p2roster = []
    for i in range(len(p2mons)):
       if p2mons[i] != "":
           is_tera = (p2tera == i + 1)
           pokmonid = selectPokemonByName(m_tourneyid, p2mons[i].strip(), player2id)
           p2roster.append({
               "id": pokmonid,
               "kills": p2kills[i],
               "deaths": p2deaths[i],
               "streak": p2streak[i],
               "tera": p2teratypes if is_tera else None
           })
    registerPokemonInSet(setid, p2roster, player2id)

    return redirect(url_for("matchdetails", m_matchid = s_matchid, m_tourneyid = m_tourneyid))

if __name__ == "__main__":
    app.run(debug=True)