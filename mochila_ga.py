import random
from typing import List, Tuple, Optional

# --- Representação do Item ---
class Item:
    def __init__(self, name: str, weight: int, value: int):
        self.name = name
        self.weight = weight
        self.value = value

    def __repr__(self) -> str:
        return f"Item(nome='{self.name}', peso={self.weight}, valor={self.value})"

# --- Funções Auxiliares do Algoritmo Genético ---

def criar_individuo(num_items: int) -> List[int]:
    """Cria um indivíduo aleatório (cromossomo) como uma lista de bits."""
    return [random.randint(0, 1) for _ in range(num_items)]

def inicializar_populacao(tam_populacao: int, num_items: int) -> List[List[int]]:
    """Inicializa uma população de indivíduos aleatórios."""
    return [criar_individuo(num_items) for _ in range(tam_populacao)]

def calcular_detalhes_individuo(individuo: List[int], items: List[Item], capacidade_maxima: int) -> Tuple[int, int, int]:
    """
    Calcula os detalhes de um indivíduo (solução).
    Retorna: (pontuacao_fitness, valor_total_real, peso_total_real)
    A pontuacao_fitness é o valor_total_real se o peso estiver dentro da capacidade,
    caso contrário, é 0 (penalidade).
    """
    peso_total = 0
    valor_total = 0
    for i, gene in enumerate(individuo):
        if gene == 1:
            peso_total += items[i].weight
            valor_total += items[i].value

    if peso_total > capacidade_maxima:
        pontuacao_fitness = 0  # Penaliza fortemente soluções inválidas
    else:
        pontuacao_fitness = valor_total
    return pontuacao_fitness, valor_total, peso_total

def selecionar_pai_torneio(populacao: List[List[int]],
                             pontuacoes_fitness: List[int],
                             tam_torneio: int) -> List[int]:
    """Seleciona um único pai usando seleção por torneio."""
    if not populacao:
        raise ValueError("A população não pode estar vazia para seleção por torneio.")
    
    # Garante que o tamanho do torneio não exceda o tamanho da população disponível
    k = min(tam_torneio, len(populacao))
    if k == 0: # Se a população efetivamente se tornou vazia (não deveria, mas como defesa)
        # Lógica do seu notebook original: se k=0 e indices_torneio não estiver vazio, usa o primeiro.
        # Mas se populacao está vazia, o erro deve ser levantado.
        raise ValueError("Não é possível selecionar de uma população vazia ou com tamanho de torneio 0.")


    indices_torneio = random.sample(range(len(populacao)), k)

    melhor_indice_contendor = -1
    melhor_fitness_contendor = -1 # Assume-se fitness não negativo

    for indice in indices_torneio:
        if pontuacoes_fitness[indice] > melhor_fitness_contendor:
            melhor_fitness_contendor = pontuacoes_fitness[indice]
            melhor_indice_contendor = indice
            
    # Lógica do seu notebook original: Se todos os contendores tiverem fitness 0 (ou negativo),
    # e nenhum melhor foi achado (melhor_indice_contendor ainda é -1),
    # ou se melhor_indice_contendor for válido.
    if melhor_indice_contendor == -1 and indices_torneio: # Todos os fitness são iguais (ex: 0)
        return populacao[indices_torneio[0]] # Retorna o primeiro do torneio
        
    return populacao[melhor_indice_contendor]


def cruzamento_ponto_unico(pai1: List[int], pai2: List[int], taxa_cruzamento: float) -> Tuple[List[int], List[int]]:
    """Realiza cruzamento de ponto único entre dois pais se a taxa_cruzamento for atingida."""
    filho1, filho2 = pai1[:], pai2[:] # Copia os pais por padrão
    if random.random() < taxa_cruzamento and len(pai1) > 1 and len(pai2) > 1: # Garante que cruzamento é possível
        ponto = random.randint(1, len(pai1) - 1)
        filho1 = pai1[:ponto] + pai2[ponto:]
        filho2 = pai2[:ponto] + pai1[ponto:]
    return filho1, filho2

def mutacao_bit_flip(individuo: List[int], taxa_mutacao: float) -> List[int]:
    """Realiza mutação bit-flip em um indivíduo."""
    individuo_mutado = individuo[:]
    for i in range(len(individuo_mutado)):
        if random.random() < taxa_mutacao:
            individuo_mutado[i] = 1 - individuo_mutado[i]  # Inverte o bit
    return individuo_mutado

# --- Algoritmo Genético Principal (Adaptado para retornar histórico para Streamlit) ---
def algoritmo_genetico_mochila_iterativo( # Renomeada para deixar claro que é a versão iterativa
    items_data: List[Tuple[str, int, int]],
    capacidade_maxima: int,
    tam_populacao: int = 100,
    num_geracoes: int = 200,
    taxa_mutacao: float = 0.02,
    taxa_cruzamento: float = 0.85,
    contagem_elitismo: int = 2,
    tam_torneio: int = 5,
    seed: Optional[int] = None
) -> List[Tuple[List[int], int, int, int]]: # Retorna histórico de (melhor_solucao_cromossomo, valor_real, peso_real, fitness_calculado)
    """
    Resolve o problema da mochila usando um algoritmo genético, retornando o histórico
    da melhor solução (cromossomo, valor real, peso real, fitness) encontrada globalmente
    até cada geração.
    """
    if seed is not None:
        random.seed(seed)

    items = [Item(nome, peso, valor) for nome, peso, valor in items_data]
    num_items = len(items)

    # Validações - Mantido o comportamento do notebook, mas sem 'verbose' prints
    if num_items == 0:
        return []
    if tam_populacao <=0:
        return []
    if contagem_elitismo < 0:
        contagem_elitismo = 0
    if contagem_elitismo >= tam_populacao:
        contagem_elitismo = max(0, tam_populacao -1) 
    if tam_torneio <= 0:
        tam_torneio = 1


    populacao_atual = inicializar_populacao(tam_populacao, num_items)
    
    melhor_solucao_geral: Optional[List[int]] = None
    melhor_fitness_geral = -1
    melhor_valor_geral = -1 # Valor real da melhor solução geral
    melhor_peso_geral = -1 # Peso real da melhor solução geral

    historico_melhores_solucoes_gerais = [] # Para armazenar o histórico para o Streamlit

    for geracao in range(num_geracoes):
        avaliacoes_populacao = []
        fitness_scores_populacao_atual = [] 

        for individuo in populacao_atual:
            fitness, valor_real, peso_real = calcular_detalhes_individuo(individuo, items, capacidade_maxima)
            avaliacoes_populacao.append((fitness, valor_real, peso_real, individuo))
            fitness_scores_populacao_atual.append(fitness)
        
        avaliacoes_populacao.sort(key=lambda x: x[0], reverse=True)

        if avaliacoes_populacao: # Checa se a lista não está vazia
            melhor_fitness_geracao_atual = avaliacoes_populacao[0][0]
            melhor_valor_geracao_atual = avaliacoes_populacao[0][1] # Valor real da melhor da geração
            melhor_peso_geracao_atual = avaliacoes_populacao[0][2] # Peso real da melhor da geração
            melhor_individuo_geracao_atual = avaliacoes_populacao[0][3]

            if melhor_fitness_geracao_atual > melhor_fitness_geral:
                melhor_fitness_geral = melhor_fitness_geracao_atual
                melhor_solucao_geral = melhor_individuo_geracao_atual
                melhor_valor_geral = melhor_valor_geracao_atual # Atualiza o valor real da melhor geral
                melhor_peso_geral = melhor_peso_geracao_atual # Atualiza o peso real da melhor geral
            # Sem a lógica do verbose print para console aqui, pois será feita no Streamlit
        # else: A lógica do notebook original não tinha um else para este if,
        # significando que se a populacao_avaliada estivesse vazia,
        # o histórico não seria atualizado para aquela geração, o que pode levar a um gap.
        # Para Streamlit, é bom ter um registro para cada geração.
        
        # Adiciona a melhor solução GERAL (acumulada) até esta geração ao histórico
        # Isso garante que o Streamlit sempre mostre o melhor resultado encontrado até o momento.
        historico_melhores_solucoes_gerais.append((
            list(melhor_solucao_geral) if melhor_solucao_geral else [0] * num_items,
            melhor_valor_geral if melhor_valor_geral != -1 else 0, # Garante que seja 0 se não houver solução válida ainda
            melhor_peso_geral if melhor_peso_geral != -1 else 0,   # Garante que seja 0 se não houver solução válida ainda
            melhor_fitness_geral if melhor_fitness_geral != -1 else 0 # Fitness para o gráfico
        ))

        nova_populacao = []
        for i in range(min(contagem_elitismo, len(avaliacoes_populacao))):
            nova_populacao.append(avaliacoes_populacao[i][3])

        num_descendentes_necessarios = tam_populacao - len(nova_populacao)
        descendentes_gerados = 0
        
        # Loop para gerar descendentes até preencher a nova população
        # Adiciona verificações para evitar erros com populações pequenas ou vazias
        while descendentes_gerados < num_descendentes_necessarios:
            # Lógica de fallback para população pequena idêntica ao notebook
            if not populacao_atual or not fitness_scores_populacao_atual or len(populacao_atual) < max(1,tam_torneio) : 
                while len(nova_populacao) < tam_populacao:
                    nova_populacao.append(criar_individuo(num_items))
                break 

            pai1 = selecionar_pai_torneio(populacao_atual, fitness_scores_populacao_atual, tam_torneio)
            # Lógica de seleção do segundo pai idêntica ao notebook
            pai2_candidatos = [p for p in populacao_atual if p is not pai1] # Evita selecionar o mesmo pai se possível
            if not pai2_candidatos and len(populacao_atual) > 0: # Se só resta o pai1
                 pai2 = pai1 # Usa o mesmo pai se for o único
            elif not pai2_candidatos: # Se população atual está vazia após seleção do pai1 (improvável)
                 pai2 = criar_individuo(num_items) # Cria um pai aleatório
            else:
                 pai2_fitness_candidatos = [fitness_scores_populacao_atual[populacao_atual.index(p)] for p in pai2_candidatos]
                 pai2 = selecionar_pai_torneio(pai2_candidatos, pai2_fitness_candidatos, tam_torneio)


            filho1, filho2 = cruzamento_ponto_unico(pai1, pai2, taxa_cruzamento)

            nova_populacao.append(mutacao_bit_flip(filho1, taxa_mutacao))
            descendentes_gerados += 1

            if descendentes_gerados < num_descendentes_necessarios:
                nova_populacao.append(mutacao_bit_flip(filho2, taxa_mutacao))
                descendentes_gerados += 1
        
        populacao_atual = nova_populacao[:tam_populacao]

    # Removidos os prints de resultados finais, pois o Streamlit cuidará disso.
    # O retorno agora é o histórico completo.
    return historico_melhores_solucoes_gerais

# O bloco if __name__ == "__main__": é para testar a função isoladamente no terminal,
# e não será executado quando o Streamlit importar este módulo.
if __name__ == "__main__":
    # Exemplo de itens: (nome, peso, valor)
    config_itens_ex1 = [
        ("Lanterna", 2, 15), ("Saco de Dormir", 5, 30), ("Comida Enlatada", 10, 50),
        ("Corda", 3, 20), ("Mapa", 1, 10), ("Bússola", 1, 15),
        ("Kit Primeiros Socorros", 4, 25), ("Cantil", 2, 20), ("Faca", 1, 18),
        ("Repelente", 1, 12), ("Câmera", 3, 40), ("Livro", 2, 5),
        ("Barraca", 15, 70), ("Fogareiro", 6, 35), ("Panelas", 4, 22),
        ("Rádio Solar", 3, 28), ("Bateria Extra", 2, 22), ("Chocolate", 1, 16)
    ]
    capacidade_mochila_ex1 = 35

    print(f"\n--- Algoritmo Genético para o Problema da Mochila (Teste de Mochila GA) ---")
    print(f"Itens: {len(config_itens_ex1)}, Capacidade Máxima: {capacidade_mochila_ex1}")
    
    historico_solucoes_teste = algoritmo_genetico_mochila_iterativo(
        items_data=config_itens_ex1,
        capacidade_maxima=capacidade_mochila_ex1,
        tam_populacao=100,
        num_geracoes=150,
        taxa_mutacao=0.03,
        taxa_cruzamento=0.90,
        contagem_elitismo=3,
        tam_torneio=5,
        seed=42
    )

    if historico_solucoes_teste:
        final_solucao, final_valor, final_peso, final_fitness = historico_solucoes_teste[-1]
        print(f"\nResultado final para Exemplo 1 (do teste interno):")
        print(f"Melhor Solução (cromossomo): {final_solucao}")
        print(f"Valor Total: {final_valor}")
        print(f"Peso Total: {final_peso}/{capacidade_mochila_ex1}")
        print(f"Fitness Final: {final_fitness}")
    else:
        print("Nenhuma solução foi encontrada no teste interno.")