import random
from typing import List, Tuple, Optional

# Repsesentação dos items
class Item:
    def __init__(self, name: str, weight: int, value: int):
        self.name = name
        self.weight = weight # Atributo 'weight'
        self.value = value

    def __repr__(self) -> str:
        return f"Item(nome='{self.name}', peso={self.weight}, valor={self.value})"

# Criação e Inicialização da População
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

# Seleção
def selecionar_pai_torneio(populacao: List[List[int]],
                             pontuacoes_fitness: List[int],
                             tam_torneio: int) -> List[int]:
    """Seleciona um único pai usando seleção por torneio."""
    if not populacao:
        raise ValueError("A população não pode estar vazia para seleção por torneio.")

    k = min(tam_torneio, len(populacao))
    if k == 0:
        # Fallback para evitar erro se a população se tornar muito pequena para o torneio
        # Embora isso deva ser evitado com controle de tam_populacao
        if populacao:
            return random.choice(populacao)
        else:
            raise ValueError("Não é possível selecionar de uma população vazia ou com tamanho de torneio 0.")


    indices_torneio = random.sample(range(len(populacao)), k)

    melhor_indice_contendor = -1
    melhor_fitness_contendor = -1 # Assume-se fitness não negativo

    for indice in indices_torneio:
        if pontuacoes_fitness[indice] > melhor_fitness_contendor:
            melhor_fitness_contendor = pontuacoes_fitness[indice]
            melhor_indice_contendor = indice

    if melhor_indice_contendor == -1 and indices_torneio: # Todos os fitness são iguais (ex: 0)
        return populacao[indices_torneio[0]] # Retorna o primeiro do torneio

    return populacao[melhor_indice_contendor]

# Cruzamento
def cruzamento_ponto_unico(pai1: List[int], pai2: List[int], taxa_cruzamento: float) -> Tuple[List[int], List[int]]:
    """Realiza cruzamento de ponto único entre dois pais se a taxa_cruzamento for atingida."""
    filho1, filho2 = pai1[:], pai2[:] # Copia os pais por padrão
    if random.random() < taxa_cruzamento and len(pai1) > 1: # Garante que cruzamento é possível (len(pai1) > 1 é suficiente pois pai1 e pai2 tem o mesmo tamanho)
        ponto = random.randint(1, len(pai1) - 1)
        filho1 = pai1[:ponto] + pai2[ponto:]
        filho2 = pai2[:ponto] + pai1[ponto:]
    return filho1, filho2

# Mutação
def mutacao_bit_flip(individuo: List[int], taxa_mutacao: float) -> List[int]:
    """Realiza mutação bit-flip em um indivíduo."""
    individuo_mutado = individuo[:]
    for i in range(len(individuo_mutado)):
        if random.random() < taxa_mutacao:
            individuo_mutado[i] = 1 - individuo_mutado[i]  # Inverte o bit
    return individuo_mutado

def algoritmo_genetico_mochila_iterativo(
    items_data: List[Tuple[str, int, int]],
    capacidade_maxima: int,
    tam_populacao: int = 100,
    num_geracoes: int = 200,
    taxa_mutacao: float = 0.02,
    taxa_cruzamento: float = 0.85,
    contagem_elitismo: int = 2,
    tam_torneio: int = 5,
    seed: Optional[int] = None
) -> List[Tuple[List[int], int, int, int]]: # Retorna histórico de (melhor_solucao_cromossomo, valor, peso, fitness)
    """
    Resolve o problema da mochila usando um algoritmo genético, retornando o histórico
    da melhor solução (o melhor cromossomo) a cada geração, junto com seu valor, peso e fitness.
    """
    if seed is not None:
        random.seed(seed)

    items = [Item(nome, peso, valor) for nome, peso, valor in items_data]
    num_items = len(items)

    # Validations
    if num_items == 0:
        return []
    if tam_populacao <= 0:
        return []
    if contagem_elitismo < 0:
        contagem_elitismo = 0
    if contagem_elitismo >= tam_populacao:
        contagem_elitismo = max(0, tam_populacao - 1)
    if tam_torneio <= 0:
        tam_torneio = 1 # Garante que o torneio tenha pelo menos 1 participante

    populacao_atual = inicializar_populacao(tam_populacao, num_items)

    melhor_solucao_geral: Optional[List[int]] = None
    melhor_fitness_geral = -1
    melhor_valor_geral = -1
    melhor_peso_geral = -1

    historico_melhores = []

    for geracao in range(num_geracoes):
        avaliacoes_populacao = []
        fitness_scores_populacao_atual = []

        for individuo in populacao_atual:
            fitness, valor_real, peso_real = calcular_detalhes_individuo(individuo, items, capacidade_maxima)
            avaliacoes_populacao.append((fitness, valor_real, peso_real, individuo))
            fitness_scores_populacao_atual.append(fitness)

        # Ordena a população pelo fitness (do maior para o menor)
        avaliacoes_populacao.sort(key=lambda x: x[0], reverse=True)

        if avaliacoes_populacao:
            melhor_fitness_geracao_atual = avaliacoes_populacao[0][0]
            melhor_valor_geracao_atual = avaliacoes_populacao[0][1]
            melhor_peso_geracao_atual = avaliacoes_populacao[0][2]
            melhor_individuo_geracao_atual = avaliacoes_populacao[0][3]

            # Atualiza a melhor solução geral se a solução atual for melhor
            if melhor_fitness_geracao_atual > melhor_fitness_geral:
                melhor_fitness_geral = melhor_fitness_geracao_atual
                melhor_solucao_geral = melhor_individuo_geracao_atual
                melhor_valor_geral = melhor_valor_geracao_atual
                melhor_peso_geral = melhor_peso_geracao_atual
            elif melhor_fitness_geracao_atual == melhor_fitness_geral and \
                 melhor_peso_geracao_atual <= capacidade_maxima and \
                 (melhor_peso_geral == -1 or melhor_peso_geracao_atual < melhor_peso_geral):
                # Se o fitness é igual, prefere soluções com menor peso (se ambas válidas)
                melhor_fitness_geral = melhor_fitness_geracao_atual
                melhor_solucao_geral = melhor_individuo_geracao_atual
                melhor_valor_geral = melhor_valor_geracao_atual
                melhor_peso_geral = melhor_peso_geracao_atual


            # Adiciona a melhor solução GERAL (acumulada) desta geração ao histórico
            # Isso garante que sempre mostramos a melhor até o momento
            historico_melhores.append((
                list(melhor_solucao_geral) if melhor_solucao_geral else [0] * num_items,
                melhor_valor_geral,
                melhor_peso_geral,
                melhor_fitness_geral
            ))
        else:
            # Se a população estiver vazia (não deveria ocorrer com tam_populacao > 0)
            historico_melhores.append((None, 0, 0, 0))


        # Gera a nova população
        nova_populacao = []
        # Elitismo: Adiciona os melhores indivíduos da geração atual à nova população
        for i in range(min(contagem_elitismo, len(avaliacoes_populacao))):
            nova_populacao.append(avaliacoes_populacao[i][3])

        num_descendentes_necessarios = tam_populacao - len(nova_populacao)
        descendentes_gerados = 0

        # Loop para gerar descendentes até preencher a nova população
        while descendentes_gerados < num_descendentes_necessarios:
            # Seleção de pais
            # Adicionado tratamento para caso a população atual seja muito pequena para o torneio
            if len(populacao_atual) < tam_torneio:
                 # Fallback: se a população é pequena, seleciona pais aleatoriamente ou duplica
                 pai1 = random.choice(populacao_atual) if populacao_atual else criar_individuo(num_items)
                 pai2 = random.choice(populacao_atual) if populacao_atual else criar_individuo(num_items)
            else:
                 pai1 = selecionar_pai_torneio(populacao_atual, fitness_scores_populacao_atual, tam_torneio)
                 # Tenta selecionar um pai2 diferente, se possível
                 temp_pop = [p for p in populacao_atual if p != pai1]
                 if temp_pop and len(temp_pop) >= tam_torneio:
                    temp_fitness = [fitness_scores_populacao_atual[populacao_atual.index(p)] for p in temp_pop]
                    pai2 = selecionar_pai_torneio(temp_pop, temp_fitness, tam_torneio)
                 elif temp_pop: # Se não há suficientes para um torneio, escolhe um aleatório entre os restantes
                    pai2 = random.choice(temp_pop)
                 else: # Se só sobrou o pai1, usa ele de novo
                    pai2 = pai1


            # Cruzamento
            filho1, filho2 = cruzamento_ponto_unico(pai1, pai2, taxa_cruzamento)

            # Mutação e adição à nova população
            nova_populacao.append(mutacao_bit_flip(filho1, taxa_mutacao))
            descendentes_gerados += 1

            if descendentes_gerados < num_descendentes_necessarios:
                nova_populacao.append(mutacao_bit_flip(filho2, taxa_mutacao))
                descendentes_gerados += 1

        # Garante que a nova população tenha o tamanho correto
        populacao_atual = nova_populacao[:tam_populacao]

    return historico_melhores