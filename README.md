# MinecraftGuess - Arquitetura AWS

Projeto prático desenvolvido para a disciplina de Redes de Computadores (GCT0149), focado na construção de uma arquitetura de serviços em nuvem na AWS com alta segurança, eficiência de custos e isolamento de rede.

## Objetivo do Projeto
O sistema consome dados da API pública Astroworld (entidades e mobs do universo Minecraft), processa as regras de negócio, persiste as informações de forma segura e as disponibiliza em um jogo web interativo.

## Arquitetura e Serviços Utilizados

A infraestrutura foi desenhada seguindo as melhores práticas de Cloud Provider, garantindo a separação de responsabilidades:

* **1 - Coleta de Dados:** Um _Collector_ em Python executado via `systemd timer` (agendamento do Linux) dentro da instância EC2. Ele busca os dados da API Astroworld, trata exceções e formata os payloads.
* **2 - Persistência de Dados (Segura):** Amazon RDS (MySQL) instanciado em uma Subnet Privada. O banco não possui IP público e só aceita conexões provindas do Security Group da API.
* **3 - Interface Web:** Amazon S3 configurado como Static Website Hosting para entrega do frontend desenvolvido em React/Vite.
* **4 - Camada Pública:** Virtual Private Cloud (VPC) dividida em:
  * **Subnet Pública:** Contém o Internet Gateway (IGW) e a instância EC2 (Nginx Proxy Reverso + FastAPI).
  * **Subnet Privada:** Contém o Amazon RDS isolado da Internet.
* **Bônus - Framework e API REST:** Backend completo estruturado com FastAPI (Python), implementando validação de dados rigorosa com Pydantic e documentação Swagger.

## Segurança e Governança
* **AWS Systems Manager (Parameter Store):** Nenhuma credencial de banco de dados ou chave sensível está armazenada no código-fonte. O backend consome os segredos dinamicamente via Parameter Store utilizando uma IAM Role atrelada à EC2.
* **Princípio do Menor Privilégio:** O Security Group do RDS está configurado com regras de Inbound restritas exclusivamente à porta 3306 e apenas para a origem do Security Group da EC2.
* **Proxy Reverso:** O Nginx recebe o tráfego HTTP na porta 80 e repassa internamente para o Uvicorn na porta 8000, não expondo o servidor de aplicação diretamente para a web.

## Observabilidade e Custos
* **Amazon CloudWatch:** O CloudWatch Agent está configurado na EC2 para capturar logs do Nginx (access/error), do Collector e do `systemd` (FastAPI), centralizando o monitoramento na nuvem.
* **Otimização Financeira:** A arquitetura evitou intencionalmente o uso de NAT Gateways e instâncias multi-AZ para manter a viabilidade econômica do projeto dentro dos limites de uma conta acadêmica (Free Tier), utilizando um fluxo eficiente de tráfego pela Subnet Pública para a ingestão de dados.

## Como Executar Localmente

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- MySQL Server

### Configuração do Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Configuração do Frontend
```bash
cd frontend
npm install
npm run dev
```

## Diagrama da Arquitetura

![Diagrama da Arquitetura](./src/assets/minecraft-guess-aws-arquitetura.svg)