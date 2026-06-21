from src import banco
from src import download


escolha = int(input("1) inserir\n2) retornar\n3) baixar\n"))

if escolha == 1:
    adicionar = "True"
    data = list()
    while adicionar == "True":
        data.append([input("Nome: "), input("URL: ")])
        adicionar = input("Adicionar mais? ")
    banco.inserir(data)

elif escolha == 2:
    a = banco.retornar()
    for i in range(len(a)):
        print(f"{a[i][0]}, {a[i][1]}")

elif escolha == 3:
    a = banco.retornar()
    for i in range(len(a)):
        download.baixar(a[i][0], a[i][1])

banco.fechar()
