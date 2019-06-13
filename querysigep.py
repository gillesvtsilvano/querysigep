import requests
from bs4 import BeautifulSoup as bs
import re
from laudo_sigep import LaudoSigep

def main():

    # Useful URLs
    root_url='https://www2.itep.rn.gov.br/sigep/public/'
    login_url=root_url+'login'
    select_sector_url=root_url+'seleciona_vinculo/20247'
    search_url=root_url+'comele/consulta'
    doc_url=root_url+'comele/documento/'
    laudo_url=root_url+'resumo_laudo/'
    NIC = 4332
    # Parameters
    mime_type = 'application/x-www-form-urlencoded'
    token=''

    # Login credentials
    # TODO: Danger! Remove it before push!
    cpf='000.000.000-00'
    pwd='xxxxxxxx'    # Create a session
    s = requests.session()
    
    # Access the login page
    response = s.get(login_url)

    # Acquire access token
    soup = bs(response.text, 'html.parser')
    for tag in soup.find_all('input', attrs={'name': '_token'}):
        if tag: # Double check :)
            token = tag['value']

    # Prepare login payload
    payload = {
            'MIME Type': mime_type,
            '_token': token,
            'st_cpf': cpf,
            'password': pwd
    }
    
    # Login
    response = s.post(login_url, params=payload)

    # Prepare new payload
    del payload['st_cpf']
    del payload['password']
    payload['id_setor'] = 5 # Sala de Peritos
    
    # Select 'Sala dos Peritos'
    response = s.post(select_sector_url, params=payload)

    # Prepare new payload 
    del payload['id_setor']
    payload.update({
        'tipo': 'cadaveres',
        'sub_tipo': 'st_nic',
        'nome': NIC, # TODO: Test NIC. Change it!
        'sequencial': '',
        'ano': ''
    })

    # Search by NIC
    response = s.post(search_url, params=payload)
    
    # Access the details of the corpse
    soup = bs(response.text, 'html.parser')
    for link in soup.find_all('a', attrs={'title': 'Detalhes'}):
        if link: # if it exists
            response = s.get(link.get('href'))
    
    # Get all links and search for " Exame perici...
    target_url = '' 
    links = list()
    accessed = list()
    soup = bs(response.text, 'html.parser')
    for link in soup.find_all('a', attrs={'href': re.compile(r'^' + root_url + '(resumo_laudo|comele/documento)/\d+$')}):
        links.append(link)    


    # Iterating over all links searching for the laudo id of
    # Local de achado de Cadáver
    while links:
        accessed.append(links[0])
        
        response = s.get(links[0].get('href'))
        soup = bs(response.text, 'html.parser')
        for link in soup.find_all('a', attrs={'href': re.compile(r'^' + root_url + '(resumo_laudo|comele/documento)/\d+$')}):
            if "Exame Pericial em Local de Achado de Cadáver" in link.text.strip():
                target_url = link.get('href')
                links = [link]
                break
            if link not in accessed:
                links.append(link)
        del links[0]
   
    # Obtaining laudo id and accessing its history
    laudo_id=target_url.split('/')[-1]
    laudo_url=''
    if laudo_id:
        laudo_url=root_url+'exibir_historico_laudo/' + laudo_id

    # TODO: scrap all values for LaudoSigep class
    
    id_num = laudo_id
    laudo_num = 0
    nic = NIC
    descr = 'Testing.'
    register_date = ''
    conclusion_date = ''


    response = s.get(laudo_url)
    soup = bs(response.text, 'html.parser')
    
    for legend in soup.find_all('legend'):
        laudo_num = legend.text.split(': ')[-1]
    
    for date,user,action,status in zip(*[iter(soup.find_all('td'))]*4):
        #print(date.text, user.text, action.text, status.text)
        if status.text == 'Finalizado' and not conclusion_date:
            conclusion_date = date.text
        if status.text == 'Cadastrado' and not register_date:
            register_date = date.text
    
    laudo = LaudoSigep(id_num, laudo_num, nic, descr)
    laudo.set_register_date(register_date)
    laudo.set_conclusion_date(conclusion_date)
           
    print(laudo)
    
if __name__ == '__main__':
    main()
