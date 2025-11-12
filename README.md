# Sistema Django - Clinica Serravet

O Sistema SerraVet é uma aplicação web desenvolvida com o **framework Django**, com o propósito de realizar o agendamento de consultas veterinárias para animais de pequeno porte, além de permitir que os tutores tenham acesso ao prontuário do seu pet. O projeto foi desenvolvido para as disciplinas Projeto de Desenvolvimento de Software, Programação para Internet e Fundamentos de Sistemas Operacionais e Sistemas Operacionais de Redes, por Erick Soares Nunes e Yasmim Lorrana Silva Lima, do curso técnico em Informática do IFRN – Campus Pau dos Ferros.

## Tecnologias Utilizadas 
- Python 3.12+
- Django 5.2+
- SQLite 
- HTML + CSS + Bootstrap 
- Docker 

## Instalação e Execução do Sistema

1. Clone o repositório:
   ```bash
   git clone https://github.com/ErickSN25/Final_Project.git
   cd Final_Project

2. Crie o ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate

3. Instale django 
   ```bash
   pip install django

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt


5. Execute as migrações:
   ```bash
   python manage.py makemigrations
   python manage.py migrate

6. Execute o servidor:
   ```bash
   python manage.py runserver


   




