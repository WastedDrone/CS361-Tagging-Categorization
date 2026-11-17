
# Test program for the Taggin microservice
# CS361 Team 11
# Uses ZeroMQ with JSON messages on port 5557.
# How to run:
# Terminal 1: python3 tagging_service.py
# Terminal 2: python3 test_tagging.py

import json
import zmq

APP = "test_program"


def send_request(socket, request):
    print("Request sent:", json.dumps(request))
    socket.send_string(json.dumps(request))

    reply = json.loads(socket.recv_string())
    print("Reply received:", json.dumps(reply))
    print()


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")

    print("Connected to Tagging microservice\n")

    # Test 1: Create a tag
    print("Test 1: Create a tag")
    send_request(socket, {
        "action": "create_tag",
        "app": APP,
        "tag": "School"
    })

    # Test 2: Create another tag
    print("Test 2: Create another tag")
    send_request(socket, {
        "action": "create_tag",
        "app": APP,
        "tag": "Work"
    })

    # Test 3: Assign a tag to an item
    print("Test 3: Assign a tag")
    send_request(socket, {
        "action": "assign_tag",
        "app": APP,
        "tag": "School",
        "item_id": 5
    })

    # Test 4: Remove a tag from an item
    print("Test 4: Remove a tag")
    send_request(socket, {
        "action": "remove_tag",
        "app": APP,
        "tag": "School",
        "item_id": 5
    })

    # Test 5: Assign a tag that does not exist
    print("Test 5: Tag does not exist")
    send_request(socket, {
        "action": "assign_tag",
        "app": APP,
        "tag": "MissingTag",
        "item_id": 5
    })

    socket.close()
    context.term()

    print("All tests finished.")


if __name__ == "__main__":
    main()
