from flask import Flask, request, render_template, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from helper import generate_answer_for, MAX_ROUNDS, fizzbuzz

app = Flask(__name__)
app.config.from_object('settings')
db = SQLAlchemy(app)


player_in_game = db.Table('player_in_game',
    db.Column('player_id', db.Integer, db.ForeignKey('player.id')),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id')),
)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(200), unique=True)
    skill = db.Column(db.Integer)
    number_games_won = db.Column(db.Integer, default=0)
    won_in_games = db.relationship('Game', backref='winner',
                                lazy='dynamic')

    def __init__(self, player_name, skill):
        self.player_name = player_name
        self.skill = skill

    def __repr__(self):
        return '<Player %r>' % self.player_name


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    players = db.relationship('Player', secondary=player_in_game,
                              backref=db.backref('games'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime, nullable=True)
    number_of_rounds = db.Column(db.Integer)

    def __init__(self, start_date, players):
        self.start_date = start_date
        self.players = players

    def __repr__(self):
        return '<Game %r won by %r>' % self.id, self.winner


def play_fizzbuzz(players):
    """
    Main loop of Fizz Buzz game.
    Fizz buzz is a counting game where each player speaks a number from 1 to n
    in sequence, but with a few exceptions:
    - if the would-be spoken number is divisible by 3 the player must say fizz
    instead
    - if the would-be spoken number is divisible by 5 the player must say buzz
    instead
    - if the would-be spoken number is divisible by 3 and 5 the player must say
    fizzbuzz instead
    """
    result = {'rounds': []}
    active_players = [player for player in players]
    current_round = 1
    current_number = 1
    game = Game(datetime.now(), players)

    while len(active_players) > 1 and current_round < MAX_ROUNDS:
        # During each round
        round_dict = {'round_number': current_round,
                 'moves': []}
        loosers = []

        for player in active_players:
            # Each player has its own answer
            answer = generate_answer_for(player, current_number)
            move = {"player_name": player.player_name,
                    "answer": answer}
            # check answer
            if answer == fizzbuzz(current_number):
                move['is_correct'] = True
            else:
                loosers.append(player)
                move['is_correct'] = False
            current_number = current_number + 1
            round_dict['moves'].append(move)
            # play further in this round only if more players are in
            if len(active_players) - len(loosers) < 2:
                break
        # Loosers are not in the game anymore
        for looser in loosers:
            active_players.remove(looser)
        result['rounds'].append(round_dict)
        current_round = current_round + 1

    if len(active_players) == 1:
        # Save game results and update winner status
        game.end_date = datetime.now()
        winner = active_players[0]
        winner.number_games_won = winner.number_games_won + 1
        game.winner = winner
        game.number_of_rounds = current_round
        db.session.add(game)
        db.session.commit()
        result["winner"] = winner
    else:
        # Draw game - no winner
        result["winner"] = None

    return result


@app.route('/', methods=['POST', 'GET'])
def main():
    error = None
    if request.method == 'POST':
        player_ids = request.form.getlist('player_id')
        players = Player.query.filter(Player.id.in_(player_ids)).all()
        # Do not start if one player is checked
        if len(players) > 1:
            result = play_fizzbuzz(players)
            return render_template('game.html', result=result)
        else:
            error = 'Please select at least two players for a game.'

    players = Player.query.all()
    leader_board = Player.query.order_by(-Player.number_games_won).limit(10).\
    all()
    recent_games = Game.query.order_by(Game.end_date.desc()).limit(10).all()
    return render_template('fizzbuzz.html',
                           players=players,
                           leader_board=leader_board,
                           recent_games=recent_games,
                           error=error)


@app.route('/add_player', methods=['POST', 'GET'])
def add_player():
    if request.method == 'POST':
        name = request.form['player_name']
        skill = int(request.form['skill'])
        new_player = Player(name, skill)
        db.session.add(new_player)
        db.session.commit()
        return redirect(url_for('main'))

    return render_template('add_player.html')

if __name__ == '__main__':
    app.run()
