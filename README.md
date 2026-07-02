 Validação e Formatação de Telefones Brasileiros
**Biblioteca-tempero:** `phonenumbers`  
**API sugerida:** `https://brasilapi.com.br/api/ddd/v1/{ddd}`

### Descrição geral
Aplicação que valida, formata e enriquece números de telefone brasileiros. A biblioteca `phonenumbers` deve ser usada para parsear números em diversos formatos, determinar tipo (fixo/móvel), validar e formatar para padrões nacional e internacional.

### Menu inicial e comportamento

1. **Validar e formatar número**  
   - Solicita um número de telefone (com ou sem DDD, com ou sem `+55`, com ou sem máscara).  
   - Usa a biblioteca-tempero para parsear e validar.  
   - Determina se é fixo ou móvel.  
   - Exibe: número formatado no padrão nacional, número formatado no padrão internacional, tipo e status de validade.  
   - Armazena no SQLite com timestamp da consulta.

2. **Consultar DDD**  
   - Solicita um DDD (dois dígitos).  
   - Consulta a API para obter estado e lista de cidades.  
   - Usa a biblioteca-tempero para validar se o DDD informado é plausível no contexto brasileiro.  
   - Armazena no SQLite: DDD, estado, lista de cidades (pode ser serializada).  
   - Exibe em tabela `rich`: estado, quantidade de cidades e as cidades associadas.

3. **Gerar números válidos por região**  
   - Solicita um estado (UF) ou um DDD.  
   - Se informado UF, consulta a API para descobrir os DDDs daquele estado.  
   - Gera uma quantidade informada de números de telefone fictícios, mas semanticamente válidos para aquela região, usando a biblioteca-tempero.  
   - Armazena no SQLite marcando como `ficticio = 1`.  
   - Exibe em tabela `rich`.

4. **Buscar histórico**  
   - Lista todos os números consultados ou gerados armazenados no SQLite.  
   - Permite filtro por tipo (fixo/móvel/fictício) ou por estado.  
   - Exibe em tabela `rich` com todas as colunas relevantes.

5. **Comparar dois números**  
   - Solicita dois números em formatos possivelmente diferentes.  
   - Usa a biblioteca-tempero para extrair a representação canônica de cada um.  
   - Informa se são equivalentes (mesmo número apesar da formatação diferente) ou distintos.

### Tarefas bônus
- Implementar uma "lista de bloqueio" local: se um número estiver cadastrado em uma tabela de reclamações (inseridas manualmente pelo usuário), a aplicação deve alertar ao consultá-lo.
- Calcular um "custo de ligação" simulado: fixo-para-fixo mesmo DDD = gratuito; fixo-para-móvel = tarifa X; DDD diferente = tarifa Y; exibir o custo ao comparar origem e destino.
- Gerar um arquivo de contato no formato vCard (`.vcf`) contendo um número válido gerado, pronto para importação.
