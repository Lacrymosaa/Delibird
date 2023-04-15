import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import ttk
import csv
import os
from PIL import Image, ImageTk

# Obtém o nome do usuário atual
user = os.getlogin()

# Cria a janela principal do programa
root = Tk()
root.title(f"Delibird de {user}")
root.geometry("800x400")
root.iconbitmap("imgs/Delibird.ico")

# Cria um quadro para a entrada de URL da loja online
url_frame = Frame(root)
url_frame.pack(pady=10)

url_label = Label(url_frame, text="Insira a URL da loja online:")
url_label.pack(side=LEFT)

url_entry = Entry(url_frame, width=50)
url_entry.pack(side=LEFT)

# Cria um quadro para exibir a lista de presentes
list_frame = Frame(root)
list_frame.pack(pady=10)

list_label = Label(list_frame, text="Lista de Presentes:")
list_label.pack()

# Cria a tabela para exibir a lista de presentes
tree = ttk.Treeview(list_frame)
tree["columns"] = ("name", "price", "link")
tree.column("#0", width=0, stretch=NO)  # Define largura 0 e sem stretch para a coluna de "id"
tree.column("name", width=200)
tree.column("price", width=100)
tree.column("link", width=300)
tree.heading("name", text="Nome")
tree.heading("price", text="Preço")
tree.heading("link", text="Link")
tree.configure(show="headings")  # Oculta a coluna de "id"
tree.pack(side=LEFT, fill=Y)

# Cria uma barra de rolagem para a tabela
scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side=RIGHT, fill=Y)
tree.configure(yscrollcommand=scrollbar.set)

# Cria o quadro para o rodapé
footer_frame = Frame(root)
footer_frame.pack(side=BOTTOM, pady=10)

# Cria o rótulo com o texto do rodapé
footer_label = Label(footer_frame, text="Para deletar um item da lista, basta clicar com o direito sobre ele")
footer_label.pack()


# Cria uma função para carregar a lista de presentes a partir do arquivo CSV
def load_list():
    try:
        with open("lista.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                name, price, link = row
                tree.insert("", "end", text=name, values=(name, price, link))
    except FileNotFoundError:
        pass

# Cria uma função para salvar a lista de presentes no arquivo CSV
def save_list():
    with open("lista.csv", "w", newline="") as file:
        writer = csv.writer(file)
        for item in tree.get_children():
            name, price, link = tree.item(item)["values"]
            writer.writerow([name, price, link])

# Chama a função para carregar a lista de presentes
load_list()

# Cria uma função para excluir um item da lista de presentes
def delete_item(event):
    item = tree.identify_row(event.y)
    tree.delete(item)
    save_list()

# Associa o evento de clique com o botão direito à função de exclusão
tree.bind("<Button-3>", delete_item)

# Armazena em cache as páginas baixadas para evitar múltiplas solicitações HTTP
cache = {}

# Máximo de tentativas para baixar uma página antes de desistir
MAX_RETRIES = 3

# Limite máximo de tempo de execução (em segundos)
MAX_EXECUTION_TIME = 300

# Cria uma função para extrair informações de produtos da página da web
def extract_info(url):
    # Verifica se a página já foi baixada e armazenada em cache
    if url in cache:
        soup = cache[url]
    else:
        # Faz a solicitação HTTP
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
        retries = 0
        while retries < MAX_RETRIES:
            try:
                response = requests.get(url, headers=headers, timeout=60, allow_redirects=False)
                if response.status_code == 200:
                        soup = BeautifulSoup(response.content, features="lxml")
                        break
            except (requests.exceptions.Timeout, requests.exceptions.RequestException):
                pass
            retries += 1
        else:
            return []
        
        # Armazena em cache a página baixada
        cache[url] = soup

    # Extrai informações de produtos, como nome, preço e link de compra
    products = []
    try:
        title_elem = soup.find_all(id="productTitle")
        price_elem = soup.find_all(id="price")
        if len(title_elem) > 0 and len(price_elem) > 0:
            title = title_elem[0].get_text().strip()
            price = price_elem[0].get_text().strip()
            link = url
            products.append((title, price, link))
    except:
        pass

    return products


# Cria uma função para adicionar um item à lista de presentes
def add_item():
    # Extrai informações de produtos da URL fornecida
    url = url_entry.get()
    products = extract_info(url)

    # Adiciona informações de produtos à lista de presentes
    for product in products:
        name, price, link = product
        tree.insert("", "end", text=name, values=(name, price, link))
        save_list()

    # Limpa a entrada de URL
    url_entry.delete(0, END)

# Cria um botão para adicionar um item à lista de presentes
add_button = Button(root, text="Adicionar Item", command=add_item)
add_button.pack(pady=10)

# Inicia a janela principal do programa
root.mainloop()
