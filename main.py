import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import pytz
import time

st.set_page_config(
    page_title="SS14 Статистика серверов",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
    <style>
        .metric-container {
            padding: 10px;
            border-radius: 5px;
            margin: 2px 0;
            width: 100%;
            min-height: 60px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .metric-label {
            font-size: 16px;
            font-weight: bold;
        }
        .metric-value {
            font-size: 20px;
            font-weight: bold;
        }
        .countdown {
            font-size: 18px;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #2b2b2b;
            border-radius: 5px;
            text-align: center;
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

def main():
    st.title("🚀 Статистика серверов SS14")
    
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()
        st.session_state.next_update = datetime.now() + timedelta(seconds=10)
    
    current_time = datetime.now()
    time_left = (st.session_state.next_update - current_time).total_seconds()
    
    if time_left <= 0:
        st.session_state.last_update = datetime.now()
        st.session_state.next_update = datetime.now() + timedelta(seconds=10)
        st.experimental_rerun()
    
    stats = get_server_stats()
    
    if stats:
        df = pd.DataFrame(stats)
        
        # Создаем контейнер для таймера и метрик
        with st.container():
            st.markdown(f"""
                <div class="countdown">
                    Следующее обновление через: {int(time_left)} секунд
                </div>
            """, unsafe_allow_html=True)
            
            st.write(f"Последнее обновление: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')} (МСК)")
            
            # Отображаем метрики серверов
            for row in reversed(stats):
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
                    <div class="metric-container {style_class}">
                        <div class="metric-label">{row['Сервер']}</div>
                        <div class="metric-value">{players}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Отдельный контейнер для графиков и таблиц
        with st.container():
            st.subheader("График распределения игроков")
            st.bar_chart(
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
