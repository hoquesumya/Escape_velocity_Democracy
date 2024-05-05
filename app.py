from flask import Flask, request, render_template, redirect, url_for, Blueprint
from vote import Vote, VoteChain, VoteChainError

app = Flask(__name__)

vote_chain = VoteChain()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        vote = Vote(request.form['name'], request.form['vote'])
        try:
            vote_chain.add_vote(vote)
        except VoteChainError as e:
            return str(e)
    votes = vote_chain.get_votes()
    results = vote_chain.get_results()
    return render_template('index.html', votes=votes, results=results)

@app.route('/reset', methods=['POST'])
def reset():
    vote_chain.reset()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)