from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import uuid
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple2work_auditorias_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auditorias.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Cores Simple2Work
TEAL = '#28939D'
CINZA = '#333f48'
BRANCO = '#FAFAFA'

# Requisitos BRCGS
REQUISITOS_BRCGS = {
    '1': {
        'titulo': '1. Compromisso da Direção e Melhoria Contínua',
        'subsecoes': {
            '1.1': {
                'titulo': '1.1. Compromisso da Direção e Melhoria Contínua',
                'requisitos': [
                    {'id': '1.1.1', 'desc': 'Política de qualidade e segurança alimentar definida'},
                    {'id': '1.1.2', 'desc': 'Objetivos da segurança alimentar definidos'},
                    {'id': '1.1.3', 'desc': 'Responsabilidades e autoridades definidas'},
                    {'id': '1.1.4', 'desc': 'Cultura de segurança alimentar promovida'},
                    {'id': '1.1.5', 'desc': 'Comunicação eficaz sobre segurança alimentar'},
                ]
            }
        }
    },
    '2': {
        'titulo': '2. O Plano de Segurança Alimentar',
        'subsecoes': {
            '2.1': {
                'titulo': '2.1. Equipa de Segurança Alimentar - HACCP',
                'requisitos': [
                    {'id': '2.1.1', 'desc': 'Equipa HACCP constituída e competente'},
                    {'id': '2.1.2', 'desc': 'Âmbito do plano HACCP definido'},
                ]
            },
            '2.2': {
                'titulo': '2.2. Programa de Pré-Requisitos',
                'requisitos': [
                    {'id': '2.2.1', 'desc': 'Programas pré-requisitos implementados'},
                    {'id': '2.2.2', 'desc': 'Boas práticas de higiene implementadas'},
                ]
            }
        }
    },
    '3': {
        'titulo': '3. Sistema de Gestão da Qualidade e Segurança',
        'subsecoes': {
            '3.1': {
                'titulo': '3.1. Manual de Segurança e Qualidade Alimentar',
                'requisitos': [
                    {'id': '3.1.1', 'desc': 'Manual de segurança alimentar elaborado'},
                    {'id': '3.1.2', 'desc': 'Procedimentos documentados'},
                ]
            }
        }
    },
    '4': {
        'titulo': '4. Normas do Site',
        'subsecoes': {
            '4.1': {
                'titulo': '4.1. Normas Externas e Segurança das Instalações',
                'requisitos': [
                    {'id': '4.1.1', 'desc': 'Instalações adequadas ao processo'},
                    {'id': '4.1.2', 'desc': 'Layouts adequados'},
                ]
            }
        }
    },
    '5': {
        'titulo': '5. Controlo de Produto',
        'subsecoes': {
            '5.1': {
                'titulo': '5.1. Conceção/Desenvolvimento de Produtos',
                'requisitos': [
                    {'id': '5.1.1', 'desc': 'Processo de conceção de produtos estabelecido'},
                    {'id': '5.1.2', 'desc': 'Avaliação de perigos realizada'},
                ]
            }
        }
    },
    '6': {
        'titulo': '6. Controlo dos Processos',
        'subsecoes': {
            '6.1': {
                'titulo': '6.1. Controlo das Operações',
                'requisitos': [
                    {'id': '6.1.1', 'desc': 'Pontos críticos de controlo identificados'},
                    {'id': '6.1.2', 'desc': 'Limites críticos estabelecidos'},
                ]
            }
        }
    },
    '7': {
        'titulo': '7. Pessoal',
        'subsecoes': {
            '7.1': {
                'titulo': '7.1. Formação: Manuseamento de Matérias-Primas',
                'requisitos': [
                    {'id': '7.1.1', 'desc': 'Plano de formação implementado'},
                    {'id': '7.1.2', 'desc': 'Registos de formação mantidos'},
                ]
            }
        }
    }
}

# Models
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<Admin {self.email}>'

class Auditoria(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empresa = db.Column(db.String(200), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    local = db.Column(db.String(200))
    objetivo = db.Column(db.Text)
    tipo = db.Column(db.String(100))
    duracao = db.Column(db.String(50))
    requisitos_selecionados = db.Column(db.JSON, default={})
    checklist_data = db.Column(db.JSON, default={})
    link_compartilhado = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    def __repr__(self):
        return f'<Auditoria {self.empresa}>'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')
        
        admin = Admin.query.filter_by(email=email).first()
        
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro='Email ou password incorretos')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    auditorias = Auditoria.query.order_by(Auditoria.data.desc()).all()
    return render_template('dashboard.html', auditorias=auditorias, teal=TEAL, cinza=CINZA)

@app.route('/nova-auditoria', methods=['GET', 'POST'])
@login_required
def nova_auditoria():
    if request.method == 'POST':
        data = request.get_json()
        auditoria = Auditoria(
            empresa=data.get('empresa'),
            local=data.get('local'),
            objetivo=data.get('objetivo'),
            tipo=data.get('tipo'),
            duracao=data.get('duracao')
        )
        db.session.add(auditoria)
        db.session.commit()
        return jsonify({'id': auditoria.id}), 201
    
    return render_template('nova_auditoria.html', teal=TEAL, cinza=CINZA)

@app.route('/auditoria/<audit_id>/ambito', methods=['GET', 'POST'])
@login_required
def selecao_ambito(audit_id):
    auditoria = Auditoria.query.get(audit_id)
    if not auditoria:
        return 'Auditoria não encontrada', 404
    
    if request.method == 'POST':
        data = request.get_json()
        auditoria.requisitos_selecionados = data.get('requisitos')
        db.session.commit()
        return jsonify({'sucesso': True}), 200
    
    return render_template('selecao_ambito.html', auditoria=auditoria, requisitos=REQUISITOS_BRCGS, teal=TEAL, cinza=CINZA)

@app.route('/auditoria/<audit_id>/checklist', methods=['GET', 'POST'])
@login_required
def checklist(audit_id):
    auditoria = Auditoria.query.get(audit_id)
    if not auditoria:
        return 'Auditoria não encontrada', 404
    
    if request.method == 'POST':
        data = request.get_json()
        auditoria.checklist_data = data.get('checklist')
        db.session.commit()
        return jsonify({'sucesso': True}), 200
    
    return render_template('checklist.html', auditoria=auditoria, requisitos=REQUISITOS_BRCGS, teal=TEAL, cinza=CINZA)

@app.route('/share/<link_id>')
def cliente_view(link_id):
    auditoria = Auditoria.query.filter_by(link_compartilhado=link_id).first()
    if not auditoria:
        return 'Link inválido ou expirado', 404
    
    return render_template('cliente_view.html', auditoria=auditoria, teal=TEAL, cinza=CINZA)

@app.route('/api/auditoria/<audit_id>')
@login_required
def get_auditoria(audit_id):
    auditoria = Auditoria.query.get(audit_id)
    if not auditoria:
        return jsonify({'erro': 'Não encontrada'}), 404
    
    return jsonify({
        'id': auditoria.id,
        'empresa': auditoria.empresa,
        'data': auditoria.data.isoformat(),
        'local': auditoria.local,
        'objetivo': auditoria.objetivo,
        'tipo': auditoria.tipo,
        'duracao': auditoria.duracao,
        'requisitos': auditoria.requisitos_selecionados,
        'checklist': auditoria.checklist_data,
        'link_compartilhado': auditoria.link_compartilhado
    })

@app.route('/gerar-pdf/<audit_id>/<tipo>')
@login_required
def gerar_pdf(audit_id, tipo):
    auditoria = Auditoria.query.get(audit_id)
    if not auditoria:
        return 'Auditoria não encontrada', 404
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    elements = []
    
    # Estilo
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(TEAL),
        spaceAfter=30,
    )
    
    # Conteúdo baseado no tipo
    if tipo == 'plano':
        elements.append(Paragraph('Plano de Auditoria', titulo_style))
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(f'<b>Empresa:</b> {auditoria.empresa}', styles['Normal']))
        elements.append(Paragraph(f'<b>Data:</b> {auditoria.data.strftime("%d/%m/%Y")}', styles['Normal']))
        elements.append(Paragraph(f'<b>Local:</b> {auditoria.local}', styles['Normal']))
        elements.append(Paragraph(f'<b>Objetivo:</b> {auditoria.objetivo}', styles['Normal']))
    
    elif tipo == 'checklist':
        elements.append(Paragraph('Checklist de Auditoria', titulo_style))
        elements.append(Spacer(1, 0.5*cm))
        # Aqui irá a checklist com os dados preenchidos
        
    elif tipo == 'relatorio':
        elements.append(Paragraph('Relatório de Auditoria', titulo_style))
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(f'<b>Empresa:</b> {auditoria.empresa}', styles['Normal']))
        elements.append(Paragraph(f'<b>Data:</b> {auditoria.data.strftime("%d/%m/%Y")}', styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{tipo}_{auditoria.empresa}_{auditoria.data.strftime("%d_%m_%Y")}.pdf'
    )

# Init database
with app.app_context():
    db.create_all()
    
    # Criar admin por defeito se não existir
    if not Admin.query.filter_by(email='filipa.ramos@simple2work.pt').first():
        admin = Admin(
            email='filipa.ramos@simple2work.pt',
            password=generate_password_hash('Iamtheboss_2026')
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
