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
    .stats-card {
        padding: 15px;
        border-radius: 10px;
        margin: 5px;
        transition: background-color 0.2s ease;
    }
    .adult-stats { background-color: rgba(255,192,203,0.2); }
    .normal-stats { background-color: rgba(144,238,144,0.2); }
    .adult-stats.highlight { background-color: rgba(255,192,203,0.5); }
    .normal-stats.highlight { background-color: rgba(144,238,144,0.5); }
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
                'Парсек': ['Parsec'], 
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

@st.cache_data(ttl=1.5)
def get_adult_servers_stats():
    try:
        response = requests.get('https://hub.spacestation14.com/api/servers', timeout=1.5)
        if response.status_code == 200:
            request = response.json()
            
            def is_18plus(server):
                status = server.get('statusData', {})
                # Проверяем tags, name и inferredTags
                tags = status.get('tags', [])
                inferred = status.get('inferredTags', [])
                name = status.get('name', '')
                return (
                    '18+' in tags or
                    '18+' in inferred or
                    '18+' in name
                )

            servers_18plus = [server for server in request if is_18plus(server)]
            servers_non_18plus = [server for server in request if not is_18plus(server)]

            players_18plus = sum(server['statusData']['players'] for server in servers_18plus)
            players_non_18plus = sum(server['statusData']['players'] for server in servers_non_18plus)

            active_servers_18plus = sum(1 for server in servers_18plus 
                                      if server['statusData']['players'] > 0)
            active_servers_non_18plus = sum(1 for server in servers_non_18plus 
                                          if server['statusData']['players'] > 0)

            avg_players_18plus = (players_18plus / active_servers_18plus 
                                if active_servers_18plus > 0 else 0)
            avg_players_non_18plus = (players_non_18plus / active_servers_non_18plus 
                                    if active_servers_non_18plus > 0 else 0)

            return {
                'players_18plus': players_18plus,
                'players_non_18plus': players_non_18plus,
                'active_servers_18plus': active_servers_18plus,
                'active_servers_non_18plus': active_servers_non_18plus,
                'avg_players_18plus': round(avg_players_18plus, 2),
                'avg_players_non_18plus': round(avg_players_non_18plus, 2)
            }
    except:
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

    main_container = st.container()
    
    with main_container:
        header = st.empty()
        servers_list = st.empty()
        separator = st.empty()
        age_stats_header = st.empty()
        age_stats_columns = st.columns(2)
        adult_stats_card = age_stats_columns[0].empty()
        normal_stats_card = age_stats_columns[1].empty()

    # Расширяем словарь для хранения предыдущих значений
    previous_data = {
        'players': {group: 0 for group in ['Корвакс', 'Санрайз', 'Империал', 'Спейс Сторис', 
                                         'Мёртвый Космос', 'Резерв', 'Парсек', 'СС220', 
                                         'Время Приключений', 'Корвакс Крафт']},
        'adult_stats': {
            'players_18plus': 0,
            'players_non_18plus': 0,
            'active_servers_18plus': 0,
            'active_servers_non_18plus': 0,
            'avg_players_18plus': 0,
            'avg_players_non_18plus': 0
        }
    }

    corvaxcraft_online = None
    last_corvaxcraft_update = 0

    while True:
        try:
            stats = get_server_stats()
            adult_stats = get_adult_servers_stats()
            current_time = time.time()

            if current_time - last_corvaxcraft_update >= 5:
                corvaxcraft_online = get_corvaxcraft_online()
                last_corvaxcraft_update = current_time

            if stats:
                header.subheader(f"Сумма: {pd.Timestamp.now().strftime('%H:%M:%S')}")
                
                all_servers = list(reversed(stats))
                if corvaxcraft_online is not None:
                    all_servers.append({
                        'Сервер': 'Корвакс Крафт',
                        'Игроки': corvaxcraft_online
                    })
                all_servers.sort(key=lambda x: x['Игроки'], reverse=True)
                
                servers_html = ""
                for index, row in enumerate(all_servers):
                    players = row['Игроки']
                    server_name = row['Сервер']
                    
                    is_corvaxcraft = server_name == 'Корвакс Крафт'
                    
                    style_class = (
                        "purple-server" if is_corvaxcraft else
                        "high-players" if index < 3 else
                        "medium-players" if index < 6 else
                        "low-players"
                    )
                    
                    highlight_class = 'highlight' if players != previous_data['players'][server_name] else ''
                    previous_data['players'].setdefault(server_name, 0)
                    previous_data['players'][server_name] = players
                    
                    servers_html += f"""
                        <div class="metric-container {style_class} {highlight_class}">
                            <div class="metric-label">{server_name}</div>
                            <div class="metric-value">{players}</div>
                        </div>
                    """
                
                servers_list.markdown(servers_html, unsafe_allow_html=True)

                if adult_stats:
                    separator.markdown("---")
                    age_stats_header.subheader("Статистика 18+ и не 18+ серверов")
                    
                    # Проверяем изменения для 18+ статистики
                    adult_highlight = any(
                        adult_stats[key] != previous_data['adult_stats'][key]
                        for key in ['players_18plus', 'active_servers_18plus', 'avg_players_18plus']
                    )
                    
                    # Проверяем изменения для не 18+ статистики
                    normal_highlight = any(
                        adult_stats[key] != previous_data['adult_stats'][key]
                        for key in ['players_non_18plus', 'active_servers_non_18plus', 'avg_players_non_18plus']
                    )
                    
                    # Обновляем предыдущие значения
                    previous_data['adult_stats'].update(adult_stats)
                    
                    adult_stats_card.markdown(f"""
                        <div class="stats-card adult-stats {'highlight' if adult_highlight else ''}">
                            <h4>Серверы 18+</h4>
                            <p>
                                🎮 Игроков: {adult_stats['players_18plus']}<br>
                                🖥️ Активных серверов: {adult_stats['active_servers_18plus']}<br>
                                📊 Среднее игроков на сервере: ~{adult_stats['avg_players_18plus']}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    normal_stats_card.markdown(f"""
                        <div class="stats-card normal-stats {'highlight' if normal_highlight else ''}">
                            <h4>Серверы не 18+</h4>
                            <p>
                                🎮 Игроков: {adult_stats['players_non_18plus']}<br>
                                🖥️ Активных серверов: {adult_stats['active_servers_non_18plus']}<br>
                                📊 Среднее игроков на сервере: ~{adult_stats['avg_players_non_18plus']}
                            </p>
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
