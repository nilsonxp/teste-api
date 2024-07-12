from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor,Postagem,app,db,inicializar_banco
import logging
import json
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

# app = Flask(__name__) #Vamos utilizar o Flask do Banco de Dados

'''
1- Definir o objetivo da API:
ex: Iremos montar uma api de blog, onde eu poderei consultar, editar, criar e excluir postagens em um blog usando a API

2 - Qual será o URL base do api?
ex: Quando você cria uma aplicação local ela terá um url tipo http://localhost:5000 , porém quando você for subir isso para nuvem, você terá que comprar ou usar um domínio como url base, vamos imaginar um exemplo de devaprender.com/api/

3 - Quais são os endpoints?
ex: Se seu requisito é de poder consultar, editar, criar e excluir, você terá que disponibilizar os endpoints para essas questões
    > /postagens/

4 - Quais recursos será disponibilizado pelo api: informações sobre as postagens

5 - Quais verbos http serão disponibilizados?
* GET
* POST
* PUT
* DELETE

6 - Quais são os URL completos para cada um?

* GET http://localhost:5000/postagens
* GET id http://localhost:5000/postagens/1
* POST id http://localhost:5000/postagens
* PUT id http://localhost:5000/postagens/1
* DELETE id http://localhost:5000/postagens/1
'''

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)

def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem':'Token não foi incluído'}), 401
        # Se temos um token, validar acesso ao BD
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensagem': 'Token é inválido'}), 401
        except Exception as e:
            return jsonify({'mensagem': 'Erro na verificação do token', 'erro': str(e)}), 401
        return f(autor, *args, **kwargs)
    return decorated

# Login
@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido',401,{'www-Authenticate':'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido',401,{'www-Authenticate':'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.now(timezone.utc) + timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token':token})
    return make_response('Login inválido',401,{'www-Authenticate':'Basic realm="Login obrigatório"'})
    
# Rota padrão - GET http://localhost:8000/
@app.route('/')
@token_obrigatorio
def obter_postagens(autor):
    postagens = Postagem.query.all()

    list_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        list_postagens.append(postagem_atual)
    return jsonify({'postagens': list_postagens})

# Get com Id http://localhost:8000/postagem/1
@app.route('/postagem/<int:indice>',methods=['GET'])
@token_obrigatorio
def obter_postagem_por_indice(autor,indice):
    postagem = Postagem.query.filter_by(id_postagem=indice).first()
    postagem_atual = {}
    try:
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass
    postagem_atual['id_autor'] = postagem.id_autor

    return jsonify({'postagens': postagem_atual})

# Criar uma nova postagem - POST http://localhost:8000/postagem
@app.route('/postagem',methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(
        titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])

    db.session.add(postagem)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem criada com sucesso'})

# Rota para atualizar uma postagem existente - PUT http://localhost:8000/postagem/1
@app.route('/postagem/<int:indice>', methods=['PUT'])
@token_obrigatorio
def atualizar_postagem(autor,indice):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=indice).first()
    try:
        postagem.titulo = postagem_alterada['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_alterada['id_autor']
    except:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Postagem alterada com sucessso'})

# Excluir uma postagem - DELETE http://localhost:8000/postagem/1
@app.route('/postagem/<int:indice>',methods=['DELETE'])
@token_obrigatorio
def excluir_postagem(autor,indice):
    postagem_a_ser_excluida = Postagem.query.filter_by(
        id_postagem=indice).first()
    if not postagem_a_ser_excluida:
        return jsonify({'mensagem': 'Não foi encontrado uma postagem com este id'})
    db.session.delete(postagem_a_ser_excluida)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem excluída com sucesso!'})

# ------------------------------------ AUTORES -----------------------

@app.route('/autores', methods=['GET']) #melhorado
@token_obrigatorio
def obter_autores(autor):
    try:
        autores = Autor.query.all()
        logging.debug(f"Autores recuperados: {autores}")
        lista_de_autores = [{'id_autor': autor.id_autor, 'nome': autor.nome, 'email': autor.email} for autor in autores]
        return jsonify({'autores': lista_de_autores})
    except Exception as e:
        logging.error(f"Erro ao obter autores: {e}")
        return jsonify({'erro': 'Erro ao obter autores'}, 500)
    
# @app.route('/autores', methods=['GET'])
# def obter_autores():
#     autores = Autor.query.all()
#     lista_de_autores = []
#     for autor in autores:
#         autor_atual = {}
#         autor_atual['id_autor'] = autor.id_autor
#         autor_atual['nome'] = autor.nome
#         autor_atual['email'] = autor.email
#         lista_de_autores.append(autor_atual)
#     return jsonify({'autores':lista_de_autores})

@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_por_id(autor,id_autor):
    try:
        autor = Autor.query.get(id_autor)
        if autor:
            return jsonify({'id_autor': autor.id_autor, 'nome': autor.nome, 'email': autor.email})
        return jsonify({'erro': 'Autor não encontrado'}, 404)
    except Exception as e:
        logging.error(f"Erro ao obter autor por ID: {e}")
        return jsonify({'erro': 'Erro ao obter autor por ID'}, 500)

@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    try:
        autor = request.get_json()
        novo_autor = Autor(nome=autor['nome'], email=autor['email'], senha=autor['senha'])
        db.session.add(novo_autor)
        db.session.commit()
        return jsonify({'id_autor': novo_autor.id_autor, 'nome': novo_autor.nome, 'email': novo_autor.email})
    except Exception as e:
        logging.error(f"Erro ao criar novo autor: {e}")
        return jsonify({'erro': 'Erro ao criar novo autor'}, 500)
    
@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor,id_autor):
    try:
        dados = request.get_json()
        autor_att = Autor.query.get(id_autor)
        if autor_att:
            if 'nome' in dados:
                autor_att.nome = dados['nome']
            if 'email' in dados:
                autor_att.email = dados['email']
            if 'senha' in dados:
                autor_att.senha = dados['senha']
            if 'admin' in dados:
                autor_att.admin = dados['admin']
            db.session.commit()
            return jsonify({'id_autor': autor_att.id_autor, 'nome': autor_att.nome, 'email': autor_att.email})
        return jsonify({'erro': 'Autor não encontrado'}, 404)
    except Exception as e:
        logging.error(f"Erro ao alterar autor: {e}")
        return jsonify({'erro': 'Erro ao alterar autor'}, 500)

@app.route('/autores/<int:id_autor>',methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor,id_autor):
    try:
        autor_existente = Autor.query.get(id_autor)
        if autor_existente:
            nome = autor_existente.nome
            db.session.delete(autor_existente)
            db.session.commit()
            return jsonify(f'O autor {nome}, com id {id_autor} foi excluído', 204)
        return jsonify({'erro': 'Autor não encontrado'}, 404)
    except Exception as e:
        logging.error(f"Erro ao excluir autor: {e}")
        return jsonify({'erro': 'Erro ao excluir autor'}, 500)



if __name__ == '__main__':
    inicializar_banco()
    app.run(port=8000, host='localhost', debug=True)
