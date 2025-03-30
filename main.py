
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
        transition: background-color 0.2s ease;
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
    .very-low-players { background-color:rgba(0, 0, 0, 0.2); }
    
    /* Интенсивные версии цветов для подсветки */
    .high-players.highlight { background-color:rgba(0,255,0,0.5); }
    .medium-players.highlight { background-color:rgba(255,255,0,0.5); }
    .low-players.highlight { background-color:rgba(255,0,0,0.5); }
    .very-low-players.highlight { background-color:rgba(0,0,0,0.5); }
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
    st.title("🚀 Статистика серверов SS14")

    stats_container = st.empty()
    previous_data = {
        'players': {group: 0 for group in ['Корвакс', 'Санрайз', 'Империал', 'Спейс Сторис', 'Мёртвый Космос', 'Резерв', 'Вайт Дрим', 'СС220', 'Время Приключений']},
        'ratio': {group: 0 for group in ['Корвакс', 'Санрайз', 'Империал', 'Спейс Сторис', 'Мёртвый Космос', 'Резерв', 'Вайт Дрим', 'СС220', 'Время Приключений']},
        'rating': {group: 0 for group in ['Корвакс', 'Санрайз', 'Империал', 'Спейс Сторис', 'Мёртвый Космос', 'Резерв', 'Вайт Дрим', 'СС220', 'Время Приключений']}
    }

    while True:
        try:
            stats = get_server_stats()
            current_time = time.time()

            if stats:
                stats_container.empty()  

                with stats_container.container():
                    col1, col2, col3 = st.columns(3)

                    # Колонка с количеством игроков
                    with col1:
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

                    # Колонка с коэффициентами
                    with col2:
                        st.subheader(f"Коэф: {pd.Timestamp.now().strftime('%H:%M:%S')}")
                        for index, row in enumerate(sorted(stats, key=lambda x: x['Коэффициент'], reverse=True)):  
                            player_ratio = row['Коэффициент']
                            server_name = row['Сервер']
                            
                            ratio_style_class = (
                                "high-players" if index < 3 else
                                "medium-players" if index < 6 else
                                "low-players"
                            )
                            
                            highlight_class = 'highlight' if player_ratio != previous_data['ratio'][server_name] else ''
                            previous_data['ratio'][server_name] = player_ratio
                            
                            st.markdown(f"""
                                <div class="metric-container {ratio_style_class} {highlight_class}">
                                    <div class="metric-label">{server_name}</div>
                                    <div class="metric-value">{player_ratio:.2f}</div>
                                </div>
                            """, unsafe_allow_html=True)

                    # Колонка с рейтингом
                    with col3:
                        st.subheader(f"Рейт: {pd.Timestamp.now().strftime('%H:%M:%S')}")
                        rating_stats = [
                            {
                                'Сервер': row['Сервер'],
                                'Рейтинг': 0.7 * row['Игроки'] + 0.3 * row['Коэффициент']
                            }
                            for row in stats
                        ]
                        for index, row in enumerate(sorted(rating_stats, key=lambda x: x['Рейтинг'], reverse=True)):
                            rating = row['Рейтинг']
                            server_name = row['Сервер']
                            
                            rating_style_class = (
                                "high-players" if index < 3 else
                                "medium-players" if index < 6 else
                                "low-players"
                            )
                            
                            highlight_class = 'highlight' if rating != previous_data['rating'][server_name] else ''
                            previous_data['rating'][server_name] = rating
                            
                            st.markdown(f"""
                                <div class="metric-container {rating_style_class} {highlight_class}">
                                    <div class="metric-label">{server_name}</div>
                                    <div class="metric-value">{rating:.2f}</div>
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
