from flask import Flask, jsonify, request
import sys
from uuid import uuid4
from time import time
import json
import hashlib


# example_block = {
#     'index': 1,
#     'timestamp': 0,
#     'votes': [
#         {
#             'from': 'a',
#             'to': 'b'
#         }
#     ],
#     'proof': 0,
#     'previous_hash': 'asdfasdfasdfasdf'
# }


class BlockChain:
    def __init__(self):
        self.chain = []
        self.votes = []
        self.new_block(0)

    def new_vote(self, f, t):
        self.votes.append({'from': f, 'to': t})
        return self.last_block()['index']+1

    def new_block(self, previous_hash):
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'votes': self.votes,
            'previous_hash': previous_hash
        }
        block = self.POW(block)
        self.votes = []
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def last_block(self):
        return self.chain[-1]

    def POW(self, block):
        block['proof'] = 0
        while not self.valid(block):
            block['proof'] += 1
        return block

    @staticmethod
    def valid(block):
        guess_hash = BlockChain.hash(block)
        return guess_hash[:4] == "0000"


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
chain = BlockChain()


@app.route('/mine', methods=['GET'])
def mine():
    last_block = chain.last_block()
    previous_hash = chain.hash(last_block)
    block = chain.new_block(previous_hash)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'votes': block['votes'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/votes/new', methods=['GET'])
def new_vote():
    values = request.args
    index = chain.new_vote(values['from'], values['to'])
    response = {'message': f'Vote will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': chain.chain,
        'length': len(chain.chain),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
