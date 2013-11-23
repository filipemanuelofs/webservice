# coding: utf-8
#!flask/bin/python

# Webservice feito em Flask para disciplina de Sistemas Distribuídos.
# Professor: Eduardo Moraes
# Aluno: Filipe Manuel

# HTTP   |  URI                                                      |  Retorno
# GET    |  http://localhost/todo/api/v1.0/atividades                |  Lista de tarefas
# GET    |  http://localhost/todo/api/v1.0/atividades/[atividade_id] |  Retorna uma tarefa específica
# POST   |  http://localhost/todo/api/v1.0/atividades                |  Cria uma nova tarefa
# PUT    |  http://localhost/todo/api/v1.0/atividades/[atividade_id] |  Atualiza uma tarefa específica
# DELETE |  http://localhost/todo/api/v1.0/atividades/[atividade_id] |  Deleta uma tarefa

# exemplos: 
# curl -u user:passwd -i http://localhost:5000/todo/api/v1.0/atividades/1
# curl -i -H "Content-Type: application/json" -X POST -d '{"titulo":"Limpar jardim"}' http://localhost:5000/todo/api/v1.0/atividades
# curl -i -H "Content-Type: application/json" -X PUT -d '{"descricao":"Limpar o jardim e as cercas"}' http://localhost:5000/todo/api/v1.0/atividades
# curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/todo/api/v1.0/atividades/1


from flask.ext.httpauth import HTTPBasicAuth
from flask import (Flask, jsonify, 
    abort, make_response,
    request, url_for)

app = Flask(__name__)
auth = HTTPBasicAuth()

# Lista com as tarefas iniciais
atividades = [
    {
    'id': 1,
    'titulo': u'Comprar frutas',
    'descricao': 'Uva, Banana, Melancia',
    'status': False
    },

    {
    'id': 2,
    'titulo': u'Fazer jantar',
    'descricao': 'Risoto de frango',
    'status': False
    }
]

@app.route('/todo/api/v1.0/atividades/<int:atividade_id>', methods=['GET'])
def get_atividade(atividade_id):
    """
    Função que retorna uma atividade específica em formato json
    porém, se o tamanho da atividade for zero (não existir) retorna 404
    """
    atividade = filter(lambda atv: atv['id'] == atividade_id, atividades)
    if len(atividade) == 0:
        abort(404)
    return jsonify({'atividade': atividade[0]})


@app.route('/todo/api/v1.0/atividades', methods = ['POST'])
def criar_atividade():
    """
    Função que cria uma atividade (status padrão = False). 
    Se não houver título ou nenhum request, retorna 404.
    """
    if not request.json or not 'titulo' in request.json:
        abort(400)
    atividade = {
        'id': atividades[-1]['id'] + 1,
        'titulo': request.json['titulo'],
        'descricao': request.json.get('descricao', ""),
        'status': False
    }
    atividades.append(atividade)
    return jsonify({'atividade': atividade}), 201

@app.route('/todo/api/v1.0/atividades/<int:atividade_id>', methods = ['PUT'])
def update_atividade(atividade_id):
    """
    Função que atualiza uma atividade específica.
    'Ifs' são apenas para garantir que todos os campos
    foram preenchidos e não estão vazios, retorna uma 
    atividade atualizada à lista inicial.
    """
    atividade = filter(lambda atv: atv['id'] == atividade_id, atividades)
    if len(atividade) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'titulo' in request.json and type(request.json['titulo']) != unicode:
        abort(400)
    if 'descricao' in request.json and type(request.json['descricao']) is not unicode:
        abort(400)
    if 'status' in request.json and type(request.json['status']) is not bool:
        abort(400)
    atividade[0]['titulo'] = request.json.get('titulo', atividade[0]['titulo'])
    atividade[0]['descricao'] = request.json.get('descricao', atividade[0]['descricao'])
    atividade[0]['status'] = request.json.get('status', atividade[0]['status'])
    return jsonify({'atividade': atividade[0]})


@app.route('/todo/api/v1.0/atividades/<int:atividade_id>', methods = ['DELETE'])
def delete_atividade(atividade_id):
    """
    Função que deleta uma atividade específica de acordo
    com o seu id, removendo da lista inicial de atividades
    """
    atividade = filter(lambda atv: atv['id'] == atividade_id, atividades)
    if len(atividade) == 0:
        abort(404)
    atividades.remove(atividade[0])
    return jsonify({'result': True})


@app.errorhandler(404)
def not_found(error):
    """
    Função que retorna 404 caso não exista o id requerido.
    """
    return make_response(jsonify({'error': u'Página não encontrada!'}), 404)


@app.route('/todo/api/v1.0/atividades', methods=['GET'])
@auth.login_required
def get_atividades():
    """
    Função que retorna toda lista de atividades se o usuário estiver autenticado.
    """
    return jsonify({'atividades': map(url_publica, atividades)})


def url_publica(atividade):
    """
    Função que oculta o campo id e em seu lugar retorna a URI da atividade.
    """
    nova_atividade = {}
    for campo in atividade:
        if campo == 'id':
            nova_atividade['uri'] = url_for('get_atividade', atividade_id=atividade['id'], _external=True)
        else:
            nova_atividade[campo] = atividade[campo]
    return nova_atividade


@auth.get_password
def get_password(username):
    """
    Função de segurança básica. Só é mostrada a lista de atividades
    se o usuário passar para o sistema a autenticação, username:password.
    """
    if username == 'filipe':
        return '123456'
    return None

@auth.error_handler
def nao_autorizado():
    """
    Função para negar o acesso caso usuário não seja identificado.
    """
    return make_response(jsonify({'error': 'Acesso negado'}), 403)


if __name__ == '__main__':
    app.run(debug=True)
