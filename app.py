from flask import Flask, render_template, request, redirect
import mysql.connector
import os

app = Flask(__name__)

# MySQL 연결 설정 (InfinityFree)
db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "sql112.infinityfree.com"),  # InfinityFree에서 제공한 Hostname
    user=os.getenv("DB_USER", "if0_38332634"),  # InfinityFree의 DB 사용자명
    password=os.getenv("DB_PASSWORD", "qBfuKy8ZlNlad"),  # 복사한 비밀번호 입력
    database=os.getenv("DB_NAME", "if0_38332634_lol_match_tracker"),  # 생성한 DB 이름
    port=int(os.getenv("DB_PORT", "3306"))
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record', methods=['GET', 'POST'])
def record():
    cursor = db.cursor()

    # GET 요청: 입력 페이지 렌더링 + 플레이어 & 챔피언 데이터 전달
    if request.method == 'GET':
        cursor.execute("SELECT player_name FROM players")
        players = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT champion_name FROM champions")
        champions = [row[0] for row in cursor.fetchall()]

        cursor.close()
        return render_template('record.html', players=players, champions=champions)

    # POST 요청: 경기 기록 저장
    winner = request.form['winner']
    match_date = request.form['match_date']

    blue_team = {
        "TOP": request.form['blue_top'],
        "JUNGLE": request.form['blue_jungle'],
        "MID": request.form['blue_mid'],
        "ADC": request.form['blue_adc'],
        "SUPPORT": request.form['blue_support']
    }
    red_team = {
        "TOP": request.form['red_top'],
        "JUNGLE": request.form['red_jungle'],
        "MID": request.form['red_mid'],
        "ADC": request.form['red_adc'],
        "SUPPORT": request.form['red_support']
    }

    blue_champions = {
        "TOP": request.form['blue_top_champion'],
        "JUNGLE": request.form['blue_jungle_champion'],
        "MID": request.form['blue_mid_champion'],
        "ADC": request.form['blue_adc_champion'],
        "SUPPORT": request.form['blue_support_champion']
    }
    red_champions = {
        "TOP": request.form['red_top_champion'],
        "JUNGLE": request.form['red_jungle_champion'],
        "MID": request.form['red_mid_champion'],
        "ADC": request.form['red_adc_champion'],
        "SUPPORT": request.form['red_support_champion']
    }

    # KDA 데이터 수집
    blue_kda = {
        "TOP": (request.form['blue_top_kill'], request.form['blue_top_death'], request.form['blue_top_assist']),
        "JUNGLE": (request.form['blue_jungle_kill'], request.form['blue_jungle_death'], request.form['blue_jungle_assist']),
        "MID": (request.form['blue_mid_kill'], request.form['blue_mid_death'], request.form['blue_mid_assist']),
        "ADC": (request.form['blue_adc_kill'], request.form['blue_adc_death'], request.form['blue_adc_assist']),
        "SUPPORT": (request.form['blue_support_kill'], request.form['blue_support_death'], request.form['blue_support_assist'])
    }
    red_kda = {
        "TOP": (request.form['red_top_kill'], request.form['red_top_death'], request.form['red_top_assist']),
        "JUNGLE": (request.form['red_jungle_kill'], request.form['red_jungle_death'], request.form['red_jungle_assist']),
        "MID": (request.form['red_mid_kill'], request.form['red_mid_death'], request.form['red_mid_assist']),
        "ADC": (request.form['red_adc_kill'], request.form['red_adc_death'], request.form['red_adc_assist']),
        "SUPPORT": (request.form['red_support_kill'], request.form['red_support_death'], request.form['red_support_assist'])
    }

    sql = """
        INSERT INTO matches 
        (match_date, 
        blue_top, blue_jungle, blue_mid, blue_adc, blue_support,
        red_top, red_jungle, red_mid, red_adc, red_support, winner,
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
        red_support_kill, red_support_death, red_support_assist)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        match_date,
        blue_team["TOP"], blue_team["JUNGLE"], blue_team["MID"], blue_team["ADC"], blue_team["SUPPORT"],
        red_team["TOP"], red_team["JUNGLE"], red_team["MID"], red_team["ADC"], red_team["SUPPORT"],
        winner,
        blue_champions["TOP"], blue_champions["JUNGLE"], blue_champions["MID"], blue_champions["ADC"], blue_champions["SUPPORT"],
        red_champions["TOP"], red_champions["JUNGLE"], red_champions["MID"], red_champions["ADC"], red_champions["SUPPORT"],
        *blue_kda["TOP"], *blue_kda["JUNGLE"], *blue_kda["MID"], *blue_kda["ADC"], *blue_kda["SUPPORT"],
        *red_kda["TOP"], *red_kda["JUNGLE"], *red_kda["MID"], *red_kda["ADC"], *red_kda["SUPPORT"]
    )

    cursor.execute(sql, values)
    db.commit()
    cursor.close()

    print(f"✅ 경기 기록 저장 완료: {match_date}, 블루팀: {blue_team}, 레드팀: {red_team}, 승리 팀: {winner}, 사용한 챔피언: {blue_champions}, {red_champions}")

    return redirect('/')

@app.route('/history')
def history():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM matches ORDER BY match_date DESC")
    matches = cursor.fetchall()  
    cursor.close()

    return render_template('history.html', matches=matches)

@app.route('/ranking')
def ranking():
    cursor = db.cursor()
    cursor.execute("""
        SELECT player, 
               COUNT(*) AS total_games, 
               SUM(CASE WHEN team = winner THEN 1 ELSE 0 END) AS wins,
               (SUM(CASE WHEN team = winner THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS win_rate,
               MAX(favorite_champion) AS favorite_champion, 
               MAX(favorite_position) AS favorite_position,
               ROUND(AVG(kda), 2) AS avg_kda
        FROM (
            SELECT blue_top AS player, 'blue' AS team, winner, 
                   blue_top_champion AS favorite_champion, 'TOP' AS favorite_position,
                   (blue_top_kill + blue_top_assist) / NULLIF(blue_top_death, 1) AS kda FROM matches UNION ALL
            SELECT blue_jungle, 'blue', winner, 
                   blue_jungle_champion, 'JUNGLE',
                   (blue_jungle_kill + blue_jungle_assist) / NULLIF(blue_jungle_death, 1) AS kda FROM matches UNION ALL
            SELECT blue_mid, 'blue', winner, 
                   blue_mid_champion, 'MID',
                   (blue_mid_kill + blue_mid_assist) / NULLIF(blue_mid_death, 1) AS kda FROM matches UNION ALL
            SELECT blue_adc, 'blue', winner, 
                   blue_adc_champion, 'ADC',
                   (blue_adc_kill + blue_adc_assist) / NULLIF(blue_adc_death, 1) AS kda FROM matches UNION ALL
            SELECT blue_support, 'blue', winner, 
                   blue_support_champion, 'SUPPORT',
                   (blue_support_kill + blue_support_assist) / NULLIF(blue_support_death, 1) AS kda FROM matches UNION ALL
            SELECT red_top, 'red', winner, 
                   red_top_champion, 'TOP',
                   (red_top_kill + red_top_assist) / NULLIF(red_top_death, 1) AS kda FROM matches UNION ALL
            SELECT red_jungle, 'red', winner, 
                   red_jungle_champion, 'JUNGLE',
                   (red_jungle_kill + red_jungle_assist) / NULLIF(red_jungle_death, 1) AS kda FROM matches UNION ALL
            SELECT red_mid, 'red', winner, 
                   red_mid_champion, 'MID',
                   (red_mid_kill + red_mid_assist) / NULLIF(red_mid_death, 1) AS kda FROM matches UNION ALL
            SELECT red_adc, 'red', winner, 
                   red_adc_champion, 'ADC',
                   (red_adc_kill + red_adc_assist) / NULLIF(red_adc_death, 1) AS kda FROM matches UNION ALL
            SELECT red_support, 'red', winner, 
                   red_support_champion, 'SUPPORT',
                   (red_support_kill + red_support_assist) / NULLIF(red_support_death, 1) AS kda FROM matches
        ) AS player_stats
        WHERE player IS NOT NULL
        GROUP BY player
        ORDER BY win_rate DESC;
    """)
    rankings = cursor.fetchall()
    print(rankings)  # 🔍 rankings 리스트 출력해서 avg_kda가 포함되는지 확인
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
            except mysql.connector.Error as err:
                print(f"Error: {err}")

    cursor.execute("SELECT * FROM players ORDER BY player_name")
    players = cursor.fetchall()
    cursor.close()

    return render_template('add_player.html', players=players)

@app.route('/add_champion', methods=['GET', 'POST'])
def add_champion():
    cursor = db.cursor()

    if request.method == 'POST':
        champion_name = request.form.get('champion_name', '').strip()
        if champion_name:
            try:
                cursor.execute("INSERT INTO champions (champion_name) VALUES (%s)", (champion_name,))
                db.commit()
            except mysql.connector.Error as err:
                print(f"Error: {err}")

    cursor.execute("SELECT * FROM champions ORDER BY champion_name")
    champions = cursor.fetchall()
    cursor.close()

    return render_template('add_champion.html', champions=champions)

if __name__ == '__main__':
    app.run(debug=True)

