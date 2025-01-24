import pandas as pd
import matplotlib.pyplot as plt
import io

# Properties
plt.rcParams['font.family'] = 'futura'
plt.rcParams['font.size'] = 15
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.left'] = False
plt.rcParams['axes.spines.bottom'] = False

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
            
            # Calculate cumulative sum and convert to integers
            cumulative_counts = [int(x) for x in pd.Series(counts).cumsum().tolist()]

            plt.style.use('seaborn-v0_8-pastel')

            plt.figure(figsize=(12,8), dpi=150)
            
            plt.fill_between(dates, cumulative_counts, color='#2ecc71', alpha=0.5)
            plt.plot(dates, cumulative_counts, color='#27ae60', linewidth=2)
            
            plt.title('Your Vocabulary Learning Journey', fontsize=18, pad=15)
            
            plt.xticks(rotation=35, ha='right', fontsize=14)
            plt.yticks(fontsize=14)
            
            plt.grid(True, alpha=0.25)
            
            plt.tight_layout()

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            plt.close()

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
            daily_average = total_words / len(dates) if dates else 0
            days_studying = len(dates)

            return {
                "total_words":total_words,
                "daily_average":daily_average,
                "days_studying":days_studying
                }
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None