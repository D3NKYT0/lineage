# Guia de Desenvolvimento

## Organização do Projeto
- **Apps Django** em `apps/` (main, lineage, api, media_storage)
- **Frontend** em `frontend/`
- **Utilitários** em `utils/`, `middlewares/`
- **Templates** em `templates/` e `themes/`

## Convenções de Código
- Seguir **PEP 8** para Python
- Usar nomes descritivos para funções, variáveis e arquivos
- Separar responsabilidades em apps e módulos distintos

## Fluxo de Trabalho (Git)
Consulte o arquivo `workflow.md` na raiz do projeto. Resumo:
- **main** — Branch estável para produção
- **develop** — Branch de desenvolvimento contínuo
- Commits e pushes em `develop`
- Releases via merge de `develop` em `main` com tag `vX.X.X`

### Desenvolvendo
```bash
git checkout develop
git pull
# editar arquivos
git add .
git commit -m "Descrição clara do que foi feito"
git push
```

### Nova release
```bash
git checkout main
git merge develop
git tag -a vX.X.X -m "Descrição da release"
git push origin main --tags
git checkout develop
```

## Testes
- Testes em `test/`
- Executar:
  ```bash
  python manage.py test
  ```
- Escreva testes para novas funcionalidades

## Linters e Qualidade
- Use `flake8`, `black` ou ferramentas similares para manter padrões

## Variáveis de Ambiente
- Use variáveis de ambiente para configurações sensíveis
- Consulte `docs/VARIABLES_ENVIRONMENT.md` para lista completa
- Copie `env.sample` para `.env` e configure

## Dicas
- Consulte a documentação de cada app em `docs/`
- Use `./install.sh menu` para comandos úteis em ambiente Docker
- Documentação da API em `docs/API_DOCUMENTATION.md` e `docs/API_ENDPOINTS.md`
