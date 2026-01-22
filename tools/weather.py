import requests

def get_current_weather(location: str) -> str:
    """
    Obtém informações meteorológicas atuais para uma determinada localização.
    
    Args:
        location (str): O nome da cidade ou região (ex: "São Paulo", "New York").
        
    Returns:
        str: Uma string contendo os dados meteorológicos ou uma mensagem de erro.
    """
    try:
        # wttr.in retorna texto simples com formato=3 para uma saída concisa
        # Equivalente a: Cidade: Condição Temp
        url = f"https://wttr.in/{location}?format=%C+%t+%w"
        response = requests.get(url)
        
        if response.status_code == 200:
            return f"Clima em {location}: {response.text.strip()}"
        else:
            return f"Não foi possível obter o clima para {location}. Status: {response.status_code}"
    except Exception as e:
        return f"Erro ao conectar com serviço de clima: {str(e)}"
