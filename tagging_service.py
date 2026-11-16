# Tagging & Categorization microservice
# CS361 Team 11
#
# Uses ZeroMQ with JSON messages on port 5557.
import json
import os
import zmq

PORT = 5557
DATA_FILE = "tags_data.json"


def load_data():
    # no file yet means nothing has been saved
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def error(message):
    return {"status": "error", "message": message}


def create_tag(data, app, tag):
    if tag in data[app]["tags"]:
        return error(f"Tag {tag} already exists")

    data[app]["tags"].append(tag)
    save_data(data)
    return {"status": "success", "message": f"Tag {tag} created"}


def assign_tag(data, app, tag, item_id):
    if tag not in data[app]["tags"]:
        return error(f"Tag {tag} does not exist")

    # item ids are saved as strings because JSON keys have to be strings
    key = str(item_id)
    if key not in data[app]["items"]:
        data[app]["items"][key] = []

    if tag in data[app]["items"][key]:
        return error(f"Item {item_id} already has tag {tag}")

    data[app]["items"][key].append(tag)
    save_data(data)
    return {
        "status": "success",
        "message": f"Tag {tag} assigned to item {item_id}",
        "item_id": item_id,
        "tags": data[app]["items"][key],
    }


def remove_tag(data, app, tag, item_id):
    key = str(item_id)
    if key not in data[app]["items"] or tag not in data[app]["items"][key]:
        return error(f"Item {item_id} does not have tag {tag}")

    data[app]["items"][key].remove(tag)
    save_data(data)
    return {
        "status": "success",
        "message": f"Tag {tag} removed from item {item_id}",
        "item_id": item_id,
        "tags": data[app]["items"][key],
    }


def handle_request(message):
    # turn the JSON string into a dictionary
    try:
        request = json.loads(message)
    except json.JSONDecodeError:
        return error("Request is not valid JSON")
    if type(request) != dict:
        return error("Request is not valid JSON")

    action = request.get("action")
    app = request.get("app")
    tag = request.get("tag")
    item_id = request.get("item_id")

    # check the parameters before doing anything
    if action not in ["create_tag", "assign_tag", "remove_tag"]:
        return error('"action" must be "create_tag", "assign_tag", or "remove_tag"')
    if type(app) != str or app == "":
        return error('"app" is required and must be a string')
    if type(tag) != str or tag == "":
        return error('"tag" is required and must be a string')
    if action != "create_tag":
        if type(item_id) not in [str, int] or item_id == "":
            return error(f'"item_id" is required for "{action}" and must be a string or number')

    # every app gets its own tags and items so programs don't see each other's data
    data = load_data()
    if app not in data:
        data[app] = {"tags": [], "items": {}}

    if action == "create_tag":
        return create_tag(data, app, tag)
    elif action == "assign_tag":
        return assign_tag(data, app, tag, item_id)
    else:
        return remove_tag(data, app, tag, item_id)


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    print(f"Tagging & Categorization microservice listening on port {PORT}")

    while True:
        message = socket.recv_string()
        print("Received request:", message)

        reply = json.dumps(handle_request(message))

        socket.send_string(reply)
        print("Sent reply:      ", reply)
        print()


if __name__ == "__main__":
    main()
