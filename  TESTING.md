# TESTING.md

This file describes how we test the Escape Velocity for Democracy blockchain project.

## Testing

We used a variety of techniques to test the project, including [pytest](https://docs.pytest.org/en/latest/) and manual testing. Below are a few our our test cases. Further tests can be seen at the bottom of most .py files.
- Verify that blockchain length is consistent with what we expect.
- Verify that our strategy for handling forks works as expected. (unimplemented due to 2-person team)
- Verify that the blockchain rejects invalid transactions.
- Verify our proof of work algorithm works as expected.


## Running blockchain network locally
It may be useful to run the blockchain network locally for testing purposes. To do so, enter these prompts into separate terminal windows:

1. Run the tracker server:
```bash
python3 tracker.py 60000
```

2. Run the peer servers:
```bash
python3 peer.py 49998 127.0.0.1 60000
python3 peer.py 49999 127.0.0.1 60000
python3 peer.py 50000 127.0.0.1 60000
(optionally) python3 peer.py 50001 127.0.0.1 60000
```

3. Run the client:
create a virtual env and activate the venv
```bash
python -m venv myenv
source myenv/bin/activate
pip3 install -r requirements.txt
```
```bash
python3 app.py
```
The client will randomly select a peer to connect to from vms.txt. If you want to connect to a specific peer, you can uncomment the block in app.py that specifies the peer to connect to.




