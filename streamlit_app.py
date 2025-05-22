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
    .knapsack-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        min-height: 250px; /* Altura mínima para a mochila */
        margin-bottom: 30px;
        position: relative;
    }
    .knapsack-base {
        width: 300px;
        height: 150px;
        background-color: #8B4513; /* Marrom escuro */
        border: 5px solid #5A2D0C;
        border-radius: 10px;
        position: relative;
        overflow: hidden; /* Garante que os itens não ultrapassem a borda */
        display: flex;
        flex-wrap: wrap; /* Para os itens se ajustarem */
        align-content: flex-end; /* Itens "sobem" de baixo para cima */
        padding: 10px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }
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
        transform: translateY(50px); /* Começa abaixo da mochila */
        transition: opacity 0.5s ease-out, transform 0.5s ease-out; /* Transição suave */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        cursor: help; /* Para indicar que há mais informações */
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 60px; /* Largura mínima para o item */
        height: 30px; /* Altura fixa para o item */
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

st.markdown('<h1 class="main-header">🎒 O Divertido Problema da Mochila com AG 🧬</h1>', unsafe_allow_html=True)

st.write("""
Este aplicativo visualiza o problema da mochila sendo resolvido por um Algoritmo Genético.
Veja como a seleção de itens evolui ao longo das gerações para encontrar a melhor combinação!
""")

# --- Sidebar para Controles e Parâmetros ---
st.sidebar.header("⚙️ Configurações do Algoritmo Genético")
capacidade_mochila = st.sidebar.number_input("Capacidade Máxima da Mochila:", min_value=1, value=DEFAULT_CAPACITY, step=1)
num_items_para_gerar = st.sidebar.slider("Número de Itens (Gerados Aleatoriamente):", 5, 30, len(DEFAULT_ITEMS_DATA))

# Gerar itens aleatórios ou usar os mockados
gerar_novos_itens = st.sidebar.checkbox("Gerar novos itens aleatórios?", value=False)

items_data = []
if gerar_novos_itens:
    st.sidebar.subheader("Itens Aleatórios Gerados:")
    for i in range(num_items_para_gerar):
        name = f"Item {i+1}"
        # Ajuste os ranges de peso e valor para serem razoáveis
        weight = random.randint(1, 15)
        value = random.randint(10, 150)
        items_data.append((name, weight, value))
        st.sidebar.write(f"- {name}: P={weight}, V={value}")
else:
    # Limita se o slider for menor que o número de itens default
    items_data = DEFAULT_ITEMS_DATA[:num_items_para_gerar]
    st.sidebar.subheader("Itens Pré-definidos:")
    for name, weight, value in items_data:
        st.sidebar.write(f"- {name}: P={weight}, V={value}")


# Parâmetros do AG
tam_populacao = st.sidebar.slider("Tamanho da População:", 10, 200, 100)
num_geracoes = st.sidebar.slider("Número de Gerações:", 50, 500, 150)
taxa_cruzamento = st.sidebar.slider("Taxa de Cruzamento:", 0.0, 1.0, 0.85, 0.05)
taxa_mutacao = st.sidebar.slider("Taxa de Mutação:", 0.0, 0.1, 0.03, 0.005)
contagem_elitismo = st.sidebar.slider("Elitismo (Melhores Indivíduos Preservados):", 0, 10, 3)
tam_torneio = st.sidebar.slider("Tamanho do Torneio (Seleção):", 2, 10, 5)
seed_val = st.sidebar.number_input("Seed (para reprodutibilidade):", value=42)
animation_speed = st.sidebar.slider("Velocidade da Animação (segundos/geração):", 0.05, 1.0, 0.2, 0.05)

st.sidebar.markdown("---")
st.sidebar.info("Ajuste os parâmetros e clique em 'Iniciar Simulação' para ver a mágica acontecer!")


# --- Colunas para Layout Principal ---
col_mochila, col_status, col_graficos = st.columns([1.5, 1, 1.5])

with col_mochila:
    st.subheader("👜 Mochila Atual")
    mochila_placeholder = st.empty() # Placeholder para a mochila e seus itens
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
    st.balloons() # Animação de balões ao iniciar

    st.write("Iniciando o Algoritmo Genético...")

    # Armazenar histórico para o gráfico
    historico_fitness_geral_para_grafico = []


    # Executar o algoritmo genético iterativamente
    # O algoritmo_genetico_mochila_iterativo já foi adaptado para retornar o histórico
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


    for geracao_idx, (solucao, valor, peso, fitness) in enumerate(historico_solucoes):
        # Atualiza a barra de progresso
        progress_bar_placeholder.progress((geracao_idx + 1) / num_geracoes)

        generation_info.markdown(f"<p class='progress-info'>Geração: <strong>{geracao_idx + 1}/{num_geracoes}</strong></p>", unsafe_allow_html=True)
        best_value_info.markdown(f"<p class='progress-info'>Valor Atual: <strong>${valor}</strong></p>", unsafe_allow_html=True)
        current_weight_info.markdown(f"<p class='progress-info'>Peso Atual: <strong>{peso}/{capacidade_mochila} kg</strong></p>", unsafe_allow_html=True)
        best_overall_info.markdown(f"<p class='progress-info'>Melhor Valor Geral: <strong>${historico_solucoes[geracao_idx][3]}</strong></p>", unsafe_allow_html=True) # historico_solucoes[geracao_idx][3] é o fitness acumulado

        # Visualização da Mochila
        with mochila_placeholder.container():
            # Inicia o container da mochila
            st.markdown('<div class="knapsack-container"><div class="knapsack-base" id="mochila-base">', unsafe_allow_html=True)
            itens_selecionados_detalhes = []
            if solucao:
                for i, gene in enumerate(solucao):
                    if gene == 1:
                        item = items_obj_list[i]
                        # Renderiza cada item dentro da mochila com a classe 'visible' para animação
                        st.markdown(
                            f"""
                            <div class="knapsack-item visible" title="{item.name} (P:{item.weight}, V:${item.value})">
                                {item.name}<br>({item.weight}kg, ${item.value})
                            </div>
                            """, unsafe_allow_html=True
                        )
                        itens_selecionados_detalhes.append(item)
            # Fecha o container da mochila
            st.markdown('</div></div>', unsafe_allow_html=True)

            # Detalhes dos itens na mochila (fora da div da mochila visual)
            with item_details_placeholder.container():
                st.subheader("Itens Selecionados na Melhor Solução:")
                if itens_selecionados_detalhes:
                    for item in itens_selecionados_detalhes:
                        st.markdown(f"""
                            <div class="item-card">
                                <h5>{item.name}</h5>
                                <p>Peso: {item.weight} kg | Valor: ${item.value}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nenhum item válido selecionado ainda nesta solução.")


        # Atualizar gráfico de evolução do fitness
        # historico_solucoes[geracao_idx][3] é o fitness da melhor solução geral até esta geração
        historico_fitness_geral_para_grafico.append(historico_solucoes[geracao_idx][3])
        # Streamlit precisa de uma estrutura de dados para o gráfico de linha, uma lista simples funciona.
        chart_data_placeholder.line_chart(historico_fitness_geral_para_grafico)


        time.sleep(animation_speed) # Controla a velocidade da animação

    st.success("Simulação Completa! 🎉")
    st.snow() # Efeito de neve ao final

    # Exibir o resultado final novamente
    st.markdown("---")
    st.subheader("✅ Melhor Solução Final Encontrada:")
    if historico_solucoes:
        # Pega a última entrada do histórico, que é a melhor solução final
        final_solucao, final_valor, final_peso, final_fitness = historico_solucoes[-1]
        if final_solucao:
            final_itens_selecionados_obj = [items_obj_list[i] for i, gene in enumerate(final_solucao) if gene == 1]
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