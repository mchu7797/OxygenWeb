from database import get_sql_console, get_sql_console_trade


class O2JamUtils:
    def __init__(self):
        self.__sql_console = get_sql_console()
        self.__trade_sql_console = get_sql_console_trade()

    def get_online_players(self):
        self.__sql_console.execute('''
            SELECT
              charinfo.USER_NICKNAME,
              charInfo.Level,
              login.SUB_CH
            FROM
              dbo.T_o2jam_login login
              LEFT OUTER JOIN dbo.T_o2jam_charinfo charInfo on charinfo.USER_INDEX_ID = login.USER_INDEX_ID
            ORDER BY
              charInfo.Level desc
        ''')

        query_answer = self.__sql_console.fetchall()

        ch_shd = []
        ch_hd = []
        ch_nm = []
        ch_ez = []

        for row in query_answer:
            player_data = {
                'player_nickname': row[0],
                'player_level': int(row[1])
            }

            if row[2] == 0:
                ch_shd.append(player_data)
            elif row[2] == 1:
                ch_hd.append(player_data)
            elif row[2] == 2:
                ch_nm.append(player_data)
            else:
                ch_ez.append(player_data)

        online_players = {
            'super_hard_channel': ch_shd,
            'hard_channel': ch_hd,
            'normal_channel': ch_nm,
            'easy_channel': ch_ez,
            'all_players_count': len(query_answer)
        }

        return online_players

    def search_song(self, keyword):
        self.__sql_console.execute('''
            SELECT m.MusicCode,
                   Title,
                   Artist,
                   NoteCharter,
                   BPM,
                   n.NoteLevel
            FROM dbo.o2jam_music_metadata m
            RIGHT OUTER JOIN (SELECT MusicCode, NoteLevel FROM dbo.o2jam_music_data WHERE Difficulty = 2) n ON n.MusicCode = m.MusicCode
            WHERE Title LIKE '%{keyword}%'
               OR Artist LIKE '%{keyword}%'
               OR NoteCharter LIKE '%{keyword}%'
            ORDER BY n.NoteLevel desc
        '''.format(keyword=keyword))

        query_results = self.__sql_console.fetchall()
        queried_song_list = []

        for query_result in query_results:
            song_data = {
                'player_code': query_result[0],
                'title': query_result[1],
                'artist': query_result[2],
                'note_charter': query_result[3],
                'bpm': query_result[4],
                'hard_level': query_result[5]
            }

            queried_song_list.append(song_data)

        return queried_song_list

    def fix_cannot_login(self, player_id, password):
        self.__sql_console.execute('''
            DELETE FROM
                dbo.T_o2jam_login
            FROM
                dbo.T_o2jam_login login
            LEFT OUTER JOIN
                dbo.member member
            ON 
                member.userid = login.USER_ID
            WHERE
                member.userid = '{}'
                AND member.passwd = '{}'
        '''.format(
            player_id, password
        ))

        self.__sql_console.commit()

    # GEM TO CASH EXCHANGE RATE = 0.01
    def gem_to_cash(self, player_id, password, amount_of_gem):
        self.__sql_console.execute('''
            DECLARE @PlayerId int

            SELECT
                @PlayerId = charinfo.USER_INDEX_ID
            FROM 
                dbo.member member
            LEFT OUTER JOIN
                dbo.T_o2jam_charinfo charinfo
            ON
                member.userid = charinfo.USER_ID
            WHERE
                member.userid = '{}'
                AND member.passwd = '{}'

            SELECT
                @PlayerId = ISNULL(@PlayerId, 0)

            SELECT
                @PlayerId AS PlayerId
        '''.format(
            player_id, password
        ))

        player_index_id = self.__sql_console.fetchone()[0]

        if player_index_id == 0:
            return 1 # Player not found.

        self.__sql_console.execute('''
            SELECT
                GEM, MCASH
            FROM
                dbo.T_o2jam_charCash
            WHERE
                USER_INDEX_ID = {}
        '''.format(player_index_id))

        player_wallet = self.__sql_console.fetchone()
        # GEM = index 0, MCASH = index 1

        if amount_of_gem < 100:
            return 2 # Amount of Gems are so low.

        if player_wallet[0] < amount_of_gem:
            return 3 # Gems of player are so low than be exchanged gems.

        player_wallet[1] += (amount_of_gem / 100)
        player_wallet[0] -= amount_of_gem

        self.__sql_console.execute('''
            UPDATE
                dbo.T_o2jam_charCash
            SET
                GEM = {},
                MCASH = {}
            WHERE
                USER_INDEX_ID = {}
        '''.format(
            player_wallet[0],
            player_wallet[1],
            player_index_id
        ))

        self.__sql_console.commit()

        self.__trade_sql_console.execute('''
            UPDATE dbo.UserMcash SET MCASH='{}' WHERE id = '{}'
        '''.format(
            int(player_wallet[1]),
            player_index_id
        ))

        self.__trade_sql_console.commit()
        
        return 0
    
    def get_wallet(self, player_id):
        self.__sql_console.execute('''
            SELECT
                info.USER_INDEX_ID,
                cash.GEM,
                cash.MCASH
            FROM
                dbo.T_o2jam_charinfo info
            LEFT OUTER JOIN
                dbo.T_o2jam_charCash cash
            ON
                info.USER_INDEX_ID = cash.USER_INDEX_ID
            WHERE
                info.USER_ID = '{}'
        '''.format(player_id))

        raw_result = self.__sql_console.fetchone()

        response = {
            'player_code': raw_result[0],
            'gem': raw_result[1],
            'mcash': raw_result[2]
        }

        return response