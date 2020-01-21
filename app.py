from flask import Flask,request,jsonify
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import BadRequest
from dna_designer2 import codons

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='CDS Optimizer API',
    description='A simple codon optimizer',
)
db = 'example.db'

# Namespaces
ns_optimize = api.namespace('optimize', description='Optimize sequences')

# General Functions
def translate(dna_seq,organism_id):
    return codons.CodingSequence(codons.CodonDatabase(database=db),dna_seq,organism_id=organism_id).aa_seq()

# Routes
protein_optimize_model = ns_optimize.schema_model("optimize_protein",{"type": "object","properties": {"protein_seq":{"type": "string"},"organism_id":{"type":"string","minLength":1}}})
@ns_optimize.route('/protein')
class OptimizeProtein(Resource):
    @ns_optimize.expect(protein_optimize_model)
    def post(self):
        try:
            return jsonify({"optimized_seq": codons.CodonDatabase(database=db).optimize_sequence(request.get_json()['protein_seq'],request.get_json()['organism_id'])})
        except Exception as e:
            raise BadRequest(e)

dna_optimize_model = ns_optimize.schema_model("optimize_dna",{"type":"object","properties":{"dna_seq":{"type":"string"},"organism_id":{"type":"string","minLength":1}}})
@ns_optimize.route('/dna')
class OptimizeDna(Resource):
    @ns_optimize.expect(dna_optimize_model)
    def post(self):
        try:
            organism_id = request.get_json()['organism_id']
            return jsonify({"optimized_seq": codons.CodonDatabase(database=db).optimize_sequence(translate(request.get_json()['dna_seq'],organism_id),organism_id)})
        except Exception as e:
            raise BadRequest(e)


if __name__ == '__main__':
    app.run(debug=True)
