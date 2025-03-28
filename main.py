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
        width:100%;
        min-height:35px;
        display:flex;
        justify-content:space-between;
        align-items:center;
        transition: all 0.3s ease;
    }
    .metric-label {
        font-size:12px;
        font-weight:bold;
    }
    .metric-value {
        font-size:16px;
        font-weight:bold;
    }
    .high-players { background-color:rgba(0,255,0,0.2); }
    .medium-players { background-color:rgba(255,255,0,0.2); }
    .low-players { background-color:rgba(255,0,0,0.2); }
    .very-low-players { background-color:black; }
    .highlight-high { background-color:rgba(0,255,0,0.5); }
    .highlight-medium { background-color:rgba(255,255,0,0.5); }
    .highlight-low { background-color:rgba(255,0,0,0.5); }
    .highlight-very-low { background-color:rgba(128,128,128,0.5); }
    .table-container {
        display: flex;
        justify-content: space-between;
    }
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
                'Мёртвый Космос': ['МЁРТВЫЙ'], 
                'Резерв': ['Reserve'],
                'Вайт Дрим': ['Giedi'], 
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
                server_count = len([server for server in json_data if any(keyword in server['statusData']['name'] for keyword in keywords)])
                player_ratio = total_players / server_count if server_count > 0 else 0 
                stats.append({'Сервер': group_name, 'Игроки': total_players, 'Коэффициент': player_ratio})  
            
            return sorted(stats, key=lambda x: x['Игроки'], reverse=False)
    except:
        pass
    return None

def main():
    if 'previous_stats' not in st.session_state:
        st.session_state.previous_stats = {}

    st.title("🚀 Статистика серверов SS14")


    stats_container = st.empty()

    while True:
        try:
            stats = get_server_stats()
            current_time = time.time()

            if stats:
                current_stats = {}
                stats_container.empty()  

                # Создаем контейнер для двух таблиц
                with stats_container.container():
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader(f"Данные о серверах (Суммарный онлайн): {pd.Timestamp.now().strftime('%H:%M:%S')}")
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
                            
                            st.markdown(f"""
                                <div class="metric-container {style_class}">
                                    <div class="metric-label">{server_name}</div>
                                    <div class="metric-value">{players}</div>
                                </div>
                            """, unsafe_allow_html=True)

                    with col2:
                        st.subheader(f"Данные о серверах (Коэффициенты): {pd.Timestamp.now().strftime('%H:%M:%S')}")
                        for row in sorted(stats, key=lambda x: x['Коэффициент'], reverse=True):  
                            player_ratio = row['Коэффициент']
                            server_name = row['Сервер']
                            
                        
                            ratio_style_class = (
                                "high-players" if player_ratio >= 60 else
                                "medium-players" if player_ratio >= 40 else
                                "very-low-players" if player_ratio < 20 else
                                "low-players"
                            )
                            
                            st.markdown(f"""
                                <div class="metric-container {ratio_style_class}">
                                    <div class="metric-label">{server_name}</div>
                                    <div class="metric-value">{player_ratio:.2f}</div>
                                </div>
                            """, unsafe_allow_html=True)

                st.session_state.previous_stats = current_stats

        except Exception as e:
            if "SessionInfo" in str(e):
                time.sleep(1)
                continue
            raise

        time.sleep(1.5)

if __name__ == '__main__':
    main()
