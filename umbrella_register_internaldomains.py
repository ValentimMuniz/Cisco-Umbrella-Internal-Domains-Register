# Script Desenvolvido por: Valentim Uliana
# Script que cria Internal Networks no Umbrella a partir de um CSV, facilitando para cadastro de redes em massa.

import json
import requests
import configparser
import csv
import sys

# Arquivo de configuração
config = configparser.ConfigParser()
config.read('config')
org_id = config['Umbrella']['OrgID']
mgmt_api_key = config['Umbrella']['ManagementAPIKey']
mgmt_api_secret = config['Umbrella']['ManagementAPISecret']
csvname = config['CSV']['FileName']


#Headers
header_internaldomain = {'Content-Type': 'application/json','Accept': 'application/json'}


# management api url, usado para pegar o access token do reporting api
mgmt_url = 'https://management.api.umbrella.com/v1'


#Função para fazer GET das Internal Networks existentes no Umbrella
def get_internaldomains_request(endpoint):
    r = requests.get(mgmt_url+endpoint, headers=header_internaldomain, auth=(mgmt_api_key, mgmt_api_secret))
    body = json.loads(r.content)
    return body

#Função para fazer POST e criar as Internal Networks
def post_internaldomains_request(endpoint, internaldomain):
     # Build the POST data
    data = {
        "domain": internaldomain
    }

    r = requests.post(mgmt_url+endpoint, headers=header_internaldomain, auth=(mgmt_api_key, mgmt_api_secret), data=json.dumps(data))
    
    if r.status_code == 200:
        print("Internal Domain:", internaldomain + " foi cadastrado com sucesso")

    body = json.loads(r.content)
    return body
    
def load_csv():
    # Lista para atribuir os dominios do CSV
    csv_domains = []

    try:
        # Pegando o nome do arquivo especificado no arquivo de configuração
        file_name = csvname

        # Tentando abrir o arquivo especificado
        with open(file_name) as csv_file:
            csv_reader = csv.reader(csv_file)

            # Adicionar cada dominio na lista de csv_domains
            for domain in csv_reader:
                csv_domains.append(domain[0])
            
            return csv_domains
    except:
        print(f"Houve um problema ao ler o nome do arquivo especificado '{file_name}'.")
        print("Revise no arquivo de configuração 'FileName', e verifique se esta tudo correto")
        sys.exit()

def main():
    # fazer o get das internal netwokrs para comparar com o vsv
    r_get_internaldomain = get_internaldomains_request('/organizations/{}/internaldomains'.format(org_id))

    new_internaldomains = []

    new_internaldomains += load_csv()
    
    lista_exist_umbrella = []

    #Adicionar do Umbrella Internal Domains a uma lista
    for internadomail in r_get_internaldomain:
        lista_exist_umbrella.append(internadomail['domain'])

    #Remover duplicados no CSV
    new_internaldomains = list(dict.fromkeys(new_internaldomains))
    
    # Remover da lista o que já esta cadastrado no Umbrella
    new_internaldomains = list(set(new_internaldomains) - set(lista_exist_umbrella))
    
    #Se a lista retornar vazia não cadastrar nada
    if not new_internaldomains:
        print("Nada neste CSV para cadastrar!! Provalemente o que tem no CSV, já está cadastrado no Umbrella!!!")
    else:   
        for cadastrar in new_internaldomains:        
            post_internaldomains_request('/organizations/{}/internaldomains'.format(org_id), cadastrar)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write("\n\nFechando script...\n\n")
        sys.stdout.flush()
        pass
     