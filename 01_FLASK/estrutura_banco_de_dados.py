from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)

# Criar API flask
app = Flask(__name__)

#Criar instância de SQLAlchemy
app.config['SECRET_KEY'] = 'FDS!#RSDASX$A'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)
db:SQLAlchemy

# Definir a estrutura da tabela Postagem
# id_postagem, titulo, autor
class Postagem(db.Model):
    __tablename__= 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))
# Definir a estrutura da tabela Autor
# id_autor, nome, email, senha, admin, postagens
class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem') # Nome da CLASSE e não da TABELA
    
# Executar o comando para criar o banco de dados
def inicializar_banco():
    with app.app_context():
        logging.debug("Criando as tabelas...")
        db.create_all()

        if not Autor.query.filter_by(email='nilsonxp@gmail.com').first():
            logging.debug("Inserindo autor inicial...")
            autor = Autor(nome='nilson', email='nilsonxp@gmail.com', senha='123456', admin=True)
            db.session.add(autor)
            db.session.commit()
        else:
            logging.debug("Autor inicial já existe.")

if __name__ == '__main__':
    inicializar_banco()
