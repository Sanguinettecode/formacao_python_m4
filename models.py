from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco, id=None):
        super().__init__(endereco)
        self.id = id
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente, id=None):
        self.id = id
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self.cliente = cliente
        self.historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    def sacar(self, valor):
        saldo = self._saldo
        excedeu_limite = valor > saldo

        if excedeu_limite:
            print("\n @@@ Operação falhou. Você não tem saldo suficiente")
        elif valor > 0:
            self._saldo -= valor
            print("\n @@@ Saque realizado com sucesso.")
            return True
        else:
            print("\n @@@ Operação falhou. O valor informado é inválido.")
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n @@@ Deposito realizado com sucesso.")
        else:
            print("\n @@@ Operação falhou. Valor informado é inválido")
            return False

        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=1000, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saque = len([
            transacao for transacao in self.historico._transacoes if transacao["tipo"] == Saque.__name__
        ])

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saque > self.limite_saques

        if excedeu_limite:
            print("\n @@@ Operação falhou. Limite de saque é maior que o permitido. @@@")

        elif excedeu_saques:
            print("\n @@@ Operação falhou. Limite de saques por dia foi excedido. @@@")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""
            Agência: \t{self._agencia}
            C/C:\t{self._numero}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    def adicionar_transacao(self, transacao):
        transaction = {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }

        self._transacoes.append(transaction)

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(cls, conta):
        pass
class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

