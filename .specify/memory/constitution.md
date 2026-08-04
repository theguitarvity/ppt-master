<!--
Sync Impact Report — Constitution update
Version change: [TEMPLATE] (unratified) → 1.0.0
Modified principles: n/a (initial ratification — all 10 principles newly defined)
Added principles:
  I. Núcleo Único, Adapters Finos
  II. Artefatos e Contratos Determinísticos Acima do Modelo
  III. Preservação das Quatro Rotas do PPT Master
  IV. SVG Canônico Restrito como IR de Geração
  V. Fidelidade, Editabilidade e Validação Antes de Velocidade
  VI. Marca FACOM/UFMS como Política Verificável
  VII. Degradação Explícita por Capacidade do Host
  VIII. Proveniência de Fontes e Assets
  IX. Paridade Entre Hosts Sem Identidade Byte a Byte
  X. Entrega Incremental Ancorada na Palestra Real
Added sections: Quality Gates; Fronteiras Não Negociáveis Herdadas do Upstream; Governança
  (processo de emenda, política de versionamento, revisão de conformidade)
Removed sections: none (template placeholders replaced with concrete content)
Templates requiring updates:
  ✅ .specify/templates/plan-template.md — Constitution Check gate is generic and already
     compatible; no structural edit required. Plans should cite applicable principles by
     numeral (I–X) when filling that gate.
  ✅ .specify/templates/spec-template.md — no changes required; scope/requirements sections
     are principle-agnostic.
  ✅ .specify/templates/tasks-template.md — no changes required; task categorization is
     principle-agnostic.
  ⚠ .specify/templates/commands/*.md — directory not present in this Spec Kit installation;
     nothing to update.
  ⚠ AGENTS.md / skills/ppt-master/SKILL.md — not modified by this command; recommend a
     follow-up pass to cross-reference this constitution once the FACOM vertical-slice
     spec/plan exist (tracked as a manual follow-up, not a placeholder left in this file).
Follow-up TODOs: none blocking. RATIFICATION_DATE is set to the date of this initial
  ratification (2026-07-27), matching CONTEXT.md's discovery date, since no prior ratified
  version of this constitution existed (the file previously held only template placeholders).
-->

# PPT Master FACOM Multimodelo Constitution

## Core Principles

### I. Núcleo Único, Adapters Finos

Workflows, referências, schemas, scripts e templates DEVEM viver em um único núcleo
compartilhado entre todos os hosts (Codex, GitHub Copilot, Claude Code e hosts futuros).
Arquivos específicos de host DEVEM se limitar a tradução de descoberta, comando e
capacidade — NUNCA a lógica de domínio, regras de rota, contratos de schema ou regras de
marca. Toda funcionalidade nova DEVE ser implementada no núcleo primeiro; um adapter só
pode adicionar código quando estritamente necessário para expor a mesma capacidade ao
host (ex.: descoberta de skill, formato de comando).

**Rationale**: evita manutenção triplicada e divergência silenciosa de comportamento
entre hosts — risco explicitamente identificado no produto ("prompts divergirem por
host" → "manutenção triplicada").

### II. Artefatos e Contratos Determinísticos Acima do Modelo

`CONTEXT.md`, o brief normalizado, `design_spec.md`, `spec_lock.md`, o SVG canônico, os
relatórios de validação e o PPTX final SÃO os contratos do sistema. Nenhum comportamento
essencial pode depender de memória implícita, estilo ou heurística não documentada de um
modelo específico. Roteamento entre as quatro rotas, schemas, resolução de assets,
exportação PPTX, validação e regras de marca DEVEM ser determinísticos e reproduzíveis a
partir dos artefatos do projeto. Criatividade é permitida apenas em narrativa, composição
visual e redação, dentro dos limites desses contratos.

**Rationale**: contratos versionados e determinismo nos pontos estruturais são o que
tornam a paridade entre hosts e a reprodutibilidade auditável possíveis, em vez de
dependerem do comportamento incidental de um LLM específico.

### III. Preservação das Quatro Rotas do PPT Master

As quatro rotas mutuamente exclusivas — Generate PPTX, Create Template, Fill Native PPTX
e Enhance Native PPTX — DEVEM permanecer distintas e não podem ser colapsadas, fundidas
ou substituídas por uma rota genérica sem uma decisão arquitetural explícita (ADR). Um
PPTX bruto NUNCA é tratado automaticamente como template do pipeline SVG; rotas nativas
(Fill/Enhance) NUNCA passam pela regeneração SVG; alterações de Master/Layout NUNCA são
inferidas e enxertadas em arquivos existentes sem passar por Create Template.

**Rationale**: essa separação evita perda de fidelidade visual e ambiguidade de contrato
entre "gerar do zero" e "editar o que já existe"; é uma fronteira herdada do upstream que
não deve ser quebrada implicitamente.

### IV. SVG Canônico Restrito como IR de Geração

O pipeline Generate PPTX e Create Template DEVEM usar exclusivamente a gramática SVG
restrita definida em `shared-standards-core.md`, `semantic-svg.md`,
`native-data-interface.md` e `pptx-structure-interface.md` como representação
intermediária. SVG arbitrário NUNCA é aceito como se fosse uma linguagem suportada.
`svg_output/` é a única fonte editada manualmente; `svg_final/` é derivado apenas para
preview e NUNCA é fonte da exportação nativa.

**Rationale**: a gramática restrita é o que garante geração razoavelmente confiável por
LLM, inspeção em navegador, coordenadas absolutas depuráveis e transformação
determinística para DrawingML/OOXML.

### V. Fidelidade, Editabilidade e Validação Antes de Velocidade

O PPTX final DEVE ser apresentável, nativamente editável (formas, texto e objetos reais,
não screenshots) e DEVE passar pela validação estática e pela auditoria pós-exportação
antes de ser considerado concluído. Perfis de execução rápida (ex.: `quick-test`) PODEM
reduzir o número de iterações e de gates interativos humanos, mas NUNCA podem eliminar os
gates críticos de qualidade definidos em Quality Gates abaixo.

**Rationale**: trocar qualidade por velocidade de forma indiscriminada é um não objetivo
herdado explícito; velocidade sem fidelidade produz um artefato tecnicamente válido mas
inutilizável como apresentação real.

### VI. Marca FACOM/UFMS como Política Verificável

Regras de identidade visual FACOM/UFMS — cor institucional `#0088B7`, tipografias
oficiais, o Grafo de Petersen como motivo estrutural, versões positiva/negativa por
contraste de fundo, área de proteção e hierarquia de convivência de marcas — DEVEM
existir como tokens, assets versionados e regras de lint automatizadas, NUNCA apenas como
texto solto em um prompt. O símbolo FACOM e os logos oficiais UFMS NUNCA são redesenhados
ou reconstruídos por IA; DEVEM ser baixados uma única vez, versionados com metadados de
origem, e usados sem distorção. Um brand lint DEVE falhar a validação quando detectar uma
violação conhecida (cor incorreta, proporção distorcida, versão de marca incompatível com
o fundo).

**Rationale**: uso incorreto da marca institucional é um risco explicitamente
identificado; verificação automatizável é necessária porque revisão humana esporádica não
escala com a geração assistida por IA.

### VII. Degradação Explícita por Capacidade do Host

Cada adapter de host DEVE declarar suas capacidades reais (geração de imagem, browser,
subagentes paralelos, confirmação interativa, inspeção de imagem, renderização de PPTX)
através de um contrato de capacidades único e público. Quando uma capacidade estiver
ausente, o sistema DEVE escolher um fallback documentado ou declarar a limitação
explicitamente no relatório de entrega. O sistema NUNCA deve simular sucesso ou omitir
silenciosamente uma etapa não suportada.

**Rationale**: sem essa disciplina, "funciona no Claude" se torna uma promessa não
verificável em Codex ou GitHub Copilot, quebrando a proposta multimodelo do produto.

### VIII. Proveniência de Fontes e Assets

Toda alegação factual externa, imagem, logo e asset institucional usado no projeto DEVE
manter URL/origem, data de captura e condição de uso/licença registrados nos artefatos do
projeto, e nas notas do slide quando aplicável.

**Rationale**: permite auditoria, atualização segura quando um link oficial mudar, e
sustenta o caráter acadêmico/institucional do conteúdo gerado.

### IX. Paridade Entre Hosts Sem Identidade Byte a Byte

Dado o mesmo `CONTEXT.md`, os mesmos assets e a mesma configuração, Codex, GitHub Copilot
e Claude Code DEVEM produzir artefatos estruturalmente equivalentes: mesmo conteúdo,
mesmos contratos, mesma marca, mesma ordem de páginas, mesma capacidade nativa de edição e
os mesmos critérios de qualidade satisfeitos. Identidade byte a byte do PPTX NUNCA é
exigida nem é critério de aceitação; variação criativa de composição e narrativa entre
execuções é esperada e aceitável.

**Rationale**: fixa o nível certo de rigor — testar invariantes e critérios de aceitação
compartilhados, não bytes ou pixels exatos, já que a geração criativa varia por modelo.

### X. Entrega Incremental Ancorada na Palestra Real

Cada feature DEVE produzir um incremento utilizável e demonstrável. O primeiro incremento
obrigatório do produto é gerar a apresentação real da palestra do mantenedor a partir de
um `CONTEXT.md` válido, servindo como fixture de aceitação viva. Trabalho que não
contribui diretamente para esse incremento (refatoração ampla para monorepo, paridade
completa de UI entre hosts, matriz extensa de Decks) DEVE ser adiado para iterações
posteriores, a menos que bloqueie o incremento atual.

**Rationale**: mitiga o maior risco identificado do produto — escopo excessivo antes da
entrega da palestra, resultando em não entregar um deck útil no prazo.

## Quality Gates

Toda entrega de um PPTX pelas rotas Generate, Fill ou Enhance DEVE passar, no mínimo,
pelos seguintes gates antes de ser considerada concluída:

1. **Validação de schema** — `CONTEXT.md`, `spec_lock.md` e `animations.json` (quando
   presente) validam contra seus schemas versionados; erros de schema bloqueiam a
   execução.
2. **Checker de SVG** — `svg_quality_checker.py` DEVE passar sem violações da gramática
   restrita (Princípio IV) antes da exportação para OOXML.
3. **Renderização completa** — todas as páginas do PPTX DEVEM ser renderizadas e reunidas
   em um contact sheet para inspeção visual; nenhuma página pode falhar silenciosamente.
4. **Auditoria OOXML** — relações, estrutura de Master/Layout (quando aplicável) e
   abertura do arquivo em PowerPoint ou LibreOffice usado no CI/local DEVEM ser
   verificadas pós-exportação.
5. **Checagem de overflow/clipping/placeholder** — nenhum overflow, clipping ou
   sobreposição não intencional pode existir no PPTX final.
6. **Brand lint** — quando um perfil de marca (ex.: `facom-ufms`) estiver ativo, o lint de
   marca (Princípio VI) DEVE passar antes da entrega.
7. **Documentação** — cada rota/feature entregue DEVE ter um caminho feliz documentado e
   reproduzível a partir dos artefatos do projeto.

Nenhum destes gates pode ser pulado por um perfil de execução rápida. Perfis rápidos
podem reduzir gates interativos humanos; nunca os gates de qualidade acima (Princípio V).

## Fronteiras Não Negociáveis Herdadas do Upstream

O fork FACOM/UFMS multimodelo NÃO PODE:

- se tornar um SaaS, aplicativo desktop ou CLI independente — chat/agent permanece a
  interface principal;
- aceitar SVG arbitrário como se fosse uma linguagem suportada pelo pipeline
  (Princípio IV);
- prometer preenchimento cego (refill) de qualquer placeholder de qualquer PPTX
  arbitrário;
- tornar gráficos nativos do PowerPoint o padrão, pois isso reduz fidelidade entre
  renderizadores;
- trocar qualidade por velocidade de forma indiscriminada (Princípio V);
- se transformar em um framework genérico de conversão OOXML;
- fazer o Executor pesquisar ou reescolher materiais que pertencem à autoridade do
  Strategist;
- criar três cópias divergentes da skill, uma por host (Princípio I).

Qualquer proposta que exija violar uma destas fronteiras DEVE ser registrada como uma
decisão arquitetural explícita (ADR) antes da implementação, não decidida ad hoc dentro
de uma feature.

## Governança

Esta constituição tem precedência sobre qualquer convenção genérica de projeto, prompt de
role ou preferência de host quando houver conflito. Em caso de conflito,
`skills/ppt-master/SKILL.md` continua sendo a autoridade de execução operacional, mas não
pode contradizer os princípios aqui definidos.

**Processo de emenda**: qualquer alteração a esta constituição DEVE (1) ser proposta com a
motivação e o risco associado, citando a seção do `CONTEXT.md` ou ADR relevante;
(2) revisar `.specify/templates/plan-template.md`, `spec-template.md` e `tasks-template.md`
para propagação quando o princípio alterado afetar seus gates; (3) incrementar a versão
conforme a política de versionamento abaixo; (4) registrar um novo Sync Impact Report no
topo deste arquivo.

**Política de versionamento** (SemVer aplicado a esta constituição):

- MAJOR: remoção ou redefinição incompatível de um princípio ou de uma fronteira não
  negociável (ex.: colapsar as quatro rotas, aceitar SVG arbitrário).
- MINOR: adição de um novo princípio, gate de qualidade ou seção, ou expansão material de
  um princípio existente.
- PATCH: esclarecimento de redação, correção de erro de digitação ou refinamento não
  semântico.

**Revisão de conformidade**: todo plano gerado por `/speckit-plan` DEVE preencher a seção
"Constitution Check" citando explicitamente quais dos dez princípios (I–X) acima se
aplicam à feature; qualquer violação DEVE ser justificada na tabela "Complexity Tracking"
do plano, incluindo por que uma alternativa mais simples foi rejeitada. Pull requests que
introduzam uma segunda cópia divergente de workflow, uma referência a primitiva
proprietária de um host dentro do núcleo, ou que pulem um gate de qualidade DEVEM ser
bloqueados até correção ou até que um ADR documente a exceção.

**Version**: 1.0.0 | **Ratified**: 2026-07-27 | **Last Amended**: 2026-07-27
