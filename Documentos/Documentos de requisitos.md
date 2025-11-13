**Documento de Requisitos**

**1 Introdução**

**1.1 Propósito do documento**

Este documento propõe a especificação dos requisitos do **sistema SerraVet**, um sistema de consultas online, que será aplicado na clínica veterinária de pequeno porte.

**1.2 Escopo do produto**

O sistema tem como objetivo auxiliar o gerenciamento de consultas médicas do Animal de estimação de forma online.

**1.3 Visão geral do documento**

Este documento apresenta uma visão geral do sistema, descrevendo suas funcionalidades e delimitações de requisitos, seja pelo contexto no qual será aplicado ou por questões de segurança.

**2 Descrição Geral**

O sistema auxilia o gerenciamento de consulta, no qual somente o administrador poderá controlar o fluxo de clientes cadastrados. Dando ao cliente(Usuário) a possibilidade de solicitar consultas via Web site.

**2.1 Perspectiva do Produto**

O sistema opera com uma máquina-servidor que gerencia o banco de dados e controla o acesso a informações, as quais podem ser consultadas, modificadas ou excluídas, de acordo com o grau de permissão do usuário logado. 

**2.2 Restrições Gerais**

Para acessar o sistema, cada cliente terá que fazer seu cadastro. O administrador irá cadastrar os veterinários da clínica e o atendete, mas o acesso do veterinário e do atentende no sistema ocorrerá por meio de login. O administrador terá acesso às funcionalidades de gerenciamento de cadastro do animal de estimação do cliente. O Veterinário terá acesso aos dados básicos dos clientes e acesso a todos os dados do Animal, podendo visualizar informações das consultas e gerar os prontuários. 

**3 Requisitos**

**3.1 Requisitos Funcionais**

| RF001 | O administrador deve realizar o cadastro e a manutenção de dados de Veterinários. |
| :---- | ----- |
| **Detalhes** |Dados dos Veterinários: Nome & Sobrenome, CPF, CRMV, gamil e senha |
| **Restrições** | O veterinário obrigatóriamente precisa ter o CRMV ativo | 
| **Responsável** | Administrador |
| **Importância** | **\[ X \] Obrigatório** \[  \] Importante  \[  \] Desejável |

| RF002 | O adminstrador deve realizar cadastro e a manutenção de dados do Atendente | 
| :---- | ----- |
| **Detalhes** |Dados do Atendente: Nome & sobrenome, CPF,telefone, gmail e senha. |
| **Restrições** | \- |
| **Responsável** | Administrador |
| **Importância** | **\[ X \] Obrigatório** \[  \] Importante  \[  \] Desejável |

| RF003 | Atendente irá realizar o cadastro de quadros de horários de consultas disponiveis e relacionar ao veterinário. |
| :---- | ----- |
| **Detalhes** | Selecionar dias e horas de forma personalizada para cada Veterinário. | 
| **Importância** | **\[ X \] Obrigatório** \[  \] Importante  \[  \] Desejável |


| RF004 | Cliente deve realizar o cadastro para acessar o sistema |
| :---- | ----- |
| **Detalhes** | Dados Obrigatórios: nome & Sobrenome, CPF, Gmail e telefone |
| **Importância** | **\[ X \] Obrigatório** \[  \] Importante  \[  \] Desejável |

| RF005 | O cliente cadastrado poderá solicitar consulta para seu(s) Animais de Estimação |
| :---- | ----- |
| **Detalhes** | Dados Obrigatórios do animal: nome, espécie, peso atual, vacinas em dia(SIM/NÃO). Dados opcionais: raça, alergias, doenças. Será possível também escolher dia, horário e Veterinário, entre os disponíveis. |
| **Importância** | **\[ X \] Obrigatório** \[  \] Importante  \[  \] Desejável |


| RF006 | O Veterinário deve poder gerar o prontuário sobre a consulta realizada. |
| :---- | ----- |
| **Detalhes** | Dados do prontuário: identificador do pet, diagnóstico, sintomas e observações. Isso enquanto ainda estive ocorrendo o acompanhamento do animal da estimação. |
| **Importância** | **\[ X \] Obrigatório** \[  \] Importante  \[  \] Desejável |

| RF007 | Veterinário deve Inserir receita do medicamento virtual |
| :---- | ----- |
| **Detalhes** | Documento em pdf que será disponibilizado na página do tutor. Para o sistema, o documento será apenas anexado. A criação e edição do documento será feita por softwares de terceiros.  |
| **Importância** | \[  \] Obrigatório **\[ X \] Importante**  \[  \] Desejável |


**3.1 Requisitos não Funcionais**


| RNF001 | O administrador irá fazer o backup do banco de dados a cada 7 dias |
| :---- | :---- |
| **Detalhes** | Os backup serão feitos de forma configurada e iniciada em um dia específico pelo administrador. |


| RNF002 | Identificação de acesso deve ser feito via login |
| :---- | :---- |
| **Detalhes** | Os tipos de identificações são referentes o administrador, Veterinários, Atendente e clientes.. |

| RNF003 | Serviço deve estar disponível 24 horas por dia |
| :---- | :---- |
| **Detalhes** | Disponibilidade |

| RNF004 | Veterinários deve poder manipular os dados da consulta até o fechamento do chamado |
| :---- | :---- |
| **Detalhes** | Após isso, poder somente adicionar comentários. |


| RNF005 | Somente o veterinário e o tutor podem ver os dados da consultas |
| :---- | :---- |
| **Detalhes** | Privacidade.|

| RNF006 | Somente o administrador pode ver os dados do veterinário e Atendente |
| :---- | :---- |
| **Detalhes** | Privacidade |



