from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
import ipaddress

app = Flask(__name__)
app.secret_key = 'sua_chave_super_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiosque.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

class Conteudo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    imagem = db.Column(db.String(255), nullable=False)
    grupo = db.Column(db.String(80), nullable=False)

class Dispositivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    ip = db.Column(db.String(32), nullable=False)

class Regra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo_id = db.Column(db.Integer, db.ForeignKey('conteudo.id'), nullable=False)
    dispositivo_id = db.Column(db.Integer, db.ForeignKey('dispositivo.id'), nullable=False)
    ordem = db.Column(db.Integer, nullable=False, default=1)
    duracao = db.Column(db.Integer, nullable=False, default=10)
    conteudo = db.relationship("Conteudo")
    dispositivo = db.relationship("Dispositivo")

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

@app.context_processor
def inject_dark_mode():
    return dict(
        dark_mode=session.get('dark_mode', False),
        usuario_nome=session.get('usuario_nome', None),
        usuario_username=session.get('usuario_username', None)
    )

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", '').strip()
        senha = request.form.get("senha", '').strip()
        nome = request.form.get("nome", '').strip()

        if not username or not senha or not nome:
            flash("Preencha todos os campos.", "error")
            return render_template("register.html")
        if len(username) < 3 or len(senha) < 6:
            flash("Usuário mínimo 3 letras, senha mínimo 6 caracteres.", "error")
            return render_template("register.html")
        if Usuario.query.filter_by(username=username).first():
            flash("Usuário já existe!", "error")
            return render_template("register.html")

        senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")
        novo = Usuario(username=username, senha_hash=senha_hash, nome=nome)
        db.session.add(novo)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro DB ao registrar usuário: {e}")
            flash("Erro ao registrar usuário.", "error")
            return render_template("register.html")
        flash("Usuário registrado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('senha', '').strip()
        if not username or not senha:
            flash("Informe usuário e senha.", "error")
            return render_template('login.html')
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and bcrypt.check_password_hash(usuario.senha_hash, senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            session['usuario_username'] = usuario.username
            return redirect(url_for('painel'))
        flash("Usuário ou senha inválidos!", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        session['dark_mode'] = not session.get('dark_mode', False)
        return redirect(url_for('configuracoes'))
    return render_template('dashconfig.html')

@app.route('/painel')
@login_required
def painel():
    total_conteudos = Conteudo.query.count()
    total_dispositivos = Dispositivo.query.count()
    total_regras = Regra.query.count()
    return render_template(
        'dashpaineladm.html',
        total_conteudos=total_conteudos,
        total_dispositivos=total_dispositivos,
        total_regras=total_regras
    )

@app.route('/conteudos', methods=['GET', 'POST'])
@login_required
def conteudos():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        imagem = request.form.get('imagem', '').strip()
        grupo = request.form.get('grupo', '').strip()
        if not titulo or not imagem or not grupo:
            flash("Preencha todos os campos!", "error")
            return redirect('/conteudos')
        db.session.add(Conteudo(titulo=titulo, imagem=imagem, grupo=grupo))
        try:
            db.session.commit()
            flash("Conteúdo cadastrado com sucesso.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Erro ao cadastrar conteúdo.", "error")
            app.logger.error(f"Erro DB: {e}")
        return redirect('/conteudos')
    conteudos = Conteudo.query.order_by(Conteudo.id.desc()).all()
    return render_template('dashavisoconteudo.html', conteudos=conteudos)

@app.route('/conteudos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_conteudo(id):
    conteudo = Conteudo.query.get_or_404(id)
    if request.method == 'POST':
        conteudo.titulo = request.form.get('titulo', '').strip()
        conteudo.imagem = request.form.get('imagem', '').strip()
        conteudo.grupo = request.form.get('grupo', '').strip()
        if not conteudo.titulo or not conteudo.imagem or not conteudo.grupo:
            flash("Preencha todos os campos!", "error")
            return render_template('editarConteudo.html', conteudo=conteudo)  
        try:
            db.session.commit()
            flash("Conteúdo atualizado.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Erro ao atualizar.", "error")
            app.logger.error(f"Erro DB: {e}")
        return redirect('/conteudos')
    return render_template('editarConteudo.html', conteudo=conteudo)  


@app.route('/conteudos/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_conteudo(id):
    conteudo = Conteudo.query.get_or_404(id)
    try:
        db.session.delete(conteudo)
        db.session.commit()
        flash("Conteúdo removido.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao deletar conteúdo.", "error")
        app.logger.error(f"Erro DB: {e}")
    return redirect('/conteudos')

@app.route('/dispositivos', methods=['GET', 'POST'])
@login_required
def dispositivos():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        ip = request.form.get('ip', '').strip()
        if not nome:
            flash("Nome do dispositivo não pode ser vazio.", "error")
            return redirect('/dispositivos')
        if not is_valid_ip(ip):
            flash("Endereço IP inválido.", "error")
            return redirect('/dispositivos')
        db.session.add(Dispositivo(nome=nome, ip=ip))
        try:
            db.session.commit()
            flash("Dispositivo cadastrado.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Erro ao cadastrar dispositivo.", "error")
            app.logger.error(f"Erro DB: {e}")
        return redirect('/dispositivos')
    dispositivos = Dispositivo.query.order_by(Dispositivo.id.desc()).all()
    return render_template('dashdispositivos.html', dispositivos=dispositivos)

@app.route('/dispositivos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_dispositivo(id):
    dispositivo = Dispositivo.query.get_or_404(id)
    if request.method == 'POST':
        dispositivo.nome = request.form.get('nome', '').strip()
        ip = request.form.get('ip', '').strip()
        if not dispositivo.nome:
            flash("Nome do dispositivo não pode ser vazio.", "error")
            return render_template('editarDispositivo.html', dispositivo=dispositivo)
        if not is_valid_ip(ip):
            flash("Endereço IP inválido.", "error")
            return render_template('editarDispositivo.html', dispositivo=dispositivo)
        dispositivo.ip = ip
        try:
            db.session.commit()
            flash("Dispositivo atualizado.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Erro ao atualizar.", "error")
            app.logger.error(f"Erro DB: {e}")
        return redirect('/dispositivos')
    return render_template('editarDispositivo.html', dispositivo=dispositivo)


@app.route('/dispositivos/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_dispositivo(id):
    dispositivo = Dispositivo.query.get_or_404(id)
    try:
        db.session.delete(dispositivo)
        db.session.commit()
        flash("Dispositivo removido.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao deletar dispositivo.", "error")
        app.logger.error(f"Erro DB: {e}")
    return redirect('/dispositivos')

@app.route('/regras', methods=['GET', 'POST'])
@login_required
def regras():
    if request.method == 'POST':
        try:
            conteudo_id = int(request.form['conteudo_id'])
            dispositivo_id = int(request.form['dispositivo_id'])
            ordem = int(request.form['ordem'])
            duracao = int(request.form['duracao'])
        except (ValueError, TypeError):
            flash("Preencha todos os campos corretamente.", "error")
            return redirect('/regras')
        if ordem < 1 or duracao < 5:
            flash("Ordem deve ser >= 1 e duração >= 5 segundos.", "error")
            return redirect('/regras')
        regra = Regra(conteudo_id=conteudo_id, dispositivo_id=dispositivo_id, ordem=ordem, duracao=duracao)
        db.session.add(regra)
        try:
            db.session.commit()
            flash("Regra cadastrada.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Erro ao cadastrar regra.", "error")
            app.logger.error(f"Erro DB: {e}")
        return redirect('/regras')
    conteudos = Conteudo.query.all()
    dispositivos = Dispositivo.query.all()
    regras = Regra.query.order_by(Regra.dispositivo_id, Regra.ordem).all()
    return render_template('dashregrasnegocio.html', conteudos=conteudos, dispositivos=dispositivos, regras=regras)

@app.route('/regras/remover/<int:id>', methods=['POST'])
@login_required
def remover_regra(id):
    regra = Regra.query.get_or_404(id)
    try:
        db.session.delete(regra)
        db.session.commit()
        flash("Regra removida.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao remover regra.", "error")
        app.logger.error(f"Erro DB: {e}")
    return redirect('/regras')

@app.route('/display')
def display():
    ip = request.args.get('ip') or request.remote_addr
    dispositivo = Dispositivo.query.filter_by(ip=ip).first()
    if not dispositivo:
        return render_template('erro.html', mensagem="Dispositivo não cadastrado."), 403

    regras = Regra.query.filter_by(dispositivo_id=dispositivo.id).order_by(Regra.ordem).all()
    banners = [r.conteudo for r in regras]
    duracoes = [r.duracao for r in regras]

    banner_imgs = [c.imagem for c in banners]
    banner1_imgs = banner_imgs[::2] or ['default1.png']
    banner2_imgs = banner_imgs[1::2] or ['default2.png']

    return render_template(
        'display.html',
        dispositivo=dispositivo,
        banner1_imgs=banner1_imgs,
        banner2_imgs=banner2_imgs,
        duracoes=duracoes
    )

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Banco de dados criado.")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
