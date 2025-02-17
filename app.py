from flask import Flask, render_template, request, redirect
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

db = psycopg2.connect(DATABASE_URL, sslmode="require")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record', methods=['GET', 'POST'])
def record():
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'GET':
        cursor.execute("SELECT player_name FROM players")
        players = [row['player_name'] for row in cursor.fetchall()]

        cursor.execute("SELECT champion_name FROM champions")
        champions = [row['champion_name'] for row in cursor.fetchall()]

        cursor.close()
        return render_template('record.html', players=players, champions=champions)

    match_date = request.form['match_date']
    winner = request.form['winner']

    blue_team = {pos: request.form[f'blue_{pos.lower()}'] for pos in ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']}
    red_team = {pos: request.form[f'red_{pos.lower()}'] for pos in ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']}

    blue_champions = {pos: request.form[f'blue_{pos.lower()}_champion'] for pos in ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']}
    red_champions = {pos: request.form[f'red_{pos.lower()}_champion'] for pos in ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']}

    blue_kda = {pos: (request.form[f'blue_{pos.lower()}_kill'], request.form[f'blue_{pos.lower()}_death'], request.form[f'blue_{pos.lower()}_assist']) for pos in ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']}
    red_kda = {pos: (request.form[f'red_{pos.lower()}_kill'], request.form[f'red_{pos.lower()}_death'], request.form[f'red_{pos.lower()}_assist']) for pos in ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']}

    sql = """
        INSERT INTO matches (
            match_date, winner,
            blue_top, blue_jungle, blue_mid, blue_adc, blue_support,
            red_top, red_jungle, red_mid, red_adc, red_support,
            blue_top_champion, blue_jungle_champion, blue_mid_champion, blue_adc_champion, blue_support_champion,
            red_top_champion, red_jungle_champion, red_mid_champion, red_adc_champion, red_support_champion,
            blue_top_kill, blue_top_death, blue_top_assist,
            blue_jungle_kill, blue_jungle_death, blue_jungle_assist,
            blue_mid_kill, blue_mid_death, blue_mid_assist,
            blue_adc_kill, blue_adc_death, blue_adc_assist,
            blue_support_kill, blue_support_death, blue_support_assist,
            red_top_kill, red_top_death, red_top_assist,
            red_jungle_kill, red_jungle_death, red_jungle_assist,
            red_mid_kill, red_mid_death, red_mid_assist,
            red_adc_kill, red_adc_death, red_adc_assist,
            red_support_kill, red_support_death, red_support_assist
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    values = (
        match_date, winner,
        *blue_team.values(), *red_team.values(),
        *blue_champions.values(), *red_champions.values(),
        *sum(blue_kda.values(), ()), *sum(red_kda.values(), ())
    )

    try:
        cursor.execute(sql, values)
        db.commit()
    except psycopg2.Error as err:
        print(f"Error: {err}")
        db.rollback()
    finally:
        cursor.close()

    return redirect('/')

@app.route('/ranking')
def ranking():
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
        SELECT player,
               COUNT(*) AS total_games,
               SUM(CASE WHEN team = winner THEN 1 ELSE 0 END) AS wins,
               ROUND((SUM(CASE WHEN team = winner THEN 1 ELSE 0 END) / COUNT(*) * 100)::numeric, 2) AS win_rate,
               MAX(favorite_champion) AS favorite_champion,
               MAX(favorite_position) AS favorite_position,
               ROUND(AVG(NULLIF(kda, 0))::numeric, 2) AS avg_kda
        FROM (
            SELECT blue_top AS player, 'blue' AS team, winner, blue_top_champion AS favorite_champion, 'TOP' AS favorite_position,
                   (blue_top_kill + blue_top_assist) / NULLIF(blue_top_death, 0) AS kda FROM matches
            UNION ALL
            SELECT red_top, 'red', winner, red_top_champion, 'TOP',
                   (red_top_kill + red_top_assist) / NULLIF(red_top_death, 0) AS kda FROM matches
        ) AS player_stats
        WHERE player IS NOT NULL
        GROUP BY player
        ORDER BY win_rate DESC
    """)

    rankings = cursor.fetchall()
    cursor.close()

    return render_template('ranking.html', rankings=rankings)

@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    cursor = db.cursor()

    if request.method == 'POST':
        player_name = request.form.get('player_name', '').strip()
        if player_name:
            try:
                cursor.execute("INSERT INTO players (player_name) VALUES (%s)", (player_name,))
                db.commit()
            except psycopg2.Error as err:
                print(f"Error: {err}")
                db.rollback()

    cursor.execute("SELECT * FROM players ORDER BY player_name")
    players = cursor.fetchall()
    cursor.close()

    return render_template('add_player.html', players=players)

if __name__ == '__main__':
    app.run(debug=True)
