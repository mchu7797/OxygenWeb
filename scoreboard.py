from database import get_sql_console

status_category_column_name = [
    'P', 'SS', 'S', 'A', 'B', 'C', 'D', 'Clear', 'PlayCount'
]


class O2JamScoreboard:
    def __init__(self):
        self.__sql_console = get_sql_console()

    def get_player_scoreboard(self, player_code, difficulty=2):
        self.__sql_console.execute('''
            SELECT
              h.PlayerCode,
              h.MusicCode,
              md.Title,
              h.Difficulty,
              d.NoteLevel,
              h.Score,
              p.progress_name,
              h.isClear,
              h.PlayedTime,
              sr.SongRank,
              ROW_NUMBER() OVER (
                ORDER BY
                  d.NoteLevel DESC,
                  h.Score DESC
              ) RowNumber
            FROM
              dbo.O2JamHighscore h
              LEFT OUTER JOIN dbo.o2jam_music_metadata md ON md.MusicCode = h.MusicCode
              LEFT OUTER JOIN dbo.o2jam_music_data d ON d.MusicCode = h.MusicCode
              AND d.Difficulty = h.Difficulty
              LEFT OUTER JOIN dbo.ProgressInfo p ON p.progress_index = h.Progress
              LEFT OUTER JOIN (
                SELECT
                  PlayerCode,
                  MusicCode,
                  Difficulty,
                  RANK() OVER (
                    PARTITION BY MusicCode,
                    Difficulty
                    ORDER BY
                      Score DESC
                  ) SongRank
                FROM
                  dbo.O2JamHighscore
              ) sr on sr.PlayerCode = h.PlayerCode
              AND sr.MusicCode = h.MusicCode
              AND sr.Difficulty = h.Difficulty
            WHERE
              h.PlayerCode = {}
              AND h.Difficulty = {}
              AND (
                h.Progress <= 7
                OR (
                  h.isClear = 1
                  AND h.Progress = 8
                )
              )
        '''.format(player_code, difficulty))

        query_data = self.__sql_console.fetchall()

        player_scoreboard = []

        for raw_player_scoreboard in query_data:
            player_score = {
                'player_code': raw_player_scoreboard[0],
                'music_code': raw_player_scoreboard[1],
                'music_title': raw_player_scoreboard[2],
                'music_difficulty': raw_player_scoreboard[3],
                'music_level': raw_player_scoreboard[4],
                'score': round(int(raw_player_scoreboard[5]) / 10000, 2),
                'progress': raw_player_scoreboard[6],
                'is_cleared_record': raw_player_scoreboard[7],
                'cleared_time': raw_player_scoreboard[8],
                'record_rank': raw_player_scoreboard[9],
                'row_number': raw_player_scoreboard[10]
            }

            player_scoreboard.append(player_score)

        if len(player_scoreboard) < 1:
            return []
        else:
            return player_scoreboard

    def get_music_scoreboard(self, ojn_code, difficulty=2):
        self.__sql_console.execute('''
            SELECT 
                h.PlayerCode, 
                c.USER_NICKNAME, 
                h.Cool, 
                h.Good, 
                h.Bad, 
                h.Miss, 
                h.MaxCombo, 
                h.Score,
                h.isClear,
                h.PlayedTime,
                p.progress_name,
                ROW_NUMBER() OVER (ORDER BY h.Score DESC, h.isClear DESC) status
            FROM 
                dbo.O2JamHighscore h 
                LEFT OUTER JOIN dbo.T_o2jam_charinfo c on h.PlayerCode = c.USER_INDEX_ID
                LEFT OUTER JOIN dbo.ProgressInfo p ON p.progress_index = h.Progress
            WHERE 
                h.MusicCode = {}
                AND h.Difficulty = {}
            ORDER BY
                h.Score desc
        '''.format(ojn_code, difficulty))

        query_data = self.__sql_console.fetchall()

        music_status = []

        for raw_music_record in query_data:
            music_record = {
                'player_code': raw_music_record[0],
                'player_nickname': raw_music_record[1],
                'score_cool': raw_music_record[2],
                'score_good': raw_music_record[3],
                'score_bad': raw_music_record[4],
                'score_miss': raw_music_record[5],
                'score_max_combo': raw_music_record[6],
                'score': round(int(raw_music_record[7]) / 10000, 2),
                'is_cleared_record': raw_music_record[8],
                'cleared_time': raw_music_record[9],
                'progress': raw_music_record[10],
                'row_number': raw_music_record[11]
            }

            music_status.append(music_record)

        if len(music_status) < 1:
            return []
        else:
            return music_status

    def get_status_ranking(self, status_category):

        if status_category == 8:
            self.__sql_console.execute('''
                SELECT 
                    c.USER_INDEX_ID, 
                    c.USER_NICKNAME, 
                    c.Battle, 
                    t.tier_name,
                    RANK() OVER (ORDER BY battle desc) RowNum
                FROM 
                    dbo.T_o2jam_charinfo c 
                    LEFT OUTER JOIN dbo.O2JamStatus s on s.PlayerCode = c.USER_INDEX_ID 
                    LEFT OUTER JOIN dbo.TierInfo t on s.Tier = t.tier_index
            ''')

            query_data = self.__sql_console.fetchall()

            play_count_status = []

            for raw_play_count in query_data:
                play_count = {
                    'player_code': raw_play_count[0],
                    'player_nickname': raw_play_count[1],
                    'rank': raw_play_count[2],
                    'tier': raw_play_count[3],
                    'row_number': raw_play_count[4],
                }

                play_count_status.append(play_count)

            return play_count_status
        else:
            self.__sql_console.execute('''
                SELECT
                    s.PlayerCode, 
                    c.USER_NICKNAME, 
                    s.{status_category}, 
                    t.tier_name,
                    RANK() OVER (ORDER BY s.{status_category} desc, s.Tier ASC) RowNum
                FROM 
                    dbo.O2JamStatus s
                    LEFT OUTER JOIN dbo.T_o2jam_charinfo c on s.PlayerCode = c.USER_INDEX_ID 
                    LEFT OUTER JOIN dbo.TierInfo t on s.Tier = t.tier_index
            '''.format(
                status_category=status_category_column_name[status_category]
            ))

            query_data = self.__sql_console.fetchall()

            player_status = []

            for raw_player_rank in query_data:
                player_rank = {
                    'player_code': raw_player_rank[0],
                    'player_nickname': raw_player_rank[1],
                    'rank': raw_player_rank[2],
                    'tier': raw_player_rank[3],
                    'row_number': raw_player_rank[4]
                }

                player_status.append(player_rank)

            return player_status
