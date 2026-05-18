# 📄 Documentação Mestre: SaaS Quadras de Areia

## 1. Visão Geral da Arquitetura
Sistema web monolítico focado em visualização de horários de quadras de areia, direcionamento de reservas via WhatsApp e gestão de alunos mensalistas. 
**Padrão Arquitetural:** Django MTV (Model-Template-View).
**Abordagem:** Test-Driven Development (TDD) e Extreme Programming (XP).

## 2. Stack Tecnológico Completo
* **Backend & Framework:** Python 3.x com Django 5.x
* **Banco de Dados (Dev):** SQLite (foco em agilidade inicial)
* **Banco de Dados (Prod):** PostgreSQL (integridade relacional e escalabilidade)
* **Frontend:** HTML5, CSS3, JavaScript puro (para a interface do cliente e redirecionamentos)

## 3. Variáveis de Ambiente (Configuração)
* `SECRET_KEY`: Chave de segurança do Django.
* `DEBUG`: `True` para desenvolvimento, `False` para produção.
* `DATABASE_URL`: String de conexão para o PostgreSQL (quando em produção).
* `WHATSAPP_NUMBER_OWNER`: Número de telefone do dono da quadra para receber os direcionamentos.

## 4. Estrutura de Apps e Models (Domínio)
O projeto utilizará a estrutura de módulos independentes (Apps) do Django:

* **App `core`:** Base do sistema.
  * Models: `CustomUser` (gestão de permissões do painel admin).
* **App `quadras`:** Gestão física do espaço.
  * Models: `Quadra` (nome, descrição, status ativa/inativa).
* **App `reservas`:** Controle da agenda.
  * Models: `Reserva` (quadra, data, horário_inicio, horário_fim, status, nome_cliente).
* **App `alunos`:** Gestão financeira e de recorrência.
  * Models: `Aluno` (nome, telefone, data_vencimento, status_pagamento).

## 5. Jobs e Automação
* **Job Diário (Management Command):** Script que roda todo dia às 08:00 para verificar `Alunos` com `data_vencimento` nos próximos 3 dias e alertar o painel admin.

## 6. Common Hurdles (Desafios Comuns e Soluções)
* **Problema:** Double Booking (duas pessoas clicando no mesmo horário ao mesmo tempo).
* **Solução:** Como o sistema redireciona para o WhatsApp, a fonte de verdade é a confirmação manual do dono. O banco de dados usará constraints de unicidade (`unique_together` em quadra, data e horário) para impedir que o dono aprove duas reservas colidentes no painel.
* **Problema:** Fusos Horários.
* **Solução:** Manter `USE_TZ = True` no Django e salvar tudo em UTC, exibindo o horário local apenas no frontend.

## 7. Checklist Pós-Implementação (Por Feature)
- [ ] Testes unitários escritos (e falhando).
- [ ] Código implementado.
- [ ] Testes passando (verde).
- [ ] Refatoração multisserviço sem apego ao código inicial.