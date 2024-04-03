import textwrap
from models import Deposito, Saque, ContaCorrente, PessoaFisica
from repository import Accounts, Clients, Conn
from sqlalchemy.sql import text
from datetime import datetime
from mongo_repository import histories


def main():

    clientes = [result for result in Conn.execute(text("select * from clients")).fetchall()]
    contas = [result for result in Conn.execute(text("select * from accounts")).fetchall()]

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            numero_conta =  len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            break

def menu():
    menu =  """\n
    ===============Menu================
    [d]\t deposito
    [s]\t sacar
    [e]\t Extrato
    [nc]\t nova conta
    [lc]\t listar contas
    [nu]\t novo usuário
    [q]\t sair
    """
    return input(menu)


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Nenhuma conta encontrada para o clinete @@@")
    return cliente.contas[0]


def depositar(clientes):
   cpf =  input("informe o número de cpf: ")
   cliente = filtrar_cliente(cpf, clientes)

   if not cliente:
       print("\n @@@ Cliente não encontrado.")
       return
   valor = float(input("Informe o valor do depósito: "))
   transacao = Deposito(valor)

   conta = recuperar_conta_cliente(cliente)
   if not conta:
       return

   transaction = {
       "id_conta": conta.id,
       "tipo": transacao.__class__.__name__,
       "valor": transacao.valor,
       "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
   }
   histories.insert_one(transaction)
   cliente.realizar_transacao(conta, transacao)
   Conn.execute(text(f"update accounts set balance = {conta.saldo} where id = {conta.id}"))


def sacar(clientes):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente nao encontrad0")
        return

    valor =  float(input("Informe o valor do saque: "))
    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)
    transaction = {
        "id_conta": conta.id,
        "tipo": transacao.__class__.__name__,
        "valor": transacao.valor,
        "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    histories.insert_one(transaction)
    cliente.realizar_transacao(conta, transacao)
    Conn.execute(text(f"update accounts set balance = {conta.saldo} where id = {conta.id}"))


def exibir_extrato(clientes):
    cpf =  input("Informe o cpf do cliente: ")
    cliente =  filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n Cliente nao encontrad0")
        return
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        print("\n conta nao encontrada ")
        return
    print("\n=================Extrato====================")
    transacoes =  conta.historico._transacoes
    extrato = ""
    if not transacoes:
        extrato = "Não a movimentação nesta conta."
    else:
        historico = histories.find({"id_conta": conta.id})
        for transacao in historico:
            extrato += f"\n{transacao["tipo"]}:\n\t R${transacao["valor"]:.2f}"
    print(extrato)
    print(f"\n Saldo\n\tR$ {conta.saldo:.2f}")
    print("\n============================================")


def criar_cliente(clientes):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if cliente:
        print("Cliente já existe.")
        return

    nome = input("insira o nome do cliente")
    endereco = input("insira o endereco do cliente")
    data_nascimento = datetime(2024, 4, 2, 18, 28, 23)
    Conn.execute(text(f"insert into clients(name,cpf,address,birtday)values('{nome}','{cpf}','{endereco}','{datetime(2024, 4, 2, 18, 28, 23)}')"))
    data = Conn.execute(text(f"select * from clients where cpf = '{cpf}'"))
    client_id = data.fetchall()[0].id
    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco, id=client_id)
    clientes.append(cliente)
    print("Cliente criado com sucesso")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n Cliente nao encontrad0")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    Conn.execute(text(f"insert into accounts(balance,number,agency,client_id)values('{conta.saldo}','{conta.numero}','{conta.agencia}', {cliente.id})"))
    data = Conn.execute(text(f"select * from accounts where number = '{numero_conta}'"))
    account_id = data.fetchall()[0].id
    conta.id = account_id
    contas.append(conta)
    cliente.contas.append(conta)
    print("Conta criada com sucesso.")

def listar_contas(contas):
    for conta in contas:
        print("=====================")
        print(textwrap.dedent(str(conta)))


main()