from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import zoneinfo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atendimentos.db'
db = SQLAlchemy(app)

def get_hora_brasil():
    return datetime.now(zoneinfo.ZoneInfo('America/Sao_Paulo'))

# Modelo do Banco de Dados
class Atendimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    produto = db.Column(db.String(100))
    duvida = db.Column(db.Text)
    atendente = db.Column(db.String(50))
    assunto = db.Column(db.String(50))
    origem = db.Column(db.String(30))
    status = db.Column(db.String(20), default='Concluído')
    motivo_pendencia = db.Column(db.Text)
    resposta_final = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=get_hora_brasil)
    data_atendimento = db.Column(db.Date)

with app.app_context():
    db.create_all()

@app.route('/consulta')
def consulta():
    search = request.args.get('search', '')
    assunto_filtro = request.args.get('assunto', '')
    atendente_filtro = request.args.get('atendente', '')
    somente_hoje = request.args.get('hoje', '')
    somente_pendentes = request.args.get('pendente', '')

    query = Atendimento.query

    if search:
        query = query.filter(
            (Atendimento.cliente.contains(search)) | 
            (Atendimento.telefone.contains(search)) | 
            (Atendimento.produto.contains(search))
        )

    if assunto_filtro:
        query = query.filter(Atendimento.assunto == assunto_filtro)

    if atendente_filtro:
        query = query.filter(Atendimento.atendente == atendente_filtro)

    if somente_hoje == '1':
        hoje = get_hora_brasil().date()
        query = query.filter(Atendimento.data_atendimento == hoje)

    if somente_pendentes == '1':
        query = query.filter(Atendimento.status == 'Pendente')

    query = query.order_by(Atendimento.data_atendimento.desc(), Atendimento.id.desc())

    resultados = query.all()
    
    atendentes = ["Carlos", "Celso", "Lucas"]
    
    return render_template('consulta.html', atendimentos=resultados, atendentes=atendentes)

@app.route('/', methods=['GET', 'POST'])
def entrada():
    if request.method == 'POST':
        origem_recebida = request.form.get('origem', "Não Informada")
        data_atendimento_str = request.form.get('data_atendimento')
        data_formatada = datetime.strptime(data_atendimento_str, '%Y-%m-%d').date() if data_atendimento_str else get_hora_brasil().date()

        is_pendente = request.form.get('is_pendente')
        status = 'Pendente' if is_pendente else 'Concluído'
        motivo = request.form.get('motivo_pendencia', '') if is_pendente else ''

        novo_atendimento = Atendimento(
            cliente=request.form['cliente'],
            telefone=request.form['telefone'],
            produto=request.form['produto'],
            assunto=request.form['assunto'],
            duvida=request.form['duvida'],
            atendente=request.form['atendente'],
            origem=origem_recebida,
            data_atendimento=data_formatada,
            status=status,
            motivo_pendencia=motivo
        )
        db.session.add(novo_atendimento)
        db.session.commit()
        return redirect('/consulta')
    
    atendentes = ["Carlos", "Celso", "Lucas"]
    hoje = get_hora_brasil().strftime('%Y-%m-%d')
    return render_template('entrada.html', atendentes=atendentes, hoje=hoje)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    atendimento = Atendimento.query.get_or_404(id)
    if request.method == 'POST':
        atendimento.cliente = request.form['cliente']
        atendimento.telefone = request.form['telefone']
        atendimento.produto = request.form['produto']
        atendimento.assunto = request.form['assunto']
        atendimento.duvida = request.form['duvida']
        atendimento.origem = request.form.get('origem', atendimento.origem or "Não Informada")

        data_atendimento_str = request.form.get('data_atendimento')
        if data_atendimento_str:
            atendimento.data_atendimento = datetime.strptime(data_atendimento_str, '%Y-%m-%d').date()
            
        atendimento.resposta_final = request.form.get('resposta_final', '')
        
        if request.form.get('concluir'):
            atendimento.status = 'Concluído'
            
        db.session.commit()
        return redirect('/consulta')
    
    atendentes = ["Carlos", "Celso", "Lucas"]
    return render_template('entrada.html', atendentes=atendentes, atendimento=atendimento)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")