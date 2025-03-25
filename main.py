import streamlit as st
import requests
import json
import pandas as pd
import time

st.set_page_config(page_title="SS14 Статистика серверов", page_icon="🚀", layout="wide")

st.markdown("""<style>
    .metric-container {padding:5px;border-radius:5px;margin:1px 0;width:100%;min-height:35px;display:flex;justify-content:space-between;align-items:center;}
    .metric-label{font-size:12px;font-weight:bold;}
    .metric-value{font-size:16px;font-weight:bold;}
    .high-players{background-color:rgba(0,255,0,0.2);}
    .medium-players{background-color:rgba(255,255,0,0.2);}
    .low-players{background-color:rgba(255,0,0,0.2);}
    .very-low-players{background-color:black;}
    .highlight-high{background-color:rgba(0,255,0,0.5);}
    .highlight-medium{background-color:rgba(255,255,0,0.5);}
    .highlight-low{background-color:rgba(255,0,0,0.5);}
    .highlight-very-low{background-color:rgba(128,128,128,0.5);}
</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=10)
def get_server_stats():
    try:
        response = requests.get('https://hub.spacestation14.com/api/servers', timeout=5)
        json_data = response.json()
        
        server_groups = {
            'Корвакс': ['Corvax'], 'Санрайз': ['РЫБЬЯ','LUST','SUNRISE','FIRE'],
            'Империал': ['Imperial'], 'Спейс Сторис': ['Stories'],
            'Мёртвый Космос': ['МЁРТВЫЙ'], 'Резерв': ['Reserve'],
            'Виктория': ['Victoria'], 'СС220': ['SS220'],
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
            stats.append({'Сервер': group_name, 'Игроки': total_players})
        
        return sorted(stats, key=lambda x: x['Игроки'], reverse=False)
    
    except:
        return None

def main():
    st.title("🚀 Статистика серверов SS14")

    if 'previous_stats' not in st.session_state:
        st.session_state.previous_stats = {}

    stats_container = st.empty()
    chart_container = st.empty()
    table_container = st.empty()

    while True:
        stats = get_server_stats()

        with stats_container.container():
            if stats:
                current_stats = {}
                st.subheader("Данные о серверах")
                for row in reversed(stats):
                    players = row['Игроки']
                    server_name = row['Сервер']
                    current_stats[server_name] = players
                    
                    style_class = (
                        "high-players" if players >= 300 else
                        "medium-players" if players >= 100 else
                        "very-low-players" if players < 20 else
                        "low-players"
                    )
                    
                    highlight_class = (
                        "highlight-high" if (server_name in st.session_state.previous_stats and players >= 300 and players != st.session_state.previous_stats[server_name]) else
                        "highlight-medium" if (server_name in st.session_state.previous_stats and players >= 100 and players != st.session_state.previous_stats[server_name]) else
                        "highlight-low" if (server_name in st.session_state.previous_stats and 20 <= players < 100 and players != st.session_state.previous_stats[server_name]) else
                        "highlight-very-low" if (server_name in st.session_state.previous_stats and players < 20 and players != st.session_state.previous_stats[server_name]) else
                        ""
                    )
                    
                    st.markdown(f"""
                        <div class="metric-container {highlight_class} {style_class}">
                            <div class="metric-label">{server_name}</div>
                            <div class="metric-value">{players}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.session_state.previous_stats = current_stats

        with chart_container.container():
            if stats:
                df = pd.DataFrame(stats)
                st.subheader("График распределения игроков")
                st.bar_chart(df.set_index('Сервер')['Игроки'])

        with table_container.container():
            if stats:
                st.subheader("Детальная информация")
                st.dataframe(pd.DataFrame(stats), hide_index=True)

        time.sleep(3)

if __name__ == '__main__':
    main()
