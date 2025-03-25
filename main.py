import streamlit as st
import requests
import json
from datetime import datetime
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
            padding: 5px;
            border-radius: 5px;
            margin: 1px 0;  
            width: 100%;
            min-height: 35px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .metric-label {
            font-size: 12px;
            font-weight: bold;
        }
        .metric-value {
            font-size: 16px;
            font-weight: bold;
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
        .highlight-high {
            background-color: rgba(0, 255, 0, 0.5);
        }
        .highlight-medium {
            background-color: rgba(255, 255, 0, 0.5);
        }
        .highlight-low {
            background-color: rgba(255, 0, 0, 0.5);
        }
        .highlight-very-low {
            background-color: rgba(128, 128, 128, 0.5);
        }
    </style>
""", unsafe_allow_html=True)

def get_moscow_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    return datetime.now(moscow_tz)

@st.cache_data(ttl=10)  # Кеширование на 10 секунд
def get_server_stats():
    url = 'https://hub.spacestation14.com/api/servers'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        json_data = response.json()
        
        server_groups = {
            'Корвакс': ['Corvax'],
            'Санрайз': ['РЫБЬЯ', 'LUST', 'SUNRISE', 'FIRE'],
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
                server['statusData']['players']
                for server in json_data
                for keyword in keywords
                if keyword in server['statusData']['name']
            )
            stats.append({
                'Сервер': group_name,
                'Игроки': total_players
            })
        
        return sorted(stats, key=lambda x: x['Игроки'], reverse=False)
    
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка соединения с API: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("Ошибка обработки данных API")
        return None

def display_server_stats(stats, previous_stats):
    if stats is None:
        st.warning("Данные временно недоступны")
        return previous_stats
    
    df = pd.DataFrame(stats)
    
    st.subheader("Данные о серверах")
    data_display = []
    
    current_stats = {}
    for row in reversed(stats):
        players = row['Игроки']
        server_name = row['Сервер']
        current_stats[server_name] = players
        
        # Определение стилей
        style_class = (
            "high-players" if players >= 300 else
            "medium-players" if players >= 100 else
            "very-low-players" if players < 20 else
            "low-players"
        )
        
        highlight_class = (
            "highlight-high" if (server_name in previous_stats and players >= 300 and players != previous_stats[server_name]) else
            "highlight-medium" if (server_name in previous_stats and players >= 100 and players != previous_stats[server_name]) else
            "highlight-low" if (server_name in previous_stats and 20 <= players < 100 and players != previous_stats[server_name]) else
            "highlight-very-low" if (server_name in previous_stats and players < 20 and players != previous_stats[server_name]) else
            ""
        )
        
        data_display.append(f"""
            <div class="metric-container {highlight_class} {style_class}">
                <div class="metric-label">{server_name}</div>
                <div class="metric-value">{players}</div>
            </div>
        """)
    
    st.markdown("".join(data_display), unsafe_allow_html=True)
    
    st.subheader("График распределения игроков")
    st.bar_chart(df.set_index('Сервер')['Игроки'])
    
    st.subheader("Детальная информация")
    st.dataframe(df, hide_index=True)
    
    return current_stats

def main():
    st.title("🚀 Статистика серверов SS14")

    if 'previous_stats' not in st.session_state:
        st.session_state.previous_stats = {}

    stats = get_server_stats()
    
    st.session_state.previous_stats = display_server_stats(
        stats,
        st.session_state.previous_stats
    )
    
    time.sleep(3)
    st.rerun()

if __name__ == '__main__':
    main()
