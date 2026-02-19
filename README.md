# 🍔 Lanchonete — Sistema de Controle de Entregas e Caixa

Sistema Django com tema dark (preto e vermelho alaranjado) para controle de entregas, motoboys e caixa.

## 🚀 Instalação

### Pré-requisitos
- Python 3.10+

### Passos

```bash
# 1. Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Criar banco de dados
python manage.py migrate

# 4. Criar superusuário (opcional, para acessar /admin)
python manage.py createsuperuser

# 5. Rodar o servidor
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

---

## 📋 Funcionalidades

### 🛵 Controle de Entregas
- **Nova Rota**: Seleciona o motoboy e adiciona entregas uma a uma
  - Por entrega: cliente, endereço, volumes, forma de pagamento (dinheiro/cartão/online), valor, taxa de entrega
- **Despachar**: Registra horário de saída do motoboy
- **Registrar Retorno**: Marca o retorno do motoboy
- **Conferência de Retorno**:
  - Informa dinheiro entregue pelo motoboy
  - Marca status de cada entrega (entregue/não entregue)
  - Marca comprovantes recebidos
  - Calcula diferença automaticamente
- **Relatório de Rota**: Resumo completo com conferência financeira

### 👤 Motoboys
- Cadastro com nome, telefone e valor fixo por turno
- Relatório por período com: rotas, entregas, volumes, dinheiro coletado, taxas

### 💰 Controle de Caixa
- **Abertura**: Informa notas e moedas (R$200, R$100, R$50, R$20, R$10, R$5, R$2 e todas as moedas)
- **Fechamento**: Conta novamente com comparativo automático
- **Relatório**: Comparativo linha a linha com diferenças destacadas

---

## 🏗️ Estrutura do Projeto

```
lanchonete/
├── manage.py
├── requirements.txt
├── lanchonete/          # Configurações Django
│   ├── settings.py
│   └── urls.py
├── entregas/            # App de entregas e motoboys
│   ├── models.py        # Motoboy, Rota, Entrega
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── caixa/               # App de controle de caixa
│   ├── models.py        # Caixa, ContaCaixa
│   ├── views.py
│   └── urls.py
└── templates/
    ├── base.html        # Layout principal dark
    ├── entregas/        # Templates de entregas
    ├── caixa/           # Templates de caixa
    └── relatorios/      # Templates de relatórios
```

---

## 🎨 Visual
- Modo Dark: fundo preto (#0d0d0d), cards (#1a1a1a)
- Cores de destaque: vermelho alaranjado (#e8390e)
- Bootstrap 5.3 com Bootstrap Icons
- Totalmente responsivo (mobile-first)
- Relógio em tempo real na navbar
