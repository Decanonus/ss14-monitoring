import streamlit as st
import requests
import json
from datetime import datetime
import time
import pandas as pd
import pytz
import schedule
import os

st.set_page_config(
    page_title="SS14 Статистика серверов",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
    <style>
        .stMetric {
            background-color: #2b2b2b;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
            max-width: 200px;
        }
        .stMetric:hover {
            background-color: #3b3b3b;
        }
        [data-testid="metric-container"] {
            padding: 10px;
            border-radius: 5px;
        }
        .high-players {
            background-color: rgba(0, 255, 0, 0.2);
        }
        .medium-players {
            background-color: rgba(255, 255, 0, 0.2);
        }
        .low-players {
            background-color: rgba(255, 0, 0, 0.2);
        }
        .very-low-players {
            background-color: black;
        }
    </style>
""", unsafe_allow_html=True)

def get_moscow_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    return datetime.now(moscow_tz)

def get_server_stats():
    url = 'https://hub.spacestation14.com/api/servers'
    try:
        r = requests.get(url)
        jsonn = json.loads(r.text)
        
        server_groups = {
            'Корвакс': ['Corvax'],
            'Санрайз': ['РЫБЬЯ', 'LUST', 'SUNRISE'],
            'Империал': ['Imperial'],
            'Спейс Сторис': ['Stories'],
            'Мёртвый Космос': ['МЁРТВЫЙ'],
            'Резерв': ['Reserve'],
            'Атараксия': ['Ataraxia'],
            'Виктория': ['Victoria'],
            'СС220': ['SS220'],
            'Время Приключений': ['Время']
        }

        stats = []
        for group_name, keywords in server_groups.items():
            total_players = sum(
                servers['statusData']['players']
                for servers in jsonn
                for keyword in keywords
                if keyword in servers['statusData']['name']
            )
            stats.append({
                'Сервер': group_name,
                'Игроки': total_players
            })
        
        return sorted(stats, key=lambda x: x['Игроки'], reverse=True)
    except Exception as e:
        st.error(f"Ошибка при получении данных: {e}")
        return []

def save_daily_stats(stats):
    current_time = get_moscow_time()
    
    if not os.path.exists('daily_stats'):
        os.makedirs('daily_stats')
    
    filename = f"daily_stats/{current_time.strftime('%Y-%m')}.csv"
    
    data = {
        'date': current_time.strftime('%Y-%m-%d'),
        'time': current_time.strftime('%H:%M:%S'),
        'timestamp': current_time.timestamp()
    }
    
    for stat in stats:
        data[stat['Сервер']] = stat['Игроки']
    
    df_new = pd.DataFrame([data])
    
    if os.path.exists(filename):
        df_existing = pd.read_csv(filename)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = df_new
    

    df.to_csv(filename, index=False)
    print(f"Статистика сохранена в {filename}")

def daily_record():
    stats = get_server_stats()
    if stats:
        save_daily_stats(stats)

def setup_scheduler():
    moscow_tz = pytz.timezone('Europe/Moscow')
    
    def is_time_to_run():
        moscow_time = datetime.now(moscow_tz)
        return moscow_time.hour == 20 and moscow_time.minute == 0
    
    schedule.every().day.at("20:00").do(daily_record)
    
    while True:
        if is_time_to_run():
            daily_record()
            time.sleep(60) 
        schedule.run_pending()
        time.sleep(30) 

def main():
    st.title("🚀 Статистика серверов SS14")
    
    import threading
    scheduler_thread = threading.Thread(target=setup_scheduler, daemon=True)
    scheduler_thread.start()
    
    placeholder = st.empty()
    countdown_placeholder = st.empty()
    
    while True:
        for seconds in range(10, 0, -1):
            countdown_placeholder.markdown(f"Следующее обновление через {seconds} секунд...")
            time.sleep(1)
        
        stats = get_server_stats()
        
        with placeholder.container():
            if stats:
                df = pd.DataFrame(stats)
                
                current_time = get_moscow_time()
                st.write(f"Последнее обновление: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (МСК)")
                
                for row in stats:
                    players = row['Игроки']
                    if players >= 300:
                        style_class = "high-players"
                    elif players >= 100:
                        style_class = "medium-players"
                    elif players < 20:
                        style_class = "very-low-players"
                    else:
                        style_class = "low-players"
                    
                    st.markdown(f"""
                        <div class="{style_class}">
                            <div data-testid="metric-container">
                                <label>{row['Сервер']}</label>
                                <div data-testid="stMetricValue" style="font-size: 24px;">{players}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.subheader("График распределения игроков")
                fig = st.bar_chart(
                    df.set_index('Сервер')['Игроки'],
                    use_container_width=True
                )
                
                st.subheader("Детальная информация")
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

if __name__ == '__main__':
    main()