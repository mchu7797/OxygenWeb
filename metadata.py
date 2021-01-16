from database import get_sql_console


class O2JamMetadata:
    def __init__(self):
        self.__sql_console = get_sql_console()

    def get_player_info(self, player_code, difficulty):
        self.__sql_console.execute('''
            SELECT 
                USER_NICKNAME, 
                Level, 
                Battle, 
                AdminLevel,
                USER_INDEX_ID
            FROM 
                dbo.T_o2jam_charinfo 
            WHERE 
                USER_INDEX_ID = {}
        '''.format(player_code))

        base_player_info = self.__sql_console.fetchone()

        self.__sql_console.execute('''
            WITH Status AS (
                SELECT 
                    PlayerCode, 
                    RANK() OVER (
                        ORDER BY 
                            Clear desc
                    ) Ranking 
                FROM 
                    dbo.O2JamStatus
            ) 
            SELECT 
                Ranking 
            FROM 
                Status
            WHERE 
                PlayerCode = {}
        '''.format(player_code))

        player_ranking = self.__sql_console.fetchone()

        self.__sql_console.execute('''
            SELECT
                COUNT(*)
            FROM
                dbo.O2JamStatus
            WHERE
                Clear=(SELECT Clear FROM dbo.O2JamStatus WHERE PlayerCode={})
        '''.format(player_code))

        tie_player_count = int(self.__sql_console.fetchone()[0])

        if base_player_info and player_ranking is not None:
            player_info = {
                'nickname': base_player_info[0],
                'level': base_player_info[1],
                'play_count': base_player_info[2],
                'admin_level': base_player_info[3],
                'player_ranking': player_ranking[0],
                'current_view_difficulty': int(difficulty),
                'tie_player_count': tie_player_count,
                'player_code': base_player_info[4]
            }

            return player_info
        elif base_player_info is not None:
            player_info = {
                'nickname': base_player_info[0],
                'level': base_player_info[1],
                'play_count': base_player_info[2],
                'admin_level': base_player_info[3],
                'player_ranking': 0,
                'current_view_difficulty': int(difficulty),
                'player_code': base_player_info[4]
            }

            return player_info
        else:
            return None

    def get_tier_info(self, player_code):
        self.__sql_console.execute('''
            SELECT
              s.P,
              s.SS,
              s.S,
              s.A,
              s.B,
              s.C,
              s.D,
              s.Clear,
              t.tier_name
            FROM
              dbo.O2JamStatus s
              LEFT OUTER JOIN dbo.TierInfo t ON s.Tier = t.tier_index
            WHERE
              PlayerCode = {}
        '''.format(player_code))

        query_result = self.__sql_console.fetchone()

        if query_result is not None:
            tier_info = {
                'p_rank': query_result[0],
                'ss_rank': query_result[1],
                's_rank': query_result[2],
                'a_rank': query_result[3],
                'b_rank': query_result[4],
                'c_rank': query_result[5],
                'd_rank': query_result[6],
                'cleared': query_result[7],
                'tier': query_result[8],
            }
        else:
            tier_info = {
                'p_rank': 0,
                'ss_rank': 0,
                's_rank': 0,
                'a_rank': 0,
                'b_rank': 0,
                'c_rank': 0,
                'd_rank': 0,
                'cleared': 0,
                'tier': 'NONE'
            }

        return tier_info

    def get_music_info(self, ojn_code, difficulty):
        self.__sql_console.execute('''
            SELECT
                d.MusicCode,
                m.Title,
                d.NoteLevel,
                d.NoteCount,
                m.Artist,
                m.NoteCharter,
                m.BPM
            FROM
                dbo.o2jam_music_data d
                LEFT OUTER JOIN dbo.o2jam_music_metadata m ON m.MusicCode = d.MusicCode
            WHERE
                d.MusicCode = {}
                AND d.Difficulty = {}
        '''.format(ojn_code, difficulty))

        query_data = self.__sql_console.fetchone()

        if query_data is not None:
            music_info = {
                'music_code': query_data[0],
                'title': query_data[1],
                'difficulty': int(difficulty),
                'level': query_data[2],
                'note_count': query_data[3],
                'artist': query_data[4],
                'note_charter': query_data[5],
                'bpm': round(float(query_data[6]))
            }

            return music_info
        else:
            return None
