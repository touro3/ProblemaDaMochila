import streamlit as st
import time
import random
# Importa as funções e classes do seu backend
from mochila_ga import Item, algoritmo_genetico_mochila_iterativo, calcular_detalhes_individuo

st.set_page_config(layout="wide", page_title="Problema da Mochila Animado")

# --- Dados Mock de Itens (você pode expandir ou permitir entrada do usuário) ---
DEFAULT_ITEMS_DATA = [
    ("Lanterna", 2, 15), ("Saco de Dormir", 5, 30), ("Comida Enlatada", 10, 50),
    ("Corda", 3, 20), ("Mapa", 1, 10), ("Bússola", 1, 15),
    ("Kit Primeiros Socorros", 4, 25), ("Cantil", 2, 20), ("Faca", 1, 18),
    ("Repelente", 1, 12), ("Câmera", 3, 40), ("Livro", 2, 5),
    ("Barraca", 15, 70), ("Fogareiro", 6, 35), ("Panelas", 4, 22),
    ("Rádio Solar", 3, 28), ("Bateria Extra", 2, 22), ("Chocolate", 1, 16)
]
DEFAULT_CAPACITY = 35

# Mapeamento de nomes de itens para emojis para a animação
ITEM_EMOJIS = {
    "Lanterna": "🔦", "Saco de Dormir": "🛌", "Comida Enlatada": "🥫",
    "Corda": "🧶", "Mapa": "🗺️", "Bússola": "🧭",
    "Kit Primeiros Socorros": "🩹", "Cantil": "🥛", "Faca": "🔪",
    "Repelente": "🦟", "Câmera": "📸", "Livro": "📚",
    "Barraca": "⛺", "Fogareiro": "🔥", "Panelas": "🍳",
    "Rádio Solar": "📻", "Bateria Extra": "🔋", "Chocolate": "🍫",
}

# --- Estilos CSS Personalizados para Animação e Beleza ---
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6; /* Fundo mais suave */
    }
    .main-header {
        font-size: 3em;
        color: #2e86c1; /* Cor primária */
        text-align: center;
        margin-bottom: 30px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    /* O contêiner principal da mochila com alça e emojis */
    .animated-knapsack-area {
        position: relative; /* Base para o posicionamento absoluto dos emojis */
        width: 300px; /* Largura da mochila */
        height: 250px; /* Altura total incluindo espaço para a alça e queda */
        margin: 0 auto 30px; /* Centraliza e adiciona margem inferior */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end; /* A mochila começa na parte inferior */
    }

    .knapsack-base {
        width: 300px;
        height: 150px;
        background-color: #8B4513; /* Marrom escuro */
        border: 5px solid #5A2D0C;
        border-radius: 10px;
        position: relative; /* Para os itens internos */
        overflow: hidden; /* Garante que os itens não ultrapassem a borda */
        display: flex;
        flex-wrap: wrap; /* Para os itens se ajustarem */
        align-content: flex-end; /* Itens "sobem" de baixo para cima */
        padding: 10px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        z-index: 1; /* Fica acima da alça virtual */

        /* --- CSS para a Alça da Mochila usando pseudo-elementos --- */
        /* Alça central superior */
        &::before {
            content: '';
            position: absolute;
            top: -50px; /* Posição acima da mochila */
            left: 50%;
            transform: translateX(-50%);
            width: 120px; /* Largura da alça */
            height: 80px; /* Altura da alça */
            border: 5px solid #5A2D0C; /* Cor da borda */
            border-bottom: none; /* Sem borda inferior */
            border-radius: 60px 60px 0 0; /* Arredonda a parte superior */
            z-index: 0; /* **Fica ABAIXO do knapsack-base** */
        }
    }

    /* Estilo para os emojis caindo */
    .falling-emoji {
        position: absolute;
        font-size: 3.5em; /* Tamanho do emoji */
        left: 50%;
        transform: translateX(-50%);
        opacity: 0; /* Começa invisível */
        /* Transição rápida, quase instantânea, pois será controlada por renderização do Streamlit */
        transition: top 0.1s ease-out, opacity 0.1s ease-out; /* Muito rápido */
        z-index: 100; /* **MUITO MAIOR Z-INDEX** para garantir que o emoji esteja na frente de tudo */
        pointer-events: none; /* Não bloqueia cliques em outros elementos */
        /* Posição inicial: relativa ao .animated-knapsack-area, começa bem no topo */
        top: 0px; 
    }
    .falling-emoji.active {
        opacity: 1;
        top: 0px; /* Mantém na posição inicial para iniciar a transição */
    }
    .falling-emoji.fall {
        /* Posição final: o fundo do .animated-knapsack-area menos a altura da mochila */
        top: 220px; /* Cai dentro da mochila */
        opacity: 0; /* Desaparece ao "entrar" */
    }

    /* Estilo para os itens dentro da mochila (caixas laranjas) */
    .knapsack-item {
        background-color: #f39c12; /* Laranja */
        color: white;
        border-radius: 5px;
        padding: 5px 10px;
        margin: 5px;
        font-size: 0.8em;
        font-weight: bold;
        text-align: center;
        opacity: 0; /* Começa invisível para a animação */
        transform: translateY(20px); /* Levemente abaixo para subir */
        transition: opacity 0.3s ease-out, transform 0.3s ease-out; /* Transição suave */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        cursor: help;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 60px;
        height: 30px;
    }
    .knapsack-item.visible {
        opacity: 1;
        transform: translateY(0);
    }
    .item-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease-in-out;
    }
    .item-card:hover {
        transform: translateY(-5px);
    }
    .item-card h5 {
        color: #34495e;
        margin-bottom: 5px;
    }
    .item-card p {
        font-size: 0.9em;
        color: #7f8c8d;
    }
    .progress-info {
        font-size: 1.2em;
        font-weight: bold;
        color: #3498db;
        text-align: center;
        margin-top: 20px;
    }
    .stMarkdown h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🎒Problema da Mochila com AG 🧬</h1>', unsafe_allow_html=True)

st.write("""
Este aplicativo visualiza o problema da mochila sendo resolvido por um Algoritmo Genético.
Veja como a seleção de itens evolui ao longo das gerações para encontrar a melhor combinação!
""")

# --- Sidebar para Controles e Parâmetros ---
st.sidebar.header("⚙️ Configurações do Algoritmo Genético")
capacidade_mochila = st.sidebar.number_input("Capacidade Máxima da Mochila:", min_value=1, value=DEFAULT_CAPACITY, step=1)

# Opção para o usuário selecionar itens ou adicionar novos
st.sidebar.subheader("Seleção de Itens")
if 'custom_items' not in st.session_state:
    st.session_state.custom_items = []

selected_default_items = []
st.sidebar.markdown("---")
st.sidebar.markdown("### Itens Pré-definidos:")
for item_data in DEFAULT_ITEMS_DATA:
    name, weight, value = item_data
    if st.sidebar.checkbox(f"{name} (P:{weight}kg, V:${value})", value=True, key=f"default_item_{name}"):
        selected_default_items.append(item_data)

st.sidebar.markdown("---")
st.sidebar.markdown("### Adicionar Item Personalizado:")
with st.sidebar.expander("Clique para adicionar um novo item"):
    item_name = st.text_input("Nome do Item:", key="new_item_name_input")
    item_weight = st.number_input("Peso do Item:", min_value=1, value=10, key="new_item_weight_input")
    item_value = st.number_input("Valor do Item:", min_value=1, value=50, key="new_item_value_input")
    if st.button("Adicionar Item", key="add_item_button"):
        if item_name:
            st.session_state.custom_items.append((item_name, item_weight, item_value))
            st.sidebar.success(f"Item '{item_name}' adicionado!")
            st.session_state.new_item_name_input = "" # Limpar campo
            st.session_state.new_item_weight_input = 10
            st.session_state.new_item_value_input = 50
            st.experimental_rerun()
        else:
            st.sidebar.warning("Por favor, insira um nome para o item.")

if st.session_state.custom_items:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Seus Itens Personalizados:")
    items_to_remove = []
    for i, item_data in enumerate(st.session_state.custom_items):
        name, weight, value = item_data
        col_name, col_remove = st.sidebar.columns([0.7, 0.3])
        col_name.write(f"- {name} (P:{weight}kg, V:${value})")
        if col_remove.button("Remover", key=f"remove_item_{i}"):
            items_to_remove.append(i)
    
    for i in sorted(items_to_remove, reverse=True):
        del st.session_state.custom_items[i]
        st.experimental_rerun()

items_data = selected_default_items + st.session_state.custom_items
if not items_data:
    st.warning("Nenhum item selecionado ou adicionado! Por favor, adicione itens para iniciar a simulação.")


# Parâmetros do AG
st.sidebar.markdown("---")
st.sidebar.header("⚡ Parâmetros do Algoritmo Genético")
tam_populacao = st.sidebar.slider("Tamanho da População:", 10, 200, 100)
num_geracoes = st.sidebar.slider("Número de Gerações:", 50, 500, 150)
taxa_cruzamento = st.sidebar.slider("Taxa de Cruzamento:", 0.0, 1.0, 0.9, 0.05)
taxa_mutacao = st.sidebar.slider("Taxa de Mutação:", 0.0, 0.1, 0.03, 0.005)
contagem_elitismo = st.sidebar.slider("Elitismo (Melhores Indivíduos Preservados):", 0, 10, 3)
tam_torneio = st.sidebar.slider("Tamanho do Torneio (Seleção):", 2, 10, 5)
seed_val = st.sidebar.number_input("Seed (para reprodutibilidade):", value=42)
animation_speed = st.sidebar.slider("Velocidade da Animação (segundos/geração):", 0.05, 2.0, 0.2, 0.05)

st.sidebar.markdown("---")
st.sidebar.info("Ajuste os parâmetros e clique em 'Iniciar Simulação' para ver a mágica acontecer!")


# --- Colunas para Layout Principal ---
col_mochila, col_status, col_graficos = st.columns([1.5, 1, 1.5])

with col_mochila:
    st.subheader("👜 Mochila Atual")
    mochila_display_placeholder = st.empty() # Placeholder para a área animada da mochila
    item_details_placeholder = st.empty() # Placeholder para detalhes dos itens na mochila

with col_status:
    st.subheader("📊 Progresso do Algoritmo")
    generation_info = st.empty()
    best_value_info = st.empty()
    current_weight_info = st.empty()
    best_overall_info = st.empty()
    progress_bar_placeholder = st.empty()

with col_graficos:
    st.subheader("📈 Evolução do Fitness")
    chart_data_placeholder = st.empty()


# --- Botão de Iniciar Simulação ---
st.markdown("---")
if st.button("🚀 Iniciar Simulação"):
    if not items_data:
        st.error("Por favor, selecione ou adicione pelo menos um item antes de iniciar a simulação.")
        st.stop()

    st.balloons()

    st.write("Iniciando o Algoritmo Genético...")

    historico_fitness_geral_para_grafico = []

    historico_solucoes = algoritmo_genetico_mochila_iterativo(
        items_data=items_data,
        capacidade_maxima=capacidade_mochila,
        tam_populacao=tam_populacao,
        num_geracoes=num_geracoes,
        taxa_mutacao=taxa_mutacao,
        taxa_cruzamento=taxa_cruzamento,
        contagem_elitismo=contagem_elitismo,
        tam_torneio=tam_torneio,
        seed=seed_val
    )

    items_obj_list = [Item(name, weight, value) for name, weight, value in items_data]

    last_best_solucao = None

    for geracao_idx, (solucao, valor, peso, fitness) in enumerate(historico_solucoes):
        # Atualiza a barra de progresso
        progress_bar_placeholder.progress((geracao_idx + 1) / num_geracoes)

        generation_info.markdown(f"<p class='progress-info'>Geração: <strong>{geracao_idx + 1}/{num_geracoes}</strong></p>", unsafe_allow_html=True)
        best_value_info.markdown(f"<p class='progress-info'>Valor Atual: <strong>${valor}</strong></p>", unsafe_allow_html=True)
        current_weight_info.markdown(f"<p class='progress-info'>Peso Atual: <strong>{peso}/{capacidade_mochila} kg</strong></p>", unsafe_allow_html=True)
        best_overall_info.markdown(f"<p class='progress-info'>Melhor Valor Geral: <strong>${historico_solucoes[geracao_idx][3]}</strong></p>", unsafe_allow_html=True)

        items_to_animate_this_generation = []
        if last_best_solucao is not None and solucao is not None:
            current_items_in_sol = set([i for i, gene in enumerate(solucao) if gene == 1])
            prev_items_in_sol = set([i for i, gene in enumerate(last_best_solucao) if gene == 1])

            newly_added_indices = current_items_in_sol - prev_items_in_sol
            
            for idx in newly_added_indices:
                if idx < len(items_obj_list):
                    items_to_animate_this_generation.append(items_obj_list[idx])
        
        last_best_solucao = solucao # Atualiza para a próxima iteração

        # --- Visualização da Mochila com Animação de Queda dos Emojis (Um de Cada Vez) ---
        # A mochila e os itens internos serão atualizados *dentro* deste loop
        
        # O estado atual dos itens na mochila ANTES de qualquer nova animação de queda
        current_items_in_knapsack_display = []
        if solucao:
            for i, gene in enumerate(solucao):
                if i < len(items_obj_list) and gene == 1 and items_obj_list[i] not in items_to_animate_this_generation:
                    current_items_in_knapsack_display.append(items_obj_list[i])

        # Anima a queda de cada novo item sequencialmente
        if items_to_animate_this_generation:
            for item_animar in items_to_animate_this_generation:
                emoji = ITEM_EMOJIS.get(item_animar.name, "❓")
                
                # Renderiza a mochila e a alça e os itens JÁ EXISTENTES + o emoji caindo
                with mochila_display_placeholder.container():
                    st.markdown('<div class="animated-knapsack-area">', unsafe_allow_html=True)
                    st.markdown('<div class="knapsack-base" id="mochila-base">', unsafe_allow_html=True)
                    
                    # Renderiza os itens que JÁ ESTAVAM na mochila (para que o emoji caia por cima)
                    for item_existente in current_items_in_knapsack_display:
                        st.markdown(
                            f"""
                            <div class="knapsack-item visible" title="{item_existente.name} (P:{item_existente.weight}, V:${item_existente.value})">
                                {item_existente.name}<br>({item_existente.weight}kg, ${item_existente.value})
                            </div>
                            """, unsafe_allow_html=True
                        )
                    
                    # O emoji caindo por cima da mochila atual
                    st.markdown(
                        f"""
                        <div class="falling-emoji active">
                            {emoji}
                        </div>
                        """, unsafe_allow_html=True
                    )
                    st.markdown('</div></div>', unsafe_allow_html=True) # Fecha knapsack-base e animated-knapsack-area
                
                # Pequeno delay para garantir que o Streamlit renderize o emoji antes da queda
                time.sleep(0.05) 
                
                # Inicia a animação de queda via JavaScript para ESTE emoji
                # Não haverá time.sleep aqui para não bloquear a geração.
                st.markdown(
                    "<script>"
                    "var emojiEl = document.querySelector('.falling-emoji.active');"
                    "if (emojiEl) { emojiEl.classList.remove('active'); emojiEl.classList.add('fall'); }"
                    "</script>", unsafe_allow_html=True
                )
                
                # Adiciona uma pequena pausa para que o olho humano perceba a transição
                # Mas não tão longa a ponto de afetar a velocidade da geração significativamente
                time.sleep(0.2) # Ajuste este valor (ex: 0.1s a 0.5s) para o "flash" da queda

            # Após todas as animações de "queda" (flash) para esta geração,
            # redesenha a mochila com todos os itens, incluindo os que acabaram de "cair".
            # Isso garante que as caixas laranjas apareçam sincronizadas.
            with mochila_display_placeholder.container():
                st.markdown('<div class="animated-knapsack-area">', unsafe_allow_html=True)
                st.markdown('<div class="knapsack-base" id="mochila-base">', unsafe_allow_html=True)
                
                itens_selecionados_final_render = []
                if solucao:
                    for i, gene in enumerate(solucao):
                        if i < len(items_obj_list) and gene == 1:
                            item = items_obj_list[i]
                            st.markdown(
                                f"""
                                <div class="knapsack-item visible" title="{item.name} (P:{item.weight}, V:${item.value})">
                                    {item.name}<br>({item.weight}kg, ${item.value})
                                </div>
                                """, unsafe_allow_html=True
                            )
                            itens_selecionados_final_render.append(item)
                st.markdown('</div></div>', unsafe_allow_html=True)
        else:
            # Se não houve itens para animar, apenas redesenha a mochila normalmente
            with mochila_display_placeholder.container():
                st.markdown('<div class="animated-knapsack-area">', unsafe_allow_html=True)
                st.markdown('<div class="knapsack-base" id="mochila-base">', unsafe_allow_html=True)
                
                itens_selecionados_final_render = []
                if solucao:
                    for i, gene in enumerate(solucao):
                        if i < len(items_obj_list) and gene == 1:
                            item = items_obj_list[i]
                            st.markdown(
                                f"""
                                <div class="knapsack-item visible" title="{item.name} (P:{item.weight}, V:${item.value})">
                                    {item.name}<br>({item.weight}kg, ${item.value})
                                </div>
                                """, unsafe_allow_html=True
                            )
                            itens_selecionados_final_render.append(item)
                st.markdown('</div></div>', unsafe_allow_html=True)


        # Detalhes dos itens na mochila (fora da área animada)
        with item_details_placeholder.container():
            st.subheader("Itens Selecionados na Melhor Solução:")
            if itens_selecionados_final_render:
                for item in itens_selecionados_final_render:
                    st.markdown(f"""
                        <div class="item-card">
                            <h5>{item.name}</h5>
                            <p>Peso: {item.weight} kg | Valor: ${item.value}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum item válido selecionado ainda nesta solução.")


        # Atualizar gráfico de evolução do fitness
        historico_fitness_geral_para_grafico.append(historico_solucoes[geracao_idx][3])
        chart_data_placeholder.line_chart(historico_fitness_geral_para_grafico)


        time.sleep(animation_speed) # Controla a velocidade da animação da GERAÇÃO

    st.success("Simulação Completa! 🎉")
    st.snow()

    st.markdown("---")
    st.subheader("✅ Melhor Solução Final Encontrada:")
    if historico_solucoes:
        final_solucao, final_valor, final_peso, final_fitness = historico_solucoes[-1]
        if final_solucao:
            final_itens_selecionados_obj = [items_obj_list[i] for i, gene in enumerate(final_solucao) if gene == 1 and i < len(items_obj_list)]
            final_itens_selecionados_nomes = [item.name for item in final_itens_selecionados_obj]

            st.write(f"**Cromossomo:** {final_solucao}")
            st.write(f"**Itens na Mochila:** {', '.join(final_itens_selecionados_nomes)}")
            st.write(f"**Valor Total:** ${final_valor}")
            st.write(f"**Peso Total:** {final_peso}/{capacidade_mochila} kg")
            st.write(f"**Fitness Final:** {final_fitness}")
        else:
            st.warning("Nenhuma solução válida foi encontrada.")
    else:
        st.warning("Não foi possível encontrar uma solução.")