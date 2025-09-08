## 📖 Workflow de Desenvolvimento — Lineage Project

Este documento descreve o fluxo de trabalho utilizado no projeto para organizar o desenvolvimento, releases e manutenção.

---

### 🚀 Branches Principais

- **`main`**  
  Branch estável, onde ficam as versões prontas para produção.  
  Recebe merges somente em releases.

- **`develop`**  
  Branch de desenvolvimento contínuo.  
  Todo desenvolvimento, novos recursos e correções devem ser feitos aqui.

---

### 🛠️ Como Trabalhar

#### 📌 1. Desenvolvendo
Sempre faça commits e pushes diretamente na `develop`:

```bash
git checkout develop
# editar arquivos
git add .
git commit -m "Descrição do que foi feito"
git push
```

---

#### 📌 2. Criando uma nova release
Quando o projeto estiver pronto para uma nova versão estável:

```bash
git checkout main
git merge develop
git tag -a vX.X.X -m "Descrição da release"
git push origin main --tags
```

- **vX.X.X** → siga o padrão `v1.0.1`, `v1.1.0`, etc.

---

#### 📌 3. Retornando ao desenvolvimento
Depois da release:

```bash
git checkout develop
```

E continue desenvolvendo.

---

### ✅ Dicas Extras

- Antes de começar qualquer coisa:
  ```bash
  git pull
  ```
- Use mensagens de commit claras e objetivas.
- Mantenha o `main` limpo, só com releases estáveis.
