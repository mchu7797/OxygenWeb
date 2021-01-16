from flask import Flask
from flask import abort
from flask import render_template
from flask import request

from flask_cors import CORS

from metadata import O2JamMetadata
from scoreboard import O2JamScoreboard
from scoreboard import status_category_column_name
from utils import O2JamUtils

import json

scoreboard = O2JamScoreboard()
metadata = O2JamMetadata()
utils = O2JamUtils()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/online')
@app.route('/online-for-launcher')
def online():
    online_players = utils.get_online_players()
    return render_template('online.html', online=online_players)

@app.route('/api/online_players')
def online_api():
    online_players = utils.get_online_players()
    return json.dumps(online_players, ensure_ascii=False)

@app.route('/troubleshoot')
def show_troubleshoot():
    return render_template('troubleshoot.html')

@app.route('/troubleshoot/fix-login', methods=['POST'])
def fix_login():
    id = request.form['o2jam-id']
    pw = request.form['o2jam-pw']
    utils.fix_cannot_login(id, pw)
    return render_template('troubleshoot.html', fix_success=True)

@app.route('/troubleshoot/gem-to-cash', methods=['POST'])
def gem_to_cash():
    id = request.form['o2jam-id']
    pw = request.form['o2jam-pw']
    gem_amount = int(request.form['gem-amount'])

    result = utils.gem_to_cash(id, pw, gem_amount)
    
    if result == 3:
        wallet = utils.get_wallet(id)
    else:
        wallet = None

    return render_template('troubleshoot.html', gtc_result=result, wallet=wallet)

@app.route('/music', methods=['GET'])
def music_find():
    keyword = request.args.get('keyword')

    if keyword is None:
        return render_template('find-music.html', song_list=[], init=True)
    else:
        music_list = utils.search_song(keyword)
        return render_template('find-music.html', song_list=music_list, init=False)


@app.route('/player-scoreboard/<player_code>')
@app.route('/player-scoreboard/<player_code>/<difficulty>')
def player_scoreboard(player_code, difficulty=2):
    player_scores = scoreboard.get_player_scoreboard(player_code, difficulty)
    player_metadata = metadata.get_player_info(player_code, difficulty)
    player_tiers = metadata.get_tier_info(player_code)

    if player_metadata is not None:
        return render_template('player.html', scoreboard=player_scores, metadata=player_metadata, tier=player_tiers)
    else:
        return abort(404)


@app.route('/music-scoreboard/<music_code>')
@app.route('/music-scoreboard/<music_code>/<difficulty>')
def music_scoreboard(music_code, difficulty=2):
    if music_code is not None:
        music_scores = scoreboard.get_music_scoreboard(music_code, difficulty)
        music_metadata = metadata.get_music_info(music_code, difficulty)

        if music_metadata is not None:
            return render_template('music.html', scoreboard=music_scores, metadata=music_metadata)
        else:
            return abort(404)


@app.route('/ranking')
@app.route('/ranking/<ranking_category>')
def ranking(ranking_category=7):
    try:
        category = int(ranking_category)
        if 0 <= category <= 8:
            return render_template('ranking.html', status=scoreboard.get_status_ranking(category),
                                   category_name=status_category_column_name[category])
        else:
            return abort(404)
    except ValueError:
        return abort(404)


if __name__ == '__main__':
    app.run()
