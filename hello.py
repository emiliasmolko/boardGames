from cloudant import Cloudant
from cloudant.result import Result, ResultByKey
from cloudant.error import CloudantException
from flask import Flask, render_template, request, jsonify
import atexit
import cf_deployment_tracker
import os
import json

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

db_name = 'gamesdb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES',vcap)
    if 'cloudantNoSQLDB' in vcap:
        print('Found VCAP_SERVICES',vcap['cloudantNoSQLDB'])
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def home():
    return render_template('index.html')

# /* Endpoint to greet and add a new visitor to database.
# * Send a POST request to localhost:8000/api/visitors with body
# * {
# *     "name": "Bob"
# * }
# */
@app.route('/api/games', methods=['GET'])
def get_visitor():
    if client:
        #return jsonify(list(map(lambda doc: doc['title'], db)))
        query = Query(database, selector={'_id': {'$gt': 0}})
        dataFromDb = [];
        for doc in query()['docs']:
            dataFromDb.append(doc);
        return jsonify(dataFromDb);
        #return jsonify(result_collection = Result(db.all_docs))
    else:
        print('No database')
        return jsonify([])

# /**
#  * Endpoint to get a JSON array of all the visitors in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */
@app.route('/api/games', methods=['POST'])
def put_visitor():
    game = request.json['name']
    if client:
        data = {'name':game}
        db.create_document(data)
        return 'Hello %s! I added your game to the database.' % user
    else:
        print('No database')
        return 'Nie moge teraz zapisac %s! Przepraszam :-(' % game

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
