import pandas as pd
import matplotlib.pyplot as plt
import io

def get_query(user_id):
    return f"""
            SELECT DATE(added_at) as date, COUNT(*) as count
            FROM user_words
            WHERE user_id = {user_id}
            GROUP BY DATE(added_at)
            ORDER BY date;
            """

def get_word_progress_plot(conn, user_id):

    try:
        with conn.cursor() as cursor:
            cursor.execute(get_query(user_id))
            
            results = cursor.fetchall()

            dates = [r[0] for r in results]
            counts = [r[1] for r in results]

            plt.figure(figsize=(10,6))
            plt.plot(dates, counts, marker='*')
            plt.title('Your learning progress')
            plt.xlabel('Date')
            plt.ylabel('Words')
            plt.xticks(rotation=45)

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)

            return buffer

    except Exception as e:
        print(f"Error generating statistics: {e}")
        return None
        
def get_stats_summary(conn, user_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute(get_query(user_id=user_id))
            
            results = cursor.fetchall()

            dates = [r[0] for r in results]
            counts = [r[1] for r in results]

            total_words = sum(counts)
            avg_per_day = total_words / len(dates) if dates else 0
            days_studying = len(dates)

            return {
                "total_words":total_words,
                "avg_per_day":avg_per_day,
                "days_studying":days_studying
                }
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None