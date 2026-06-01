import requests

def pegar_ids_estados():
    # Endpoint da API de Localidades do IBGE que lista todos os estados brasileiros
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    # Parâmetro 'view=nivelado' retorna uma lista de dicionários de nível único (sem aninhamento)
    params = {
        'view':'nivelado',
    }
    # Faz o request GET para a API e retorna o JSON como lista de dicionários
    dados_estados = fazer_request(url, params=params)
    # Dicionário que vai mapear ID numérico do estado → nome do estado
    dict_estado = {}
    # Cada item da lista representa um estado com suas informações
    for dados in dados_estados:
        # 'UF-id' é o identificador numérico do estado (ex: 33 = Rio de Janeiro)
        id_estado = dados['UF-id']
        # 'UF-nome' é o nome completo do estado (ex: 'Rio de Janeiro')
        nome_estado = dados['UF-nome']
        # Armazena o par id → nome para cruzar com os dados de frequência de nomes
        dict_estado[id_estado] = nome_estado
    return dict_estado


def frequencia_nome_por_estado(nome):
    # Endpoint da API de Nomes do IBGE que retorna a frequência de um nome por localidade
    url = f"https://servicodados.ibge.gov.br/api/v2/censos/nomes/{nome}"
    # Parâmetro 'groupBy=UF' agrupa os resultados por Unidade Federativa (estado)
    params = {
        'groupBy':'UF',
    }
    # Faz o request GET e obtém a lista de frequências agrupadas por estado
    dados_frequencias = fazer_request(url, params=params)
    # Dicionário que vai mapear ID numérico do estado → proporção do nome (por 100.000 hab)
    dict_frequencias = {}
    # Cada item da lista representa um estado com os dados de frequência do nome
    for dados in dados_frequencias:
        # 'localidade' é o ID numérico do estado; convertido para int para bater com o dict de estados
        id_estado = int(dados['localidade'])
        # 'res' é a lista de resultados do censo; [0] pega o registro mais recente; 'proporcao' é a frequência
        frequencia = dados['res'][0]['proporcao']
        # Armazena o par id → proporção para exibir junto ao nome do estado
        dict_frequencias[id_estado] = frequencia
    return dict_frequencias

def fazer_request(url, params=None):
    # Realiza o request HTTP GET para a URL informada, passando os parâmetros como query string
    resposta = requests.get(url, params=params)
    try:
        # Lança uma exceção se o servidor retornou um status de erro (4xx ou 5xx)
        resposta.raise_for_status()
    except requests.HTTPError as e:
        # Exibe a mensagem de erro HTTP e retorna None para sinalizar falha ao chamador
        print(f"Erro na requisição: {e}")
        resultado = None
    else:
        # Se não houve erro, converte o corpo da resposta de JSON para objeto Python (lista ou dict)
        resultado = resposta.json()
    return resultado

def main(nome):
    # Obtém o dicionário {id_estado: nome_estado} consultando a API de localidades
    dict_estados = pegar_ids_estados()
    # Obtém o dicionário {id_estado: proporcao} consultando a API de nomes do IBGE
    dict_frequencias = frequencia_nome_por_estado(nome)
    # Cabeçalho da tabela de resultados exibida no terminal
    print(f'--- Frequência do nome "{nome}" por estado (por 100.000 hab) ---')
    # Itera sobre todos os estados para exibir a frequência do nome em cada um
    for id_estado, nome_estado in dict_estados.items():
        # Busca a proporção do nome no estado; usa 0 se o nome não aparece naquele estado
        frequencia_estado = dict_frequencias.get(id_estado, 0)
        # Exibe o nome do estado e a proporção por 100.000 habitantes
        print(f'-> {nome_estado}: {frequencia_estado}')


if __name__ == "__main__":
    # Solicita ao usuário que digite o nome a ser pesquisado antes de executar o programa
    nome = input("Digite um nome para verificar a frequência por estado: ")
    # Inicia o fluxo principal passando o nome informado pelo usuário
    main(nome)
    