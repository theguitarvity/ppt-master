# Feature Specification: Gerar Deck FACOM/UFMS Animado a partir de CONTEXT.md

**Feature Branch**: `001-generate-facom-deck`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "Leia integralmente o CONTEXT.md e especifique a primeira vertical slice descrita nas seções 8, 9 e 15: gerar um PPTX FACOM/UFMS completo e animado a partir de um CONTEXT.md, inicialmente no Codex, sem reescrever o motor existente."

## Clarifications

### Session 2026-07-27

- Q: O que acontece quando um gate de qualidade (SVG, OOXML, overflow, brand lint) falha —
  o PPTX ainda é gravado em disco ou a exportação fica bloqueada até todos os gates passarem?
  → A: Gate rígido — nenhum PPTX é gravado em disco enquanto qualquer gate falhar.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gerar o deck real da palestra a partir de um único CONTEXT.md (Priority: P1)

Uma pessoa (o mantenedor) fornece um único `CONTEXT.md` — com frontmatter YAML de parâmetros
operacionais e corpo Markdown com o conteúdo da palestra — e solicita a geração de uma
apresentação. O sistema valida e normaliza esse contexto, inicializa um projeto PPT Master,
aplica o perfil de marca FACOM/UFMS, executa o pipeline de geração existente até produzir um
PPTX 16:9 completo (abertura, conteúdo e encerramento), com notas do apresentador e com
transições/animações intencionais quando solicitadas. O host inicial é o Codex, mantendo o
Claude Code funcional sem regressão.

**Why this priority**: é o primeiro incremento obrigatório do produto — sem ele não existe
"palestra amanhã" nem MVP demonstrável; todo o restante (QA consolidado, mensagens de erro
mais ricas, segundo host) só tem valor depois que esse caminho fim-a-fim funciona.

**Independent Test**: fornecer um `CONTEXT.md` válido com `brand.profile: facom-ufms` e
`delivery.animations: purposeful` e executar o caminho feliz documentado do Codex; o teste
passa se um PPTX 16:9 é produzido, abre corretamente, contém as três seções obrigatórias,
exibe a marca institucional correta e possui animações validadas — sem edição manual de
scripts de geração.

**Acceptance Scenarios**:

1. **Given** um `CONTEXT.md` completo e válido referenciando `brand.profile: facom-ufms`,
   **When** o caminho feliz de geração é executado no Codex, **Then** um PPTX 16:9 nativo e
   editável é produzido, contendo slides de abertura, conteúdo e encerramento com a marca
   institucional aplicada corretamente.
2. **Given** o mesmo `CONTEXT.md` com `delivery.speaker_notes: true`, **When** a geração é
   concluída, **Then** cada slide do PPTX contém notas do apresentador correspondentes ao seu
   conteúdo.
3. **Given** o mesmo `CONTEXT.md` com `delivery.animations: purposeful`, **When** a geração é
   concluída, **Then** o deck contém transições e animações por objeto que passam na
   validação, sem referências de âncora inexistentes ou conflitantes.
4. **Given** um `CONTEXT.md` com `delivery.animations: none`, **When** a geração é concluída,
   **Then** o PPTX resultante não contém nenhuma animação injetada pelo motor.
5. **Given** um `CONTEXT.md` válido cujo deck gerado falha em pelo menos um gate de qualidade
   (ex.: overflow detectado), **When** a exportação é executada, **Then** nenhum arquivo PPTX é
   gravado em disco e a pessoa recebe a lista exata dos gates que falharam.

---

### User Story 2 - Corrigir um CONTEXT.md incompleto ou ambíguo antes de gerar (Priority: P2)

Uma pessoa autora fornece um `CONTEXT.md` com campos obrigatórios ausentes, mal formatados ou
desconhecidos. Em vez de falhar silenciosamente ou gerar um deck incorreto, o sistema informa
exatamente qual campo está com problema e o que é esperado, e produz um brief normalizado que
documenta todos os defaults aplicados quando um campo foi omitido.

**Why this priority**: sem isso, o caminho "palestra amanhã" é frágil — qualquer erro de
digitação no frontmatter levaria a um deck incorreto ou a uma falha opaca, tornando a iteração
sobre o `CONTEXT.md` custosa. É a segunda prioridade porque depende do pipeline básico da
User Story 1 já existir, mas não bloqueia a primeira geração bem-sucedida.

**Independent Test**: fornecer um `CONTEXT.md` com um campo obrigatório ausente e um campo com
tipo incorreto; o teste passa se as mensagens de erro apontam exatamente os campos problemáticos
e o que é esperado. Em seguida, fornecer um `CONTEXT.md` mínimo válido e confirmar que ele
prossegue sem qualquer intervenção manual, com um brief normalizado listando os defaults usados.

**Acceptance Scenarios**:

1. **Given** um `CONTEXT.md` sem o campo obrigatório de título da apresentação, **When** a
   validação é executada, **Then** o sistema reporta um erro acionável identificando o campo
   ausente, sem iniciar a geração.
2. **Given** um `CONTEXT.md` mínimo mas válido, **When** a validação é executada, **Then** o
   sistema produz um brief normalizado registrando cada default aplicado e prossegue para a
   inicialização do projeto sem intervenção manual.
3. **Given** um `CONTEXT.md` com um campo de frontmatter desconhecido, **When** a validação é
   executada, **Then** o sistema emite um aviso não bloqueante e preserva o corpo Markdown
   original sem perda de conteúdo.

---

### User Story 3 - Obter um relatório único de conformidade sobre o deck gerado (Priority: P3)

Uma pessoa revisora (o mantenedor ou um colaborador) quer confirmar, antes de apresentar, que o
PPTX gerado passa em todos os gates de qualidade — schema, checker de SVG, auditoria OOXML,
renderização de todas as páginas, checagem de overflow/clipping e brand lint — sem precisar
inspecionar manualmente cada verificação isoladamente.

**Why this priority**: reforça a confiança no artefato entregue pela User Story 1, mas o deck
já pode ser gerado e inspecionado visualmente (ainda que manualmente) sem esse relatório
consolidado existir; por isso vem depois das duas primeiras histórias.

**Independent Test**: executar a suíte de conformidade sobre um deck já gerado pela User Story
1; o teste passa se o relatório único enumera, para cada gate, o resultado (passou/falhou), o
host usado e as capacidades declaradas, permitindo identificar qualquer problema sem reabrir
os artefatos intermediários manualmente.

**Acceptance Scenarios**:

1. **Given** um PPTX já gerado a partir de um `CONTEXT.md` válido, **When** a suíte de
   conformidade é executada, **Then** um relatório único lista o resultado de cada gate de
   qualidade (schema, SVG, OOXML, render, overflow, brand lint).
2. **Given** um deck com uma violação de marca conhecida (ex.: proporção do logo distorcida),
   **When** a suíte de conformidade é executada, **Then** o gate de brand lint falha e o
   relatório aponta a violação específica.

---

### Edge Cases

- O que acontece quando o `CONTEXT.md` declara `brand.profile: facom-ufms` mas um slide tem
  mais de 40% de preenchimento escuro no fundo? O sistema deve selecionar automaticamente a
  versão negativa/branca da marca institucional nesse slide, não a versão colorida padrão.
- Como o sistema se comporta quando os assets oficiais da marca FACOM/UFMS não estão
  disponíveis (sem rede ou download ainda não realizado) no momento da geração? A geração deve
  falhar de forma clara e explícita, nunca substituir o logo por uma versão reconstruída ou
  aproximada por IA.
- O que acontece quando `slide_count: auto` é usado com um corpo de conteúdo muito esparso? O
  brief normalizado deve registrar explicitamente a contagem de slides inferida como um default
  aplicado, não apenas gerar um resultado silenciosamente arbitrário.
- Como o sistema se comporta quando uma capacidade declarada do host Codex (ex.: confirmação
  interativa) está indisponível na sessão atual? O adapter deve declarar essa limitação e usar
  um fallback documentado, nunca simular sucesso ou pular a etapa silenciosamente.
- O que acontece quando o `CONTEXT.md` de entrada referencia um PPTX bruto como "template"? O
  sistema deve recusar tratá-lo automaticamente como template do pipeline SVG, mantendo a
  separação das quatro rotas do produto.
- O que acontece quando um gate de qualidade (SVG, OOXML, overflow, brand lint) falha? A
  exportação do PPTX é bloqueada — nenhum arquivo PPTX é gravado em disco até que todos os
  gates passem — e a pessoa recebe a lista exata de falhas para corrigir e tentar novamente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE aceitar um único arquivo `CONTEXT.md`, com frontmatter YAML e
  corpo Markdown, como entrada suficiente para iniciar um projeto de deck de palestra
  FACOM/UFMS.
- **FR-002**: O sistema DEVE validar o frontmatter do `CONTEXT.md` contra um schema versionado
  e DEVE reportar erros acionáveis que identifiquem o campo problemático e o valor/tipo
  esperado.
- **FR-003**: O sistema DEVE produzir um brief normalizado e versionado que registre todo
  default aplicado quando um campo foi omitido, sem descartar ou alterar o conteúdo original do
  corpo Markdown.
- **FR-004**: O sistema DEVE encaminhar um `CONTEXT.md` válido através do pipeline de geração
  já existente (Strategist → Executor → exportação), sem introduzir uma quinta rota de produto
  nem contornar a separação já existente entre as quatro rotas.
- **FR-005**: O sistema DEVE aplicar o perfil de marca FACOM/UFMS — incluindo a cor
  institucional oficial (`#0088B7`), os assets de logo oficiais e a seleção de versão
  positiva/negativa da marca conforme o contraste do fundo — a todo slide gerado quando
  `brand.profile: facom-ufms` estiver definido.
- **FR-006**: O sistema DEVE recusar ou sinalizar (nunca substituir silenciosamente) a geração
  quando um asset oficial de marca FACOM/UFMS necessário estiver ausente ou não puder ser
  verificado, em vez de aproximá-lo ou reconstruí-lo.
- **FR-007**: O sistema DEVE produzir um deck completo em formato 16:9 contendo, no mínimo,
  seções de abertura, conteúdo e encerramento, em conformidade com os padrões institucionais de
  slide da FACOM/UFMS.
- **FR-008**: O sistema DEVE gerar notas do apresentador para cada slide quando
  `delivery.speaker_notes: true` estiver definido no `CONTEXT.md`.
- **FR-009**: O sistema DEVE aplicar transições e animações semânticas por objeto, validadas,
  quando `delivery.animations: purposeful` estiver definido, e DEVE produzir um deck sem
  qualquer movimento injetado quando `delivery.animations: none` estiver definido.
- **FR-010**: O sistema DEVE executar validação estática de SVG, auditoria de relações OOXML,
  renderização completa de todas as páginas com contact sheet, e checagem de
  overflow/clipping/placeholder antes de reportar um deck gerado como concluído.
- **FR-011**: O sistema DEVE executar uma checagem de brand lint que falha quando uma violação
  conhecida de marca FACOM/UFMS (cor incorreta, proporção de logo distorcida, versão de marca
  incompatível com o fundo) estiver presente no deck gerado.
- **FR-012**: O sistema DEVE executar o caminho completo de `CONTEXT.md` até PPTX no host
  Codex como primeiro host suportado, mantendo o caminho já existente no Claude Code funcional
  sem regressão.
- **FR-013**: O registro de proveniência de cada deck gerado DEVE capturar URL/origem, data de
  captura e condição de licença/uso para toda alegação factual externa, imagem e asset
  institucional usado.
- **FR-014**: O sistema NÃO DEVE modificar, reescrever ou substituir os scripts, workflows ou a
  separação das quatro rotas do motor de geração existente para entregar esta vertical slice;
  nova capacidade DEVE ser adicionada como módulos aditivos (schema/parser de `CONTEXT.md`,
  pacote de marca, declaração de capacidades de host).
- **FR-015**: O sistema DEVE declarar, para o host Codex, quais capacidades (geração de imagem,
  browser, subagentes paralelos, confirmação interativa, inspeção de imagem, renderização de
  PPTX) estão disponíveis, e DEVE usar um fallback documentado ou declarar explicitamente a
  limitação sempre que uma capacidade declarada estiver ausente — nunca pular uma etapa
  silenciosamente.
- **FR-016**: O sistema DEVE fornecer um único comando/sequência de instruções documentado e
  reproduzível para gerar um deck de palestra FACOM/UFMS no host Codex.
- **FR-017**: O sistema DEVE fornecer uma fixture de smoke test derivada de uma palestra
  FACOM/UFMS real, utilizável para verificar o caminho fim-a-fim sem entrada manual de dados.
- **FR-018**: Para o host GitHub Copilot, esta vertical slice DEVE apenas definir e documentar
  a interface de capacidades (o mesmo contrato usado pelo Codex — geração de imagem, browser,
  subagentes paralelos, confirmação interativa, inspeção de imagem, renderização de PPTX) que um
  futuro adapter Copilot precisaria implementar. Um adapter Copilot funcional capaz de executar o
  caminho feliz de geração NÃO é exigido nesta slice e fica explicitamente para uma iteração
  posterior.
- **FR-019**: O sistema DEVE bloquear a escrita do PPTX em disco enquanto qualquer gate de
  qualidade (FR-010, FR-011) não passar; nenhum arquivo PPTX parcial ou não conforme é
  entregue à pessoa usuária até que todos os gates de qualidade passem, e a falha DEVE ser
  reportada com a lista exata dos gates que não passaram. Um gate declarado `skipped` por
  ausência de capacidade do host (FR-015) NÃO conta como aprovado para este bloqueio — DEVE
  ser tratado como equivalente a uma falha para efeito de liberar a exportação, distinguindo
  apenas o motivo (capacidade indisponível vs. violação real) no relatório.

### Key Entities *(include if feature involves data)*

- **CONTEXT.md / Contexto da Apresentação**: entrada única em Markdown com frontmatter YAML;
  contém identidade da apresentação, público, objetivo, duração, contagem de slides, idioma,
  perfil de marca, preferências de entrega (animações, notas, citações) e modo de qualidade.
- **Brief Normalizado**: saída versionada e legível por máquina da validação/normalização do
  `CONTEXT.md`; registra defaults aplicados e avisos; alimenta o Strategist sem duplicar
  `design_spec.md`.
- **Pacote de Marca FACOM/UFMS**: coleção versionada de tokens de cor/tipografia, assets de logo
  oficiais, metadados de proveniência e regras de brand lint; referenciado por qualquer Deck que
  use `brand.profile: facom-ufms`.
- **Declaração de Capacidades do Host**: registro por host (inicialmente Codex) de quais
  capacidades (geração de imagem, browser, subagentes paralelos, confirmação interativa,
  inspeção de imagem, renderização de PPTX) estão disponíveis, consumido pelos workflows para
  escolher fallbacks.
- **Relatório de Conformidade/Entrega**: saída consolidada dos gates de QA (schema, SVG,
  auditoria OOXML, render, overflow, brand lint) para um deck gerado, incluindo host e contexto
  de capacidades.
- **Deck FACOM "Palestra Técnica 16:9"**: workspace de template reutilizável que aplica o
  Pacote de Marca FACOM/UFMS a uma estrutura de páginas (canvas, papéis de página, slots)
  voltada a palestras/aulas técnicas; referencia a autoridade de identidade do Pacote de Marca
  sem duplicar seus tokens.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma pessoa com um `CONTEXT.md` completo e válido obtém um PPTX FACOM/UFMS
  finalizado e abrível sem precisar editar manualmente scripts de geração nem intervir além dos
  gates de confirmação já previstos no pipeline.
- **SC-002**: 100% dos slides de um deck FACOM/UFMS gerado são renderizados com sucesso e
  aparecem no contact sheet, com zero ocorrência de overflow, clipping ou sobreposição não
  intencional.
- **SC-003**: Todo slide de um deck FACOM/UFMS gerado exibe a marca institucional na versão
  (positiva ou negativa) apropriada ao seu fundo, com zero falhas de brand lint.
- **SC-004**: Quando `delivery.animations: purposeful` é solicitado, 100% da configuração de
  animação/transição validada do deck passa na validação, sem referências de objeto não
  resolvidas ou conflitantes.
- **SC-005**: O deck real da palestra do mantenedor, usado como fixture de aceitação, é avaliado
  pela pessoa que o solicitou como uma apresentação utilizável — não apenas como um arquivo
  tecnicamente válido.
- **SC-006**: Uma pessoa nova, seguindo apenas as instruções documentadas do caminho feliz do
  Codex, consegue reproduzir um deck FACOM/UFMS funcional a partir de um `CONTEXT.md` novo, sem
  precisar de passos não documentados.
- **SC-007**: Toda imagem externa, alegação factual e asset institucional usado em um deck
  gerado tem proveniência rastreável (origem, data de captura, condição de uso) registrada nos
  artefatos do projeto.

## Assumptions

- Não é exigida narração em áudio ou vídeo para esta vertical slice; a entrega é um PPTX nativo
  totalmente animado, sem áudio/vídeo (essa geração permanece escopo de segunda iteração,
  conforme CONTEXT.md §8.2).
- O MVP suporta apenas o formato de tela `ppt169`; outros formatos ficam fora do escopo desta
  slice.
- Campos de frontmatter do `CONTEXT.md` desconhecidos/não reconhecidos geram um aviso (não um
  erro bloqueante), consistente com a abordagem do projeto de documentar defaults em vez de
  bloquear por ambiguidade não crítica.
- Há acesso à internet (ao menos intermitente) durante a criação do Pacote de Marca para
  realizar o download único, com proveniência registrada, dos assets oficiais FACOM/UFMS; a
  geração em tempo de execução em si não exige rede uma vez que os assets já estejam
  armazenados localmente.
- Aprovação formal da direção/Agecom não é necessária para entregar esta vertical slice, porque
  o primeiro caso de aceitação (a palestra do próprio mantenedor) é uso interno acadêmico, já
  permitido pelo manual UFMS; aprovação para distribuição externa/pública permanece fora de
  escopo.
- A tipografia institucional oficial UFMS (personalização de Futura XBlkCn BT, Swis721 Cn BT) é
  respeitada nos assets de logo/assinatura entregues sem alteração; o texto de corpo e títulos
  dos decks gerados usa fontes livres/instaláveis de fallback, em vez de empacotar tipografias
  proprietárias.
- A verificação de renderização/abertura (gate de Auditoria OOXML) usa o renderizador
  compatível com PowerPoint ou LibreOffice já disponível na ferramentaria existente do projeto;
  provisionar um renderizador específico de CI está fora do escopo desta slice.
- O GitHub Copilot recebe apenas a definição da interface de capacidades nesta slice (decisão
  confirmada com o mantenedor); um adapter Copilot funcional é explicitamente adiado para uma
  iteração posterior e não bloqueia a aceitação desta feature.
