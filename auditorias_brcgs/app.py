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

# Requisitos BRCGS (mantém-se igual)
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
    
    # Novos campos para Plano de Auditoria
    data_realizacao = db.Column(db.String(50))  # Data de realização (editável)
    ambito = db.Column(db.Text)  # Âmbito da auditoria
    requisitos_nao_aplicaveis = db.Column(db.Text)  # Requisitos não aplicáveis
    equipa_auditora = db.Column(db.JSON, default={})  # {'nome': 'Filipa Ramos', 'cv_file': 'uuid1', 'cert1_file': 'uuid2', 'cert2_file': 'uuid3'}
    identificacao_colaboradores = db.Column(db.Text)  # Identificação dos colaboradores
    documentos_referencia = db.Column(db.Text)  # Documentos de referência
    idioma = db.Column(db.String(50))  # Idioma da auditoria
    programa_auditoria = db.Column(db.JSON, default=[])  # Lista de linhas da tabela
    observacoes = db.Column(db.Text)  # Observações
    abreviaturas = db.Column(db.JSON, default={})  # {'FR': 'Filipa Ramos', 'EA': 'Equipa Auditora'}
    data_plano = db.Column(db.DateTime, default=datetime.utcnow)  # Data do plano (editável)
    
    # Campos originais
    requisitos_selecionados = db.Column(db.JSON, default={})
    checklist_data = db.Column(db.JSON, default={})
    link_compartilhado = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    def __repr__(self):
        return f'<Auditoria {self.empresa}>'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
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
    auditorias = Auditoria.query.all()
    return render_template('dashboard.html', auditorias=auditorias, teal=TEAL, cinza=CINZA)

@app.route('/nova-auditoria', methods=['GET', 'POST'])
@login_required
def nova_auditoria():
    if request.method == 'POST':
        # Processar dados básicos da auditoria
        auditoria = Auditoria(
            empresa=request.form.get('empresa'),
            local=request.form.get('local'),
            objetivo=request.form.get('objetivo'),
            tipo=request.form.get('tipo'),
            duracao=request.form.get('duracao'),
            data_realizacao=request.form.get('data_realizacao'),
            ambito=request.form.get('ambito'),
            requisitos_nao_aplicaveis=request.form.get('requisitos_nao_aplicaveis'),
            identificacao_colaboradores=request.form.get('identificacao_colaboradores'),
            documentos_referencia=request.form.get('documentos_referencia'),
            idioma=request.form.get('idioma'),
            observacoes=request.form.get('observacoes'),
            data_plano=datetime.strptime(request.form.get('data_plano'), '%Y-%m-%d') if request.form.get('data_plano') else datetime.utcnow()
        )
        
        # Processar Equipa Auditora com ficheiros
        equipa_nome = request.form.get('equipa_nome')
        equipa_data = {'nome': equipa_nome}

        # Processar uploads de CV e certificados
        if 'equipa_cv' in request.files and request.files['equipa_cv'].filename:
            cv_file = request.files['equipa_cv']
            cv_filename = f"cv_{auditoria.id}_{uuid.uuid4()}.pdf"
            cv_path = os.path.join('uploads', cv_filename)
            os.makedirs('uploads', exist_ok=True)
            cv_file.save(cv_path)
            equipa_data['cv_file'] = cv_filename

        if 'equipa_cert1' in request.files and request.files['equipa_cert1'].filename:
            cert1_file = request.files['equipa_cert1']
            cert1_filename = f"cert1_{auditoria.id}_{uuid.uuid4()}.pdf"
            cert1_path = os.path.join('uploads', cert1_filename)
            cert1_file.save(cert1_path)
            equipa_data['cert1_file'] = cert1_filename

        if 'equipa_cert2' in request.files and request.files['equipa_cert2'].filename:
            cert2_file = request.files['equipa_cert2']
            cert2_filename = f"cert2_{auditoria.id}_{uuid.uuid4()}.pdf"
            cert2_path = os.path.join('uploads', cert2_filename)
            cert2_file.save(cert2_path)
            equipa_data['cert2_file'] = cert2_filename

        auditoria.equipa_auditora = equipa_data
        
        # Processar Programa da Auditoria (tabela)
        programa = []
        horas = request.form.getlist('programa_hora[]')
        processos = request.form.getlist('programa_processo[]')
        auditores = request.form.getlist('programa_auditor[]')
        
        for hora, processo, auditor in zip(horas, processos, auditores):
            if hora and processo:  # Apenas linhas preenchidas
                programa.append({
                    'hora': hora,
                    'processo': processo,
                    'auditor': auditor
                })
        auditoria.programa_auditoria = programa
        
        # Processar Abreviaturas
        abreviaturas = {}
        for i in range(1, 5):  # Até 4 abreviaturas
            abrev = request.form.get(f'abrev_sigla_{i}')
            desc = request.form.get(f'abrev_descricao_{i}')
            if abrev and desc:
                abreviaturas[abrev] = desc
        auditoria.abreviaturas = abreviaturas
        
        db.session.add(auditoria)
        db.session.commit()
        
        return redirect(url_for('selecao_ambito', audit_id=auditoria.id))
    
    return render_template('nova_auditoria.html', teal=TEAL, cinza=CINZA)

@app.route('/auditoria/<audit_id>/ambito')
@login_required
def selecao_ambito(audit_id):
    auditoria = Auditoria.query.get(audit_id)
    if not auditoria:
        return 'Auditoria não encontrada', 404
    
    return render_template('selecao_ambito.html', auditoria=auditoria, requisitos=REQUISITOS_BRCGS, teal=TEAL, cinza=CINZA)

@app.route('/api/salvar-ambito', methods=['POST'])
@login_required
def salvar_ambito():
    data = request.get_json()
    audit_id = data.get('audit_id')
    requisitos = data.get('requisitos', {})
    
    auditoria = Auditoria.query.get(audit_id)
    if auditoria:
        auditoria.requisitos_selecionados = requisitos
        db.session.commit()
        return jsonify({'sucesso': True, 'redirect': url_for('checklist', audit_id=audit_id)}), 200
    
    return jsonify({'erro': 'Auditoria não encontrada'}), 404

@app.route('/auditoria/<audit_id>/checklist')
@login_required
def checklist(audit_id):
    auditoria = Auditoria.query.get(audit_id)
    if not auditoria:
        return 'Auditoria não encontrada', 404
    
    return render_template('checklist.html', auditoria=auditoria, requisitos=REQUISITOS_BRCGS, teal=TEAL, cinza=CINZA)

@app.route('/api/guardar-requisito', methods=['POST'])
@login_required
def guardar_requisito():
    data = request.get_json()
    audit_id = data.get('audit_id')
    requisito_id = data.get('requisito_id')
    checklist = data.get('checklist', {})
    
    auditoria = Auditoria.query.get(audit_id)
    if auditoria:
        current_checklist = auditoria.checklist_data or {}
        current_checklist.update(checklist)
        auditoria.checklist_data = current_checklist
        db.session.commit()
        return jsonify({'sucesso': True}), 200
    
    return jsonify({'erro': 'Auditoria não encontrada'}), 404

@app.route('/share/<link_id>')
def cliente_view(link_id):
    auditoria = Auditoria.query.filter_by(link_compartilhado=link_id).first()
    if not auditoria:
        return 'Link inválido ou expirado', 404

    return render_template('cliente_view.html', auditoria=auditoria, teal=TEAL, cinza=CINZA)

@app.route('/download/<audit_id>/<file_type>')
def download_file(audit_id, file_type):
    auditoria = Auditoria.query.get(audit_id)
    if not auditoria:
        return 'Auditoria não encontrada', 404

    equipa = auditoria.equipa_auditora
    if not isinstance(equipa, dict):
        return 'Ficheiro não encontrado', 404

    filename = None
    if file_type == 'cv' and 'cv_file' in equipa:
        filename = equipa['cv_file']
    elif file_type == 'cert1' and 'cert1_file' in equipa:
        filename = equipa['cert1_file']
    elif file_type == 'cert2' and 'cert2_file' in equipa:
        filename = equipa['cert2_file']

    if not filename:
        return 'Ficheiro não encontrado', 404

    filepath = os.path.join('uploads', filename)
    if not os.path.exists(filepath):
        return 'Ficheiro não encontrado no servidor', 404

    return send_file(filepath, as_attachment=True, download_name=filename)

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
        'data_realizacao': auditoria.data_realizacao,
        'ambito': auditoria.ambito,
        'idioma': auditoria.idioma,
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
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor(TEAL),
        spaceAfter=10,
    )
    
    # Conteúdo baseado no tipo
    if tipo == 'plano':
        # Título
        elements.append(Paragraph('Plano de Auditoria', titulo_style))
        elements.append(Spacer(1, 0.3*cm))
        
        # 1. Data, Local e Duração
        elements.append(Paragraph('1. Data, Local e Duração da Auditoria', heading_style))
        data_table = Table([
            ['Data', auditoria.data_realizacao or auditoria.data.strftime('%d/%m/%Y')],
            ['Local', auditoria.local or ''],
            ['Duração', auditoria.duracao or ''],
        ], colWidths=[2*cm, 10*cm])
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(TEAL)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(data_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # 2. Objetivo
        elements.append(Paragraph('2. Objetivo da Auditoria', heading_style))
        elements.append(Paragraph(auditoria.objetivo or '', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        
        # 3. Âmbito
        elements.append(Paragraph('3. Âmbito da Auditoria', heading_style))
        elements.append(Paragraph(auditoria.ambito or '', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        
        # 4. Requisitos não aplicáveis
        elements.append(Paragraph('4. Requisitos Não Aplicáveis ao Âmbito da Auditoria', heading_style))
        elements.append(Paragraph(auditoria.requisitos_nao_aplicaveis or 'Os requisitos não aplicáveis são identificados no decorrer da auditoria.', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        
        # 5. Equipa Auditora
        elements.append(Paragraph('5. Constituição da Equipa Auditora', heading_style))
        equipa_nome = auditoria.equipa_auditora.get('nome') if isinstance(auditoria.equipa_auditora, dict) else 'Não preenchida'
        elements.append(Paragraph(f'A Equipa Auditora (EA) será constituída pelo seguinte elemento:<br/>- {equipa_nome} (Auditor Coordenador)', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        
        # 6. Identificação dos Colaboradores
        elements.append(Paragraph('6. Identificação dos Colaboradores da Empresa com Responsabilidades Diretas no Objetivo e Âmbito da Auditoria', heading_style))
        elements.append(Paragraph(auditoria.identificacao_colaboradores or 'Esta identificação será efetuada no decurso da auditoria e de acordo com o seu programa.', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        
        # 7. Documentos de Referência
        elements.append(Paragraph('7. Documentos de Referência', heading_style))
        elements.append(Paragraph(auditoria.documentos_referencia or 'BRC Food V9', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        
        # 8. Idioma
        elements.append(Paragraph('8. Idioma utilizado em auditoria', heading_style))
        elements.append(Paragraph(f'A auditoria será realizada em {auditoria.idioma or "Português"}.', styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        
        elements.append(PageBreak())
        
        # 9. Programa da Auditoria (Página 2)
        elements.append(Paragraph('9. Programa da Auditoria', heading_style))
        elements.append(Spacer(1, 0.3*cm))
        
        # Tabela do Programa
        if auditoria.programa_auditoria:
            programa_data = [['Hora', 'Processo/Assunto/Requisito', 'Auditor(es)']]
            for linha in auditoria.programa_auditoria:
                programa_data.append([
                    linha.get('hora', ''),
                    linha.get('processo', ''),
                    linha.get('auditor', '')
                ])

            programa_table = Table(programa_data, colWidths=[2*cm, 11*cm, 3*cm])
            programa_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(TEAL)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(programa_table)
        
        elements.append(Spacer(1, 0.5*cm))
        
        # Observações
        elements.append(Paragraph('Observações:', heading_style))
        obs_text = auditoria.observacoes or 'Este plano poderá ser alvo de ajustes no decurso da auditoria.<br/>Toda a documentação é considerada estritamente confidencial.'
        elements.append(Paragraph(obs_text, styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Abreviaturas
        elements.append(Paragraph('Abreviaturas:', heading_style))
        if auditoria.abreviaturas:
            for sigla, descricao in auditoria.abreviaturas.items():
                elements.append(Paragraph(f'- {sigla} – {descricao}', styles['Normal']))
        else:
            elements.append(Paragraph('- FR – Filipa Ramos<br/>- EA – Equipa Auditora', styles['Normal']))
        
        elements.append(Spacer(1, 1*cm))
        
        # Assinatura
        equipa_nome = auditoria.equipa_auditora.get('nome') if isinstance(auditoria.equipa_auditora, dict) else 'Filipa Ramos'
        elements.append(Paragraph('Com os melhores cumprimentos,', styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(f'<b>{equipa_nome}</b>', styles['Normal']))
        elements.append(Paragraph('(Auditor Coordenador)', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(auditoria.data_plano.strftime('%d de %B de %Y'), styles['Normal']))
    
    elif tipo == 'checklist':
        elements.append(Paragraph('Checklist de Auditoria', titulo_style))
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(f'<b>Empresa:</b> {auditoria.empresa}', styles['Normal']))
        elements.append(Paragraph(f'<b>Data:</b> {auditoria.data.strftime("%d/%m/%Y")}', styles['Normal']))
        
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
