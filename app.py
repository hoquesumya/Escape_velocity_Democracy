import random
import socket
import json
from flask import Flask, render_template, request

ROUTING_TABLE = 'static/local_instances.txt'

# get peer ip and peer port from a random line of vms.txt
with open(ROUTING_TABLE) as f:
    # random.seed(1w00) # control reproducibility in testing
    peer_ip, peer_port = random.choice(f.readlines()).strip().split(',')
    peer_port = int(peer_port)
    print(f"Peer IP: {peer_ip}, Peer Port: {peer_port}")

# parser = argparse.ArgumentParser(description='Flask app to send data to a specified peer.')
# parser.add_argument('peer_ip', type=str, help='IP address of the peer')
# parser.add_argument('peer_port', type=int, help='Port number of the peer')
# args = parser.parse_args()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    This function renders the index.html page and handles the form data. 
    '''
    with open('static/candidates.txt') as f:
        random.seed(100) # control reproducibility in testing
        candidates = random.sample(f.readlines(), 10, )

    if request.method == 'POST':
        # Retrieve data from the form
        voterID = request.form['voter_id']
        passphrase = request.form['passphrase']
        public_key = request.form['key']
        vote = request.form['vote']
        vote = vote.replace('\r', '').replace('\n', '')
        
        #data = f"{passphrase},{public_key},{vote}"
        data= {
            "msg_type":"transaction",
            "voterID":voterID,
            "passphrase":passphrase,
            "key":public_key,
            "vote":vote
        }

        # Send data to the peer using the IP and port from command-line arguments
        response = send_data_to_peer(data, peer_ip, peer_port)

        return render_template('index.html', response=response, candidates=candidates)
    return render_template('index.html', response=None, candidates=candidates)

# @app.route('/blockchain', methods=['GET'])
# def show_blockchain():
#     # request blockchain data from the peer and display it on the page
#     data = {
#         "msg_type":"request_blockchain"
#     }
#     response = send_data_to_peer(data, peer_ip, peer_port)
#     return render_template('blockchain.html', response=response)

@app.route('/results', methods=['GET'])
def show_results():
    # request results data from the peer and display it on the page
    data = {
        "msg_type":"get_results"
    }
    response = send_data_to_peer(data, peer_ip, peer_port)
    print(response)
    # response: Received from server: {"Oliver Tambo": 2, "Giuseppe Garibaldi": 1, "Daniel Ortega": 1, "Karl Marx": 3}done
    # remove received from server: and done
    response = response.replace("Received from server: ", "").replace("done", "")
    print(response)    
    if response:
        results = json.loads(response)
    else:
        results = None

    # order by number of votes
    if results:
        results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
    return render_template('results.html', results=results)

def send_data_to_peer(data, ip, port):
    """this function will redirect client data to the peer"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    
            data1 = json.dumps(data)
            temp_data = ""
            temp_data+=data1
            temp_data+="done"
            
            sock.connect((ip, port))
            sock.sendall(temp_data.encode('utf-8'))
            # Optionally receive a response
            response = sock.recv(1024)
            return f"Received from server: {response.decode('utf-8')}"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
   app.run(debug=True)
