from db import get_db_connection
import requests
import re
import pokepastes_scraper as pastes

def getPokemonList(po_tourneyid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT po_pokeid, po_name, pl_name,po_tier, po_isteracaptain, po_type1, po_type2 
        FROM Pokemon JOIN Player ON pl_playerid = po_playerid
        WHERE po_tourneyID = %s ORDER BY po_name ASC;""", (po_tourneyid,))
    poke_results = cursor.fetchall()

    cursor.close()
    conn.close()
    return poke_results

def newPokemon(po_tourneyid, po_playerid, pokemonData, type1, type2):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Pokemon(po_tourneyid, po_playerid, po_name, po_ability, po_item, po_nickname, po_move1, po_move2, po_move3, po_move4, po_nature, po_isShiny, po_type1, po_type2) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (po_tourneyid, po_playerid, pokemonData["name"], pokemonData["ability"], pokemonData["item"], pokemonData["nickname"],
              pokemonData["moves"][0], pokemonData["moves"][1], pokemonData["moves"][2], pokemonData["moves"][3], pokemonData["nature"], pokemonData["isShiny"],type1, type2))
    conn.commit()

    cursor.close()
    conn.close()

def selectPokemon(pl_tourneyid, po_pokeid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
            SELECT po_pokeid, po_name, pl_name, po_type1, po_type2, po_tier, po_isteracaptain, po_k, po_d, po_numbrought, po_winstreak, po_ability,
            po_item, po_nickname, po_move1, po_move2, po_move3, po_move4, po_nature, po_isshiny, pl_total_sets FROM Pokemon
            JOIN Player ON pl_playerid = po_playerid
            WHERE (po_tourneyID = %s and po_pokeid = %s);
            """, (pl_tourneyid,po_pokeid,))
    selectedpokemon = cursor.fetchone()
    cursor.close()
    conn.close()
    return selectedpokemon

def selectPokemonByName(po_tourneyid, po_name, po_playerid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT po_pokeid FROM Pokemon WHERE (po_tourneyid = %s AND po_name = %s AND po_playerid = %s);",
                   (po_tourneyid, po_name, po_playerid,))
    selectedpokemonid = cursor.fetchone()
    cursor.close()
    conn.close()
    return selectedpokemonid

def editPokemon(po_tourneyid, po_pokeid, name):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE Pokemon SET po_name = %s WHERE (po_tourneyid = %s AND po_pokeid = %s);",
                   (name, po_tourneyid, po_pokeid))

    conn.commit()
    cursor.close()
    conn.close()
    return

def editPokemonfromPaste(po_tourneyid, po_pokeid, pokemonData, type1, type2):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Pokemon SET po_name = %s, po_ability = %s, po_item = %s, po_nickname = %s, po_move1 = %s, po_move2 = %s, po_move3 = %s, po_move4 = %s,
        po_nature = %s, po_isShiny = %s, po_type1 = %s, po_type2 = %s WHERE (po_tourneyid = %s AND po_pokeid = %s);
        """, (pokemonData["name"], pokemonData["ability"], pokemonData["item"], pokemonData["nickname"],
        pokemonData["moves"][0], pokemonData["moves"][1], pokemonData["moves"][2], pokemonData["moves"][3], pokemonData["nature"],
           pokemonData["isShiny"], type1, type2, po_tourneyid, po_pokeid,))

    conn.commit()
    cursor.close()
    conn.close()
    return

def apiNameFix(api_name):
    if api_name.startswith("ogerpon") and not api_name.endswith("-mask"):
        api_name += "-mask"
    if api_name.startswith("aegislash") and not api_name.endswith("-shield"):
        api_name += "-shield"
    if api_name.startswith("mimikyu") and not api_name.endswith("-disguised"):
        api_name += "-disguised"
    if api_name.startswith("darmanitan") and not api_name.endswith("-standard"):
        api_name += "-standard"
    if api_name.startswith("indeedee") and not api_name.endswith("-f"):
        api_name += "-male"
    if (api_name.startswith("enamorus") or api_name.startswith("tornadus") or api_name.startswith("thundurus") or api_name.startswith("landorus")) and not api_name.endswith("-therian"):
        api_name += "-incarnate"
    if api_name.startswith("eiscue") and not api_name.endswith("-ice"):
        api_name += "-ice"
    if api_name.startswith("lycanroc") and not (api_name.endswith("-dusk") or api_name.endswith("-midnight")):
        api_name += "-midday"
    if api_name.startswith("tatsugiri") and not api_name.endswith("-curly"):
        api_name += "-curly"
    if api_name.startswith("basculegion") and not api_name.endswith("-male"):
        api_name += "-male"
    if api_name.startswith("urshifu") and not api_name.endswith("-rapid-strike"):
        api_name += "-single-strike"

    if api_name.startswith("greninja") and api_name.endswith("-bond"):
        api_name = api_name.replace("-bond", "")
    if api_name.startswith("necrozma") and api_name.endswith("-mane"):
        api_name = api_name.replace("-mane", "")
    if api_name.startswith("basculegion") and api_name.endswith("-f"):
        api_name = api_name.replace("-f", "-female")
    if api_name.startswith("indeedee") and api_name.endswith("-f"):
        api_name = api_name.replace("-f", "-female")
        
    if api_name.startswith("arceus"):
        api_name = "arceus"
    if api_name.startswith("silvally"):
        api_name = "silvally"
    if api_name.startswith("sinistcha"):
        api_name = "sinistcha"
    print(api_name)
    return api_name

def pokeAPICall(po_name):
    api_name = po_name.lower().replace(" ", "-")
    api_name = apiNameFix(api_name)

    url = f"https://pokeapi.co/api/v2/pokemon/{api_name}"
    response = requests.get(url)

    pokemon_api = None

    if response.status_code == 200:
        data = response.json()

        pokemon_api = {
            "name": data["name"].title(),
            "imageshiny": data["sprites"]["front_shiny"],
            "imagealt": data["sprites"]["front_default"],
            "stats": {
                "hp": data["stats"][0]["base_stat"],
                "attack": data["stats"][1]["base_stat"],
                "defense": data["stats"][2]["base_stat"],
                "sp_attack": data["stats"][3]["base_stat"],
                "sp_defense": data["stats"][4]["base_stat"],
                "speed": data["stats"][5]["base_stat"],
            },
            "types": [t["type"]["name"] for t in data["types"]]
        }
    return pokemon_api

def pokemonFilter(po_tourneyid, keyword, tier, type):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT po_pokeid, po_name, pl_name,po_tier, po_isteracaptain, po_type1, po_type2 FROM Pokemon JOIN Player ON pl_playerid = po_playerid WHERE po_tourneyID = %s"
    parameters = [po_tourneyid]

    if keyword:
        query += " AND (po_name LIKE %s OR pl_name LIKE %s)"
        parameters.extend([f"%{keyword}%", f"%{keyword}%"])

    if tier:
        query += " AND po_tier = %s"
        parameters.append(tier)

    if type:
        query += " AND (po_type1 = %s OR po_type2 = %s)"
        parameters.extend([type.lower(), type.lower()])

    query += " ORDER BY po_name ASC"

    cursor.execute(query, tuple(parameters))
    poke_results = cursor.fetchall()

    cursor.close()
    conn.close()
    return poke_results

def pokemonTeamFromPlayer(pl_tourneyid, pl_playerid):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT po_pokeid, po_name, po_tier, po_isTeraCaptain FROM Pokemon WHERE (po_tourneyID = %s and po_playerid = %s) ORDER BY po_name ASC;", (pl_tourneyid,pl_playerid,))
    pokemonteam = cursor.fetchall()

    cursor.close()
    conn.close()
    return pokemonteam

def pokepasteParser(url):
    team = pastes.team_from_url(url)

    pokemonTeam = []

    for mon in team.members:

        if mon.species == 'M' or mon.species == 'F':
            mon.species = mon.nickname
            mon.nickname = None

        if len(mon.moveset) < 4:
            if len(mon.moveset) == 1:
                mon.moveset.append("N/A")
                mon.moveset.append("N/A")
                mon.moveset.append("N/A")

            mon.moveset.append("Ivy Cudgel")

        pokemonData = {
            "name": mon.species,
            "nickname": mon.nickname,
            "item": mon.item,
            "ability": mon.ability,
            "EVs": mon.evs,
            "IVs": mon.ivs,
            "nature": mon.nature,
            "moves": mon.moveset,
            "isShiny": mon.shiny
        }

        pokemonTeam.append(pokemonData)

    return pokemonTeam