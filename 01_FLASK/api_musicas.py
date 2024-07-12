from flask import Flask, jsonify, request

app = Flask(__name__)

musicas = [
    {
    'cancao': 'Jeová Jireh',
    'estilo': 'Gospel',
    },
    {
    'cancao': 'Geração Coca-Cola',
    'estilo': 'Pop',
    },
]

# Rota padrão - GET http://localhost:8000/
@app.route('/')
def obter_musica():
    return jsonify(musicas)

# Get com Id http://localhost:8000/musica/1
@app.route('/musicas/<int:indice>',methods=['GET'])
def obter_musica_por_indice(indice):
    return jsonify(musicas[indice])

# Criar uma nova postagem - POST http://localhost:8000/musica
@app.route('/musica',methods=['POST'])
def nova_musica():
    musica = request.get_json()
    musicas.append(musica)
    return jsonify(musica,200)

# Rota para atualizar uma musica existente - PUT http://localhost:8000/musica/1
@app.route('/musica/<int:indice>', methods=['PUT'])
def atualizar_postagem(indice):
        dados_atualizados = request.get_json()
        musicas[indice].update(dados_atualizados)
        return jsonify(musicas[indice],200)
    
# Excluir uma postagem - DELETE http://localhost:8000/musica/1
@app.route('/musica/<int:indice>',methods=['DELETE'])
def excluir_musica(indice):
    try:
        musica_excluida = musicas[indice]
        del musicas[indice]
        return jsonify(f'Foi excluída a postagem: {musica_excluida}', 204)
    except:
        return jsonify('Não foi possível encontrar a música para exclusão', 404)

app.run(port=8000,host='localhost',debug=True)