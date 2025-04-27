import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="SS14 Статистика серверов", page_icon="🚀", layout="centered")

st.markdown("""<style>
    .metric-container {
        padding:5px;
        border-radius:5px;
        margin:1px 0;
        width:320px;
        min-height:35px;
        display:flex;
        justify-content:space-between;
        align-items:center;
        transition: background-color 0.2s ease;
        margin-left:auto;
        margin-right:auto;
    }
    .metric-label {
        font-size:12px;
        font-weight:bold;
        margin-right:10px;
        white-space:nowrap;
    }
    .metric-value {
        font-size:16px;
        font-weight:bold;
        margin-left:10px;
        white-space:nowrap;
    }
    .high-players { background-color:rgba(0,255,0,0.2); }
    .medium-players { background-color:rgba(255,255,0,0.2); }
    .low-players { background-color:rgba(255,0,0,0.2); }
    .very-low-players { background-color:rgba(0, 0, 0, 0.2); }
    .high-players.highlight { background-color:rgba(0,255,0,0.5); }
    .medium-players.highlight { background-color:rgba(255,255,0,0.5); }
    .low-players.highlight { background-color:rgba(255,0,0,0.5); }
    .very-low-players.highlight { background-color:rgba(0,0,0,0.5); }
    .purple-server { background-color: rgba(128, 0, 128, 0.3); }
    .purple-server.highlight { background-color: rgba(128, 0, 128, 0.6); }
</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=1.5)
def get_server_stats():
    try:
        response = requests.get('https://hub.spacestation14.com/api/servers', timeout=1.5)
        if response.status_code == 200:
            json_data = response.json()
            
            server_groups = {
                'Корвакс': ['Corvax'], 
                'Санрайз': ['РЫБЬЯ','LUST','SUNRISE','FIRE'],
                'Империал': ['Imperial'], 
                'Спейс Сторис': ['Stories'],
                'Мёртвый Космос': ['МЁРТВЫЙ', 'Spellward'], 
                'Резерв': ['Reserve'],
                'Парсек': ['Giedi'], 
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
                stats.append({'Сервер': group_name, 'Игроки': total_players})  
            
            return sorted(stats, key=lambda x: x['Игроки'], reverse=False)
    except:
        pass
    return None

def get_corvaxcraft_online():
    try:
        url = 'https://mcstatus.snowdev.com.br/api/query/v3/203.31.40.127'
        response = requests.get(url, timeout=1.5)
        if response.status_code == 200:
            data = response.json()
            return data.get("players_online", 0)
    except:
        pass
    return None

def main():
    st.title("🚀 Статистика серверов SS14")

    stats_container = st.empty()
    previous_data = {
        'players': {group: 0 for group in ['Корвакс', 'Санрайз', 'Империал', 'Спейс Сторис', 'Мёртвый Космос', 'Резерв', 'Парсек', 'СС220', 'Время Приключений']}
    }

    corvaxcraft_online = None
    last_corvaxcraft_update = 0

    while True:
        try:
            stats = get_server_stats()
            current_time = time.time()

            if current_time - last_corvaxcraft_update >= 5:
                corvaxcraft_online = get_corvaxcraft_online()
                last_corvaxcraft_update = current_time

            if stats:
                stats_container.empty()  

                with stats_container.container():
                    st.subheader(f"Сумма: {pd.Timestamp.now().strftime('%H:%M:%S')}")
                    for index, row in enumerate(reversed(stats)):
                        players = row['Игроки']
                        server_name = row['Сервер']
                        
                        style_class = (
                            "high-players" if index < 3 else
                            "medium-players" if index < 6 else
                            "low-players"
                        )
                        
                        highlight_class = 'highlight' if players != previous_data['players'][server_name] else ''
                        previous_data['players'][server_name] = players
                        
                        st.markdown(f"""
                            <div class="metric-container {style_class} {highlight_class}">
                                <div class="metric-label">{server_name}</div>
                                <div class="metric-value">{players}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    if corvaxcraft_online is not None:
                        st.markdown(f"""
                            <div class="metric-container purple-server highlight">
                                <div class="metric-label">CorvaxCraft</div>
                                <div class="metric-value">{corvaxcraft_online}</div>
                            </div>
                        """, unsafe_allow_html=True)

        except Exception as e:
            if "SessionInfo" in str(e):
                time.sleep(1)
                continue
            raise

        time.sleep(1.5)

if __name__ == '__main__':
    main()
