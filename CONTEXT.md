# Contexto de Produto e Desenvolvimento — PPT Master FACOM/UFMS Multimodelo

> Documento de entrada para GitHub Spec Kit  
> Data da descoberta: 27 de julho de 2026  
> Projeto-base analisado: `/Users/mrlopito/Documents/desenv/masterdegree/projects/ppt-master`  
> Fork: `https://github.com/theguitarvity/ppt-master`  
> Commit analisado: `5260a14f8467e52d7fc945c5efead3e2090f0f86`  
> Versão declarada da skill: `4.2.0`

## 1. Visão do produto

Construir uma distribuição do PPT Master que funcione de forma previsível em Codex, GitHub Copilot e Claude Code, mantendo um único núcleo de geração e oferecendo um perfil institucional FACOM/UFMS. A experiência principal deve permitir que uma pessoa forneça um único `CONTEXT.md` com conteúdo, objetivo, público, duração, identidade e preferências; o agente deve produzir uma apresentação PowerPoint completa, coerente, editável, validada e, quando solicitado, animada.

O produto não deve ser três forks de prompts. Deve ser:

1. um núcleo portátil de contratos, workflows, scripts e templates;
2. adapters finos de instalação e capacidades por host;
3. um pacote de marca FACOM/UFMS versionado e verificável;
4. um compilador de `CONTEXT.md` para os artefatos internos do PPT Master;
5. uma suíte de conformidade que prove paridade entre hosts e qualidade do PPTX.

Nome de trabalho: **PPT Master FACOM**. O nome definitivo permanece decisão do mantenedor.

## 2. Resultado esperado

Ao final do MVP:

```text
CONTEXT.md
   ↓ validação e normalização
Presentation Brief normalizado
   ↓ Strategist
design_spec.md + spec_lock.md + assets locais
   ↓ Executor
SVG canônico por slide
   ↓ validação estática e visual
PPTX nativo editável
   ↓ pós-processamento opcional
transições + animações + notas + áudio/vídeo
```

O mesmo `CONTEXT.md`, os mesmos assets e a mesma configuração devem gerar artefatos estruturalmente equivalentes em Codex, GitHub Copilot e Claude Code. Não se exige identidade byte a byte do PPTX, mas se exige paridade de conteúdo, contratos, marca, ordem das páginas, capacidade nativa e critérios de qualidade.

## 3. Descobertas sobre o projeto existente

### 3.1 O projeto já é mais portátil do que sua embalagem sugere

O repositório não é apenas uma skill para Claude. Seu núcleo atual já é uma arquitetura orientada a artefatos e scripts:

- `AGENTS.md` é a fonte geral de instruções para agentes.
- `CLAUDE.md` apenas importa `AGENTS.md`.
- `skills/ppt-master/SKILL.md` define disciplina global e roteamento.
- `.claude-plugin/` e `skills/.claude-plugin/` são a embalagem específica do Claude.
- `.specify/` já está inicializado com Spec Kit `0.8.17`.
- `.agents/skills/speckit-*` e `.specify/integrations/codex.manifest.json` indicam integração Codex em modo skills.
- A documentação declara compatibilidade conceitual com Codex, Cursor, Copilot e outros hosts.

Portanto, a iniciativa deve ser tratada como **produto multimodelo com adapters**, não como “porte do código Claude para Codex”.

### 3.2 Rotas de produto existentes

`skills/ppt-master/workflows/routing.md` define quatro ciclos de vida mutuamente exclusivos:

| Rota | Entrada | Estratégia | Saída |
|---|---|---|---|
| Generate PPTX | tema, documentos, URLs, Markdown ou PPTX como fonte | planejamento → SVG → DrawingML | novo projeto e PPTX |
| Create Template | referências visuais, marca, PPTX/SVG ou briefing | cria workspace portátil Brand/Layout/Deck | template reutilizável |
| Fill Native PPTX | PPTX nativo e novo conteúdo | clone e patch OOXML | novo PPTX preenchido |
| Enhance Native PPTX | PPTX finalizado | patch OOXML preservando visual | PPTX com notas/áudio/transições |

Essa separação deve permanecer. Em especial:

- um PPTX bruto não é automaticamente template do pipeline SVG;
- rotas nativas não devem passar pela regeneração SVG;
- templates reutilizáveis devem ser workspaces explícitos;
- alterações de Master/Layout não devem ser inferidas e enxertadas em arquivos existentes.

### 3.3 Pipeline Generate PPTX

O fluxo principal é serial e possui gates humanos:

1. converter/importar fontes;
2. inicializar o projeto;
3. aplicar workspace de template somente quando houver caminho explícito;
4. executar o papel Strategist;
5. adquirir ou gerar imagens quando necessário;
6. executar o papel Executor;
7. dividir notas, materializar preview, validar e exportar.

Artefatos centrais:

| Artefato | Responsabilidade |
|---|---|
| `sources/` | conteúdo canônico e fontes arquivadas |
| `analysis/` | fatos extraídos de máquina, não decisões de design |
| `design_spec.md` | explicação completa da estratégia de comunicação e design |
| `spec_lock.md` | contrato compacto e executável entre páginas |
| `images/` e `icons/` | pool local de materiais aprovados |
| `svg_output/` | única fonte SVG editada manualmente |
| `svg_final/` | derivado para preview; não é fonte da exportação nativa |
| `validation/` | relatórios de qualidade e pós-flight |
| `exports/` | entregáveis PPTX |
| `animations.json` | configuração opcional de animação por objeto |

### 3.4 Modelo técnico

O projeto usa SVG como linguagem intermediária restrita de design de página. O SVG canônico é compilado para DrawingML/OOXML, preservando texto, formas, imagens, gráficos suportados, notas, relacionamentos e, quando aplicável, estrutura de Master/Layout.

Essa escolha oferece:

- geração razoavelmente confiável por LLM;
- inspeção em navegador;
- coordenadas absolutas fáceis de depurar;
- transformação determinística para PowerPoint;
- objetos editáveis em vez de screenshots;
- validação antes da escrita de OOXML.

O SVG aceito não é SVG arbitrário. O projeto possui uma gramática prática e contratos de compatibilidade em:

- `references/shared-standards-core.md`;
- `references/semantic-svg.md`;
- `references/native-data-interface.md`;
- `references/pptx-structure-interface.md`;
- `docs/powerpoint-svg-mapping.md`;
- `scripts/svg_quality_checker.py`;
- `scripts/svg_to_pptx.py`.

### 3.5 Papéis e prompts

Os papéis principais são modos especializados de um agente, não agentes independentes:

- **Strategist**: interpreta conteúdo, define comunicação, narrativa, modo, estilo visual, cores, tipografia, páginas, layouts, imagens, gráficos e notas.
- **Image Generator/Searcher**: materializa o plano de assets definido pelo Strategist.
- **Executor**: realiza cada página sob o contrato do `design_spec.md` e `spec_lock.md`.
- **Template Designer** e papéis de rotas nativas: atuam apenas em seus ciclos específicos.

O projeto favorece execução serial porque o design de cada slide depende do contexto acumulado, do ritmo visual anterior e dos assets realmente disponíveis. A revisão visual paralela existe como estágio opcional e é o ponto com maior acoplamento ao sistema de equipes do Claude.

### 3.6 Templates

Há três tipos:

| Tipo | O que governa |
|---|---|
| Brand | identidade: cores, tipografia, logos, voz, estilo de ícones |
| Layout | estrutura neutra: canvas, papéis de página, slots e topologia |
| Deck | aplicação recorrente: identidade + estrutura + contexto comunicacional |

Master, Layout e Placeholder do PowerPoint são alvos de compilação, não novos tipos de template.

O pacote FACOM/UFMS deve começar como **Deck** quando trouxer identidade institucional e padrões de palestra/aula/defesa. Pode também expor um **Brand** FACOM/UFMS separado para composição com outros Layouts. O MVP deve evitar duplicar regras entre os dois: Brand é a autoridade da identidade; Deck referencia ou incorpora essa autoridade por meio do mecanismo já existente de fusão/proveniência.

### 3.7 Animações

O projeto já suporta:

- transições de página;
- autoavanço;
- Morph como diferença entre páginas;
- animações de entrada, ênfase, saída e caminhos de movimento;
- configuração por âncoras semânticas em grupos `<g id="...">`;
- validação de `animations.json`;
- narração, sincronização e exportação de vídeo.

Limite importante: animações por objeto são aplicadas no pipeline gerado. As rotas nativas preservam animações existentes, mas não devem prometer edição genérica de qualquer animação PowerPoint.

### 3.8 Scripts e dependências

O runtime é majoritariamente Python e OOXML direto. Os grupos relevantes incluem:

- conversão: `source_to_md.py` e conversores por formato;
- projeto: `project_manager.py`, `project_specs.py`;
- intake PPTX: `pptx_intake.py`, `pptx_to_svg/`;
- SVG: authoring view, compactação, finalização, checker e exportador;
- template: importação, materialização mirror, preview e fill nativo;
- imagens: busca, análise, geração e múltiplos providers;
- animação/transição: `animation_config.py`, `pptx_animations.py`, `pptx_transitions.py`;
- notas/áudio/vídeo: TTS, narração, legendas e motion plan;
- revisão: preview ao vivo, edição e revisão visual.

O `requirements.txt` raiz delega para `skills/ppt-master/requirements.txt`. O projeto deliberadamente mantém `pip` como caminho oficial e não exige `uv` para o runtime do PPT Master. `uv` pode ser usado para instalar o Spec Kit, mas essas duas decisões não devem ser confundidas.

### 3.9 Fronteiras e não objetivos herdados

Devem ser preservados no fork:

- não virar SaaS, aplicativo desktop ou CLI independente; chat/agent é a interface principal;
- não aceitar SVG arbitrário como se fosse linguagem suportada;
- não prometer refill cego de qualquer placeholder de qualquer PPTX;
- não tornar charts nativos o padrão, pois isso reduz fidelidade entre renderizadores;
- não trocar qualidade por velocidade de forma indiscriminada;
- não transformar o projeto em framework genérico de conversão OOXML;
- não fazer o Executor pesquisar ou escolher novamente materiais que pertencem ao Strategist;
- não criar três cópias divergentes da skill por host.

## 4. Identidade FACOM/UFMS

### 4.1 Fontes oficiais encontradas

- Identidade visual FACOM: `https://www.facom.ufms.br/institucional/identidade-visual/`
- Logo FACOM: `https://www.facom.ufms.br/wp-content/uploads/2015/12/grafo_facom.png`
- Manual de Identidade Visual UFMS, aprovado pela Resolução nº 493-Coun/UFMS de 1º de abril de 2026: `https://agecom.ufms.br/files/2026/06/Manual-de-Identidade-Visual-UFMS_abr2026.pdf`
- Apresentação institucional e PPT oficial: `https://agecom.ufms.br/apresentacao-institucional/`
- Downloads de logos: `https://www.ufms.br/logos-ufms/`

### 4.2 Fatos institucionais que se tornam contratos

- O símbolo da FACOM é o **Grafo de Petersen**.
- O logo oficial UFMS é composição indivisível de símbolo e logotipo, salvo aprovação especial.
- Cor institucional UFMS: `#0088B7`.
- Tipografia da assinatura UFMS: personalização de Futura XBlkCn BT.
- Tipografia de apoio para assinaturas de unidades: Swis721 Cn BT.
- Tipografia do slogan: Poppins Bold, somente nas proporções oficiais.
- Para fundos claros, usar marca institucional colorida ou preta.
- Para fundos com mais de 40% de preenchimento/escuros, usar marca branca/negativa.
- Sobre imagem complexa, posicionar em área neutra ou usar box branco.
- Preservar proporção e área de proteção da marca.
- A unidade pode ter logo própria, mas a marca adicional deve ser usada com a marca UFMS e não pode reutilizar elementos da marca UFMS.
- Em convivência com marcas internas/externas comuns, a UFMS fica à direita ou abaixo, conforme orientação.
- Com Governo Federal/ministérios, a UFMS fica à esquerda ou acima.
- O manual contém padrões específicos para slides de abertura, conteúdo e encerramento.
- Uso interno acadêmico é permitido quando o manual é respeitado; uso externo deve considerar autorização da Agecom.

### 4.3 Direção visual proposta

O perfil FACOM/UFMS não deve ser apenas “azul institucional”. Deve usar:

- a geometria do Grafo de Petersen como motivo estrutural discreto;
- azul UFMS `#0088B7` como token institucional;
- superfícies brancas e azul profundo para garantir contraste;
- cor de destaque derivada do conteúdo, nunca aplicada à marca oficial;
- hierarquia tipográfica acadêmica e técnica;
- layouts adequados a palestras, aulas, defesas, seminários, projetos de pesquisa e extensão;
- rodapé institucional configurável, sem transformar todos os slides em papel timbrado;
- fontes livres/instaláveis de fallback para conteúdo, mantendo os logos oficiais como assets não reconstruídos.

O símbolo FACOM não deve ser redesenhado por IA. Os arquivos oficiais devem ser baixados, versionados com metadados de origem e usados sem distorção.

## 5. Problema a resolver

Hoje o núcleo é portável, mas a experiência ainda depende de convenções implícitas do host:

- instalação e descoberta diferem entre Claude, Codex e Copilot;
- capacidades como geração de imagem, browser, visualização, subagentes e confirmação interativa não têm um contrato formal único;
- a revisão visual opcional menciona primitivas de equipes específicas do Claude;
- não existe um schema público para um único `CONTEXT.md` de entrada;
- não existe pacote oficial FACOM/UFMS;
- não existe matriz automatizada de conformidade por host;
- não existe um caminho “palestra amanhã” com defaults institucionais e mínimo de gates;
- o repositório oferece muitas opções, mas falta um caminho feliz documentado para um usuário FACOM.

## 6. Princípios propostos para a Constituição do Spec Kit

1. **Núcleo único, adapters finos**  
   Workflows, referências, schemas, scripts e templates devem ser compartilhados. Arquivos por host apenas traduzem descoberta, comando e capacidade.

2. **Artefatos acima do modelo**  
   `CONTEXT.md`, brief normalizado, `design_spec.md`, `spec_lock.md`, SVG, relatórios e PPTX são os contratos. Nenhum comportamento essencial pode depender de memória implícita de um modelo específico.

3. **Determinismo onde importa**  
   Roteamento, schemas, assets, exportação, validação e regras de marca são determinísticos. Criatividade é permitida em narrativa e composição dentro dos contratos.

4. **Fidelidade e editabilidade antes de velocidade**  
   O PPTX final deve ser apresentável e editável. Quick mode pode reduzir iterações, não eliminar os gates críticos de qualidade.

5. **Marca como política verificável**  
   Regras FACOM/UFMS devem existir como tokens, assets, constraints e testes. Não podem depender apenas de texto em prompt.

6. **Degradação explícita por capacidade**  
   Quando um host não oferecer imagens nativas, browser, subagentes ou UI, o adapter deve escolher fallback documentado ou declarar a limitação. Nunca deve simular sucesso.

7. **Paridade sem identidade byte a byte**  
   Todos os hosts devem satisfazer os mesmos cenários e critérios de aceitação. Variação criativa é permitida.

8. **Fontes e proveniência**  
   Alegações externas, imagens e assets institucionais devem manter URL/origem e licença/condição de uso nos artefatos do projeto e nas notas quando aplicável.

9. **Entrega incremental**  
   Cada feature deve produzir um incremento utilizável. O primeiro incremento obrigatório é gerar a apresentação da palestra a partir de `CONTEXT.md`.

10. **Preservar as fronteiras do upstream**  
    As quatro rotas, a autoridade do Strategist, a gramática SVG restrita e a separação entre geração e patch nativo não podem ser colapsadas sem uma decisão arquitetural explícita.

## 7. Arquitetura alvo

```text
packages/
├── core/
│   ├── skill/                 # SKILL, workflows e referências comuns
│   ├── schemas/               # context, capabilities, brief, reports
│   ├── scripts/               # motor Python/OOXML/SVG
│   └── templates/             # charts, icons, layouts e decks comuns
├── brands/
│   └── facom-ufms/
│       ├── brand/
│       ├── deck/
│       ├── assets/
│       ├── provenance.json
│       └── brand-policy.yaml
└── adapters/
    ├── claude/
    ├── codex/
    └── github-copilot/

conformance/
├── fixtures/
│   ├── minimal-context/
│   ├── facom-talk/
│   ├── animated-talk/
│   └── source-backed-talk/
├── expected/
└── host-matrix.yaml
```

Essa árvore é uma direção para o plano técnico, não uma obrigação de reestruturação imediata. O MVP pode manter a árvore existente e introduzir interfaces compatíveis de forma incremental.

### 7.1 Contrato de capacidade do host

Criar `host-capabilities.schema.json` com, no mínimo:

```yaml
host_id: codex | github-copilot | claude-code
skill_discovery: true
shell: true
filesystem_read: true
filesystem_write: true
browser: optional
image_generation: native | api | unavailable
parallel_agents: native | sequential-fallback | unavailable
interactive_confirmation: web-ui | chat | unavailable
image_inspection: true | false
pptx_rendering: local | external | unavailable
```

Workflows consultam capacidades sem mencionar marcas de agente. O adapter declara a capacidade real.

### 7.2 Contrato de `CONTEXT.md`

O parser deve aceitar frontmatter YAML e corpo Markdown. O corpo contém o material narrativo; o frontmatter contém parâmetros operacionais.

Exemplo mínimo:

```yaml
---
presentation:
  title: "Título da palestra"
  language: pt-BR
  audience: "Estudantes e docentes da FACOM"
  objective: "Ensinar e provocar discussão"
  duration_minutes: 30
  slide_count: auto
  format: ppt169
brand:
  profile: facom-ufms
delivery:
  animations: purposeful
  speaker_notes: true
  citations: true
  output_name: palestra-facom.pptx
quality:
  mode: standard
---

# Tese central

...

# Conteúdo e evidências

...
```

Campos necessários para o schema completo:

- identidade da apresentação;
- público, objetivo e resultado esperado;
- duração, quantidade de slides e idioma;
- mensagem central e tópicos obrigatórios;
- fontes e restrições factuais;
- tipo de narrativa/modo;
- estilo visual e perfil de marca;
- assets fornecidos;
- requisitos de gráficos, tabelas, código, equações e imagens;
- notas, citações, acessibilidade;
- transições/animações/autoavanço;
- formato de tela e destino;
- gates interativos permitidos;
- modo de qualidade;
- restrições e não objetivos.

O compilador deve:

1. validar o frontmatter;
2. preservar o corpo Markdown como fonte;
3. produzir um brief normalizado, versionado e legível;
4. mapear campos para o Strategist sem duplicar `design_spec.md`;
5. registrar defaults aplicados e avisos;
6. interromper somente em ambiguidades que alterem materialmente o resultado.

## 8. Escopo do MVP “palestra amanhã”

### 8.1 Obrigatório

- usar o fork atual sem reescrita estrutural ampla;
- adicionar schema e parser de `CONTEXT.md`;
- adicionar adapter Codex funcional;
- manter Claude funcional;
- adicionar instruções/adapter GitHub Copilot;
- criar pacote Brand FACOM/UFMS com assets oficiais;
- criar ao menos um Deck FACOM para palestra técnica em 16:9;
- gerar deck completo com abertura, conteúdo e encerramento;
- permitir notas do apresentador;
- permitir transições e animações intencionais;
- validar SVG, overflow, relações OOXML e abertura do PPTX;
- renderizar todas as páginas e produzir contact sheet;
- adicionar smoke fixture baseada em uma palestra FACOM;
- documentar um único comando/caminho feliz por host.

### 8.2 Pode ficar para a segunda iteração

- paridade completa da UI de confirmação em todos os hosts;
- matriz extensa de templates FACOM para aula, defesa e relatório;
- execução paralela da revisão visual em todos os hosts;
- geração de áudio e vídeo como caminho padrão;
- publicação em marketplaces;
- refatoração completa para monorepo/packages;
- golden tests visuais em múltiplos renderizadores;
- localização completa de toda a documentação.

### 8.3 Fora do MVP

- SaaS;
- editor visual novo;
- preencher qualquer PPTX arbitrário;
- substituir PowerPoint;
- identidade byte a byte entre modelos;
- animação avançada editável em PPTX arbitrário;
- aprovação automática de uso externo da marca UFMS.

## 9. Épicos e features para o Spec Kit

### Épico 0 — Baseline e caracterização

Objetivo: congelar o comportamento atual antes de alterar a embalagem.

- inventariar rotas, scripts, schemas, prompts, templates e dependências;
- criar fixtures mínimas para Generate, Template, Fill e Enhance;
- executar smoke tests do fork;
- registrar tempos, artefatos e falhas;
- criar decisão arquitetural sobre “core + adapters”.

Aceite:

- pelo menos uma fixture do Generate exporta um PPTX válido;
- artefatos esperados estão documentados;
- alterações futuras conseguem distinguir regressão de comportamento pré-existente.

### Épico 1 — `CONTEXT.md` como entrada

- criar JSON Schema/YAML schema versionado;
- implementar parser e normalizador;
- produzir mensagens de erro acionáveis;
- adicionar defaults para FACOM/palestra;
- integrar com Step 1 e Step 4 sem eliminar gates obrigatórios;
- documentar exemplos mínimo, completo e animado.

Aceite:

- um contexto mínimo válido inicia um projeto sem intervenção;
- campos desconhecidos geram aviso ou erro conforme política;
- saída normalizada registra todos os defaults;
- conteúdo do corpo não é perdido.

### Épico 2 — Adapter de host e matriz de capacidades

- definir interface de capacidades;
- mover referências explícitas a primitivas Claude para adapter;
- implementar fallback sequencial de revisão;
- mapear ferramentas nativas de imagem;
- mapear confirmação por UI ou chat;
- criar diagnósticos de host.

Aceite:

- core não exige `TeamCreate`, `SendMessage` ou nomes de ferramentas proprietárias;
- cada host informa capacidades e fallbacks antes da execução;
- ausência de uma capacidade não produz falso positivo.

### Épico 3 — Empacotamento Codex

- validar `SKILL.md` sob regras Codex;
- manter referências com carregamento progressivo;
- fornecer instalador/documentação;
- garantir paths e scripts portáveis;
- integrar o fluxo do Spec Kit em modo skills;
- testar geração, imagem e revisão.

Aceite:

- a skill é descoberta e acionada por pedido natural;
- o `CONTEXT.md` gera PPTX usando o adapter Codex;
- toda limitação do host aparece no relatório.

### Épico 4 — Empacotamento GitHub Copilot

- gerar `.github/prompts/` e/ou configuração de custom agent adequada;
- adaptar comandos e instruções sem duplicar o core;
- documentar requisitos de terminal e extensões;
- testar em VS Code;
- validar os mesmos fixtures.

Aceite:

- Copilot consegue executar o caminho feliz a partir do repositório aberto;
- os mesmos schemas e scripts do core são usados;
- não existe segunda cópia divergente dos workflows.

### Épico 5 — Marca FACOM/UFMS

- baixar e versionar assets oficiais;
- registrar URLs, data, hash e condição de uso;
- codificar tokens e regras de contraste;
- construir Brand workspace;
- construir Deck “palestra técnica FACOM 16:9”;
- adicionar regras de co-branding;
- criar lint de marca.

Aceite:

- `#0088B7` e versões corretas do logo são usadas;
- o logo não é reconstruído nem distorcido;
- contraste/fundo determina versão positiva ou negativa;
- FACOM e UFMS respeitam hierarquia e área de proteção;
- slides de abertura, conteúdo e final seguem o manual;
- o lint falha em violações conhecidas.

### Épico 6 — Deck completo e animado

- adicionar presets `none`, `subtle`, `purposeful`, `narrative`;
- mapear presets para transições e animações existentes;
- usar âncoras semânticas estáveis;
- validar `animations.json`;
- documentar Morph por duplicação/diferença de páginas;
- limitar animações por critérios de comunicação e acessibilidade.

Aceite:

- `purposeful` gera animações que reforçam a narrativa;
- IDs inexistentes ou animações conflitantes falham na validação;
- modo `none` remove animações adicionadas pelo motor;
- o deck continua utilizável sem animações em renderizadores limitados;
- `prefers_reduced_motion` ou opção equivalente é suportada no contexto.

### Épico 7 — QA e conformidade

- checker de schema;
- checker SVG;
- auditoria OOXML;
- render de todas as páginas;
- overflow/clipping/placeholder checks;
- verificação de marca;
- notas e fontes;
- matriz de host;
- relatório único de entrega.

Aceite:

- nenhum overflow ou overlap não intencional;
- todas as páginas renderizam;
- arquivo abre em PowerPoint ou LibreOffice usado no CI/local;
- notas e fontes são rastreáveis;
- relatório identifica host, versão, capabilities, warnings e checks.

### Épico 8 — Documentação e distribuição

- quickstart por host;
- guia “palestra amanhã”;
- exemplos de `CONTEXT.md`;
- troubleshooting;
- política de atualização do upstream;
- changelog e versionamento;
- estratégia de marketplace posterior.

## 10. Ordem recomendada de implementação

### Faixa A — hoje, orientada à palestra

1. baseline do Generate;
2. assets oficiais FACOM/UFMS;
3. Brand + Deck mínimo;
4. parser simples de `CONTEXT.md`;
5. geração pelo Codex;
6. animações `purposeful`;
7. render e QA manual/automático;
8. usar o deck real da palestra como fixture de aceitação.

### Faixa B — produto multimodelo

1. capability contract;
2. adapters Codex/Claude/Copilot;
3. suíte de paridade;
4. revisão visual com fallback;
5. documentação de instalação;
6. sincronização com upstream.

### Faixa C — endurecimento

1. mais Decks FACOM;
2. testes de marca;
3. golden renders;
4. acessibilidade;
5. áudio/vídeo;
6. distribuição.

## 11. Critérios globais de aceitação

### Funcionais

- dado um `CONTEXT.md` válido, gerar um projeto completo e um PPTX;
- aceitar fontes locais e URLs de forma rastreável;
- gerar notas por slide quando solicitado;
- aplicar Brand/Deck FACOM/UFMS;
- ativar ou desativar animações por contexto;
- retomar projeto interrompido a partir de artefatos;
- executar em Codex, Copilot e Claude com adapters próprios.

### Qualidade visual

- título de capa legível e sem excesso;
- uma função narrativa principal por slide;
- sem textos cortados, sobreposições acidentais ou placeholders;
- hierarquia tipográfica consistente;
- contraste WCAG razoável para conteúdo;
- logo legível, proporcional e em área neutra;
- uso não repetitivo e relevante de imagens;
- transições/animações sem distração.

### Técnicos

- schema versionado;
- scripts com exit codes confiáveis;
- nenhum segredo versionado;
- paths absolutos ou resolvidos de forma portátil;
- outputs reproduzíveis a partir dos artefatos do projeto;
- validação estática antes da exportação;
- auditoria pós-exportação;
- logs sem dados sensíveis;
- compatibilidade macOS, Linux e Windows conforme scripts suportados.

### Multimodelo

- nenhuma lógica de domínio exclusiva em adapter;
- toda capacidade específica declarada;
- fixtures comuns;
- relatório de diferenças;
- mesma rota e mesmos contratos para a mesma entrada.

## 12. Riscos e mitigação

| Risco | Impacto | Mitigação |
|---|---|---|
| escopo excessivo antes da palestra | não entregar deck útil | usar Faixa A e o deck real como vertical slice |
| prompts divergirem por host | manutenção triplicada | core único, adapters finos e testes de hash/manifest |
| fonte institucional não instalada | layout inconsistente | logos como assets oficiais; conteúdo com fallback livre testado |
| uso incorreto da marca | risco institucional | brand lint, provenance e revisão manual do primeiro pacote |
| animações incompatíveis | deck quebrado | presets conservadores, validação e fallback sem motion |
| revisão visual cara | lentidão/token | batches opcionais, fallback sequencial e QA determinístico primeiro |
| upstream evoluir rapidamente | fork divergir | política de rebase/cherry-pick, ADRs e patches pequenos |
| geração criativa variar por modelo | paridade difícil | testar invariantes e resultados, não bytes/pixels exatos |
| links oficiais mudarem | assets sem origem | hashes locais, metadados, data de captura e rotina de atualização |

## 13. Questões que o Spec Kit deve resolver durante `/speckit.clarify`

Estas questões não bloqueiam a especificação inicial, mas devem ser fechadas antes do plano final:

1. O produto será mantido dentro do fork atual ou em um novo repositório?
2. O nome público será PPT Master FACOM, PPT Master Codex ou outro?
3. A distribuição FACOM é interna, pública ou upstreamável?
4. Qual é o ambiente primário do GitHub Copilot: VS Code custom agents, prompt files ou ambos?
5. Quais ferramentas de renderização estarão disponíveis no CI?
6. A primeira palestra exige áudio/vídeo ou apenas PPTX animado?
7. Quais fontes podem ser legalmente distribuídas no pacote?
8. O pacote FACOM precisa de aprovação formal da direção/Agecom antes de uso público?
9. O MVP deve suportar somente `ppt169`?
10. Qual nível de acesso à internet deve ser permitido em execução normal?

## 14. Prompt sugerido para `/speckit.constitution`

```text
Crie a constituição do PPT Master FACOM multimodelo. Adote como princípios
obrigatórios: núcleo único com adapters finos por host; artefatos e schemas como
contratos acima do modelo; preservação das quatro rotas do PPT Master; SVG
canônico restrito como IR de geração; fidelidade, editabilidade e validação antes
de velocidade; marca FACOM/UFMS codificada como política verificável; degradação
explícita por capacidades do host; proveniência de fontes e assets; paridade de
resultados entre Codex, GitHub Copilot e Claude sem exigir identidade byte a
byte; entrega incremental começando pelo deck real da palestra. Inclua gates
obrigatórios de testes, renderização, auditoria OOXML, brand lint e documentação.
Detalhes de schemas e interfaces devem ficar nas specs e contracts das features,
não na constituição.
```

## 15. Prompt sugerido para `/speckit.specify`

```text
Implemente a primeira vertical slice do PPT Master FACOM multimodelo.

Uma pessoa fornece um CONTEXT.md com frontmatter e conteúdo Markdown. O sistema
valida e normaliza o contexto, inicializa um projeto PPT Master, aplica o perfil
FACOM/UFMS, executa o pipeline Generate PPTX, produz design_spec.md, spec_lock.md,
SVGs canônicos, notas, validações e um PPTX 16:9 completo. Quando
delivery.animations for purposeful, o deck recebe transições e animações
semânticas validadas. O primeiro host é Codex, preservando compatibilidade com
Claude e definindo a interface necessária para GitHub Copilot. O primeiro caso
de aceitação é a palestra real do mantenedor. O pacote de marca usa somente
assets oficiais, cor UFMS #0088B7 e regras do Manual de Identidade Visual UFMS
de abril de 2026, incluindo contraste, área de proteção e convivência de marcas.

Não construir SaaS, desktop app, editor visual novo, refill genérico de PPTX ou
três cópias da skill. Não reescrever o motor atual. Entregar um caminho feliz
documentado, fixtures, validação e relatório de conformidade.
```

## 16. Prompt sugerido para `/speckit.plan`

```text
Planeje a vertical slice sobre o fork existente, usando Python 3 e os scripts
OOXML/SVG atuais. Preserve a árvore atual sempre que possível. Introduza:
(1) schema versionado e parser de CONTEXT.md;
(2) brief normalizado;
(3) host-capabilities schema e adapter Codex mínimo;
(4) Brand e Deck FACOM/UFMS com assets oficiais e provenance;
(5) presets de animação sobre animations.json;
(6) conformance fixture da palestra;
(7) pipeline de QA com schema, SVG checker, render de todas as páginas, overflow,
brand lint e auditoria PPTX.

Inclua research.md com decisões sobre empacotamento Codex/Copilot/Claude,
data-model.md para Context/Brief/Capabilities/BrandPolicy/DeliveryReport,
contracts/ com JSON Schemas e CLI boundaries, quickstart.md e ADRs quando uma
decisão alterar fronteiras do upstream. Priorize uma entrega executável em um
dia antes da refatoração ampla.
```

## 17. Comandos e próximos passos

### 17.1 Proteger o estado atual

```bash
cd /Users/mrlopito/Documents/desenv/masterdegree/projects/ppt-master
git status
git switch -c codex/facom-multimodel
git add CONTEXT.md
git commit -m "docs: define FACOM multimodel PPT Master context"
```

Se o `CONTEXT.md` estiver inicialmente fora do fork, copie-o para a raiz do fork antes do `git add`.

### 17.2 Verificar o Spec Kit já instalado

O fork analisado já contém Spec Kit `0.8.17` com integração Codex. Primeiro:

```bash
cd /Users/mrlopito/Documents/desenv/masterdegree/projects/ppt-master
specify version
specify check
specify self check
```

Não execute `specify init --force` sem revisar o diff, pois o projeto já possui `.specify/`, manifests e skills Codex.

### 17.3 Adicionar Copilot sem remover Codex

Versões atuais do Spec Kit permitem múltiplas integrações controladas. Verifique a versão antes:

```bash
specify integration list
specify integration install copilot
specify integration list
```

Mantenha Codex como default durante o MVP:

```bash
specify integration use codex
```

### 17.4 Executar o ciclo Spec Kit no Codex

No Codex em modo skills, os comandos são:

```text
$speckit-constitution <usar o prompt da seção 14>
$speckit-specify <usar o prompt da seção 15>
$speckit-clarify
$speckit-plan <usar o prompt da seção 16>
$speckit-checklist
$speckit-tasks
$speckit-analyze
$speckit-implement
```

Em hosts com slash commands:

```text
/speckit.constitution
/speckit.specify
/speckit.clarify
/speckit.plan
/speckit.checklist
/speckit.tasks
/speckit.analyze
/speckit.implement
```

### 17.5 Ordem prática para hoje

```text
1. Colocar este CONTEXT.md na raiz do fork.
2. Criar a branch codex/facom-multimodel.
3. Rodar constitution e specify.
4. Rodar clarify apenas para decisões que afetam a vertical slice.
5. Rodar plan exigindo entrega em um dia.
6. Gerar tasks e marcar como P0:
   - parser CONTEXT.md;
   - assets/Brand/Deck FACOM;
   - geração Codex;
   - animações purposeful;
   - QA;
   - deck real.
7. Implementar P0.
8. Usar o conteúdo real da palestra como fixture.
9. Renderizar e revisar cada slide.
10. Só depois iniciar adapter Copilot e refatoração ampla.
```

## 18. Definição de pronto do primeiro marco

O primeiro marco está pronto somente quando:

- um `CONTEXT.md` real da palestra foi aceito;
- o perfil FACOM/UFMS foi aplicado com assets oficiais;
- todos os slides foram gerados;
- notas foram geradas quando solicitadas;
- animações/transições foram aplicadas e validadas;
- o PPTX abriu corretamente;
- todas as páginas foram renderizadas;
- não há overflow, clipping ou overlap não intencional;
- a marca respeita contraste, proporção e hierarquia;
- fontes e assets possuem proveniência;
- há instrução reproduzível para gerar novamente;
- o resultado foi revisado como apresentação, não apenas como arquivo tecnicamente válido.

