# Contribuindo com Últimos Rastros

Obrigado pelo interesse em contribuir! Este documento descreve o processo para reportar bugs, sugerir melhorias e enviar código.

---

## Sumário

- [Código de Conduta](#código-de-conduta)
- [Como Reportar Bugs](#como-reportar-bugs)
- [Como Sugerir Melhorias](#como-sugerir-melhorias)
- [Enviando Pull Requests](#enviando-pull-requests)
- [Padrões de Código](#padrões-de-código)
- [Estrutura de Commits](#estrutura-de-commits)

---

## Código de Conduta

Ao contribuir, você concorda em seguir nosso [Código de Conduta](CODE_OF_CONDUCT.md).

---

## Como Reportar Bugs

1. Verifique se o bug já foi reportado nas [Issues](https://github.com/lucasrbsouza/ultimos-rastros/issues)
2. Se não existir, abra uma nova issue com:
   - **Título claro** descrevendo o problema
   - **Passos para reproduzir** o bug
   - **Comportamento esperado** vs **comportamento atual**
   - **Sistema operacional** e versão do Python/Pygame
   - **Screenshots ou logs** se disponíveis

---

## Como Sugerir Melhorias

1. Abra uma issue com o label `enhancement`
2. Descreva a melhoria e a motivação por trás dela
3. Se possível, inclua exemplos ou mockups

---

## Enviando Pull Requests

### 1. Fork e clone

```bash
git clone https://github.com/seu-usuario/ultimos-rastros.git
cd ultimos-rastros
```

### 2. Crie uma branch

Use nomes descritivos:

```bash
git checkout -b feat/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

### 3. Faça as alterações

- Mantenha o escopo do PR focado — uma feature ou fix por PR
- Teste o jogo localmente antes de enviar: `python main.py`

### 4. Commit

Siga o padrão de commits abaixo.

### 5. Abra o Pull Request

- Descreva o que foi feito e por quê
- Referencie a issue relacionada com `Closes #número`
- Aguarde revisão

---

## Padrões de Código

- **Python 3.10+** — sem uso de features exclusivas de versões mais novas
- Nomes de variáveis e funções em **snake_case**
- Classes em **PascalCase**
- Constantes em **UPPER_CASE** no `settings.py` ou `levels.py`
- Evite comentários óbvios — comente apenas o **porquê**, não o **o quê**
- Assets novos devem seguir a estrutura existente em `assets/`

---

## Estrutura de Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>: <descrição curta em português ou inglês>
```

| Tipo | Uso |
|---|---|
| `feat` | Nova feature |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `refactor` | Refatoração sem mudança de comportamento |
| `assets` | Adição ou modificação de assets |
| `chore` | Tarefas de manutenção (deps, configs) |

**Exemplos:**

```
feat: adicionar sistema de double jump
fix: corrigir colisão com água na fase 2
assets: adicionar sprites do boss Orc Shaman
docs: atualizar instruções de execução no README
```
