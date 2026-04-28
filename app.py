from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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
    data_criacao = db.Column(db.DateTime, default=get_hora_brasil)

with app.app_context():
    db.create_all()

@app.route('/consulta')
def consulta():
    search = request.args.get('search', '')
    # Busca flexível por nome, telefone ou produto
    if search:
        resultados = Atendimento.query.filter(
            (Atendimento.cliente.contains(search)) | 
            (Atendimento.telefone.contains(search)) | 
            (Atendimento.produto.contains(search))
        ).all()
    else:
        resultados = Atendimento.query.all()
    
    return render_template('consulta.html', atendimentos=resultados)

@app.route('/', methods=['GET', 'POST'])
def entrada():
    if request.method == 'POST':
        # Captura com segurança: se vier vazio/nulo, atribui uma string válida
        origem_recebida = request.form.get('origem')
        if not origem_recebida:
            origem_recebida = "Não Informada"

        novo_atendimento = Atendimento(
            cliente=request.form['cliente'],
            telefone=request.form['telefone'],
            produto=request.form['produto'],
            assunto=request.form['assunto'],
            duvida=request.form['duvida'],
            atendente=request.form['atendente'],
            origem=origem_recebida
        )
        db.session.add(novo_atendimento)
        db.session.commit()
        return redirect('/consulta')
    
    atendentes = ["Carlos", "Celso", "Lucas"]
    return render_template('entrada.html', atendentes=atendentes)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    atendimento = Atendimento.query.get_or_404(id)
    if request.method == 'POST':
        atendimento.cliente = request.form['cliente']
        atendimento.telefone = request.form['telefone']
        atendimento.produto = request.form['produto']
        atendimento.assunto = request.form['assunto']
        atendimento.duvida = request.form['duvida']
        
        # Atualiza a origem se ela vier no formulário. Se for um registo antigo nulo, corrige-o.
        origem_recebida = request.form.get('origem')
        if origem_recebida:
            atendimento.origem = origem_recebida
        elif not atendimento.origem:
            atendimento.origem = "Não Informada"
            
        db.session.commit()
        return redirect('/consulta')
    
    atendentes = ["Carlos", "Celso", "Lucas"]
    return render_template('entrada.html', atendentes=atendentes, atendimento=atendimento)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")