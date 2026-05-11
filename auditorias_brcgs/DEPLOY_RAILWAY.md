# Deploy em Railway — Guia Passo a Passo

## 1. Preparar o Código (Já Feito! ✓)

A pasta `auditorias_brcgs/` contém tudo pronto para Railway:
- app.py
- requirements.txt
- Procfile
- runtime.txt

## 2. Upload para Railway

### Opção A: Via GitHub (Recomendado — Deploy Automático)

```bash
# 1. Criar repositório GitHub
# Ir a github.com → New Repository
# Nome: auditorias-brcgs
# Privado ou Público (tua escolha)

# 2. Clonar e fazer push
cd auditorias_brcgs
git init
git add .
git commit -m "Initial commit: auditorias BRCGS app"
git branch -M main
git remote add origin https://github.com/SEU_USERNAME/auditorias-brcgs.git
git push -u origin main

# 3. Em Railway
# - Ir a railway.app dashboard
# - "New Project" → "Deploy from GitHub"
# - Seleccionar repositório auditorias-brcgs
# - Railway faz deploy automático!
```

### Opção B: Via Railway CLI (Mais Rápido)

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy
cd auditorias_brcgs
railway init
railway up
```

## 3. Configurar Variáveis de Ambiente em Railway

No dashboard do Railway:
1. Ir ao projeto
2. "Variables" → "Add Variable"
3. Adicionar:
   ```
   FLASK_ENV=production
   SECRET_KEY=simple2work_auditorias_2026
   DATABASE_URL=postgresql://... (Railway fornece automaticamente se usares DB)
   ```

**Nota:** Para usar PostgreSQL em produção (melhor que SQLite):
- Em Railway, "Add Service" → PostgreSQL
- Railway fornece DATABASE_URL automaticamente

## 4. Configurar Domínio (auditorias.simple2work.pt)

### Em Railway:
1. Dashboard → Settings → Custom Domain
2. Copiar: `auditorias-xxx.railway.app` (CNAME fornecido)

### Em Dominios.pt:
1. Ir a dominios.pt → Gerir simple2work.pt
2. DNS → Adicionar CNAME:
   - Host: `auditorias`
   - Valor: `auditorias-xxx.railway.app`
   - TTL: 3600

3. Aguardar 5-10 minutos pela propagação

## 5. Verificar Deploy

```bash
# URL da app
https://auditorias.simple2work.pt

# Login
Email: filipa.ramos@simple2work.pt
Password: Iamtheboss_2026
```

## Troubleshooting

### "502 Bad Gateway"
- Verificar logs em Railway: "View Logs"
- Certificar que Procfile está correto
- Certificar que requirements.txt tem todas as dependências

### Base de dados não funciona
- Se usar SQLite: ficheiro `auditorias.db` é criado automaticamente
- Se usar PostgreSQL: Railway fornece DATABASE_URL automaticamente

### Domínio não funciona
- Aguardar propagação DNS (até 24h, mas normalmente 5-10 min)
- Ir a dnschecker.org para verificar propagação

## Deploy de Atualizações

Se fizeres mudanças ao código:

**Com GitHub:**
```bash
git add .
git commit -m "Descrição da mudança"
git push origin main
# Railway faz deploy automático em segundos!
```

**Com Railway CLI:**
```bash
railway up
```

## Suporte

- Railway Docs: railway.app/docs
- Para dúvidas: filipa.ramos@simple2work.pt
