from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
from person import Person

# GLOBAL CONSTANTS
HOST = 'localhost'
PORT = 5500
ADDR = (HOST, PORT)
MAX_CONNECTIONS = 10
BUFSIZ = 512

# GLOBAL VARIABLES
persons = []
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)   # Set up the server


def broadcast(msg, name):
    """
    Send new messages to a client
    :param msg: bytes["utf8"]
    :param name: str
    :return: None
    """

    for person in persons:
        client = person.client
        try:
            client.send(bytes(name, "utf8") + msg)
        except Exception as e:
            print("[EXCEPTION]", e)


def client_communication(person):
    """
    Thread to handle all the messages form client
    :param person: Person
    :return: None
    """

    client = person.client

    # first message received is always the person's name
    name = client.recv(BUFSIZ).decode("utf8")
    person.set_name(name)
    msg = bytes(f"{name} has joined the chat!", "utf8")
    broadcast(msg, "")  # broadcast a welcome message

    while True:  # wait for any messages from the person
        try:
            msg = client.recv(BUFSIZ)

            if msg == bytes("{quit}", "utf8"):  # if the message is quit, disconnect client
                client.close()
                persons.remove(person)
                broadcast(bytes(f"{name} has left the chat...", "utf8"), "")
                print(f"[DISCONNECTED] {name} disconnected")
                break
            else:    # otherwise send message to all other clients
                broadcast(msg, name + ": ")
                print(f"{name}: ", msg.decode("utf8"))

        except Exception as e:
            print("[EXCEPTION]", e)
            break


def wait_for_connection():
    """
    Wait for a connection from new clients, then start the new thread once it's connected.
    :return: None
    """

    while True:
        try:
            client, addr = SERVER.accept()    # wait for any new connections
            person = Person(addr, client)    # create a new person for connection
            persons.append(person)

            print(f"[CONNECTION] {addr} connected to the server at "
                  f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")    # show the time the client has connected
            Thread(target=client_communication, args=(person,)).start()
        except Exception as e:
            print("[EXCEPTION]", e)
            break

    print("THE SERVER CRASHED")


if __name__ == "__main__":
    SERVER.listen(MAX_CONNECTIONS)    # open server to listen for connections
    print("[STARTED] Waiting for connections...")
    ACCEPT_THREAD = Thread(target=wait_for_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
