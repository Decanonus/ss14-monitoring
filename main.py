import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import pytz

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

@st.cache_data(ttl=10) 
def get_server_stats():
    url = 'https://hub.spacestation14.com/api/servers'
    try:
        r = requests.get(url)
        jsonn = json.loads(r.text)
        
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
                servers['statusData']['players']
                for servers in jsonn
                for keyword in keywords
                if keyword in servers['statusData']['name']
            )
            stats.append({
                'Сервер': group_name,
                'Игроки': total_players
            })
        
        return sorted(stats, key=lambda x: x['Игроки'], reverse=False)
    except Exception as e:
        st.error(f"Ошибка при получении данных: {e}")
        return []

def main():
    st.title("🚀 Статистика серверов SS14")
    
    st.autorefresh(interval=3000, key="auto_refresh")  

    stats = get_server_stats()
    previous_stats = st.session_state.get("previous_stats", {}) 
    
    if stats:
        df = pd.DataFrame(stats)
        
        st.subheader("Данные о серверах")
        data_display = [] 
        
        for row in reversed(stats):
            players = row['Игроки']
            server_name = row['Сервер']
            style_class = ""
            highlight_class = ""
            
            if server_name in previous_stats:
                if previous_stats[server_name] != players:
                    if players >= 300:
                        highlight_class = "highlight-high"
                    elif players >= 100:
                        highlight_class = "highlight-medium"
                    elif players < 20:
                        highlight_class = "highlight-very-low"
                    else:
                        highlight_class = "highlight-low"
            
            # Обновляем предыдущие значения
            previous_stats[server_name] = players
            
            # Определяем стиль в зависимости от количества игроков
            if style_class == "":
                if players >= 300:
                    style_class = "high-players"
                elif players >= 100:
                    style_class = "medium-players"
                elif players < 20:
                    style_class = "very-low-players"
                else:
                    style_class = "low-players"
            
            data_display.append(f"""
                <div class="metric-container {highlight_class} {style_class}">
                    <div class="metric-label">{server_name}</div>
                    <div class="metric-value">{players}</div>
                </div>
            """)
        
        st.markdown("".join(data_display), unsafe_allow_html=True)
        
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
    
    st.session_state.previous_stats = previous_stats

if __name__ == '__main__':
    main()
