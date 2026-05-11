# Sistema de Auditorias BRCGS — Simple2Work

Aplicação web profissional para gestão de auditorias BRCGS com:
- Dashboard admin para Filipa
- Links compartilhados para clientes (read-only)
- Checklist com split view
- Geração automática de PDFs
- Histórico de auditorias

## Estrutura

```
auditorias_brcgs/
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências Python
├── Procfile           # Configuração de hospedagem
├── templates/         # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── nova_auditoria.html
│   ├── selecao_ambito.html
│   ├── checklist.html
│   └── cliente_view.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Instalação Local

```bash
# Clonar o projeto
cd auditorias_brcgs

# Criar virtual environment
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar
python app.py
```

Aceder em: http://localhost:5000

**Credenciais de teste:**
- Email: filipa.ramos@simple2work.pt
- Password: Iamtheboss_2026

## Hospedagem em Railway

1. Criar conta em railway.app
2. Conectar repositório GitHub
3. Definir variável de ambiente:
   - `DATABASE_URL` (automático)
4. Deploy automático

Domínio: auditorias.simple2work.pt

## Funcionalidades

### Dashboard Admin (Filipa)
- Ver todas as auditorias
- Criar nova auditoria
- Editar checklist
- Ver estatísticas
- Gerar PDFs

### Link Compartilhado (Cliente)
- Aceder sem login
- Ver plano, checklist, relatório
- Gerar PDFs
- Read-only (sem edições)

### Checklist
- Split view (esquerda: requisitos, direita: formulário)
- Auto-preenchimento conforme classificação
- Classificações: Conforme, NC Menor, NC Maior, NC Crítica, Não Aplicável
- Campos: Descição, Evidência, Descrição da NC

## Cores Simple2Work
- Teal: #28939D
- Cinza: #333F48
- Fonte: Calibri Light

## Support
Para dúvidas ou ajustes: filipa.ramos@simple2work.pt
