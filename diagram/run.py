from os import listdir
from os.path import isfile, join
from diagrams import Diagram, Cluster, Edge
from diagrams.k8s.compute import Pod
from diagrams.onprem.queue import RabbitMQ
from diagrams.onprem.compute import Server
from diagrams.onprem.client import Client
from Objects import Box

boxes_path = "../boxes/"
core_boxes_path = "../core/"
boxes_files = [f for f in listdir(boxes_path) if isfile(join(boxes_path, f)) and f.endswith(".yml")]
core_boxes_files = [f for f in listdir(core_boxes_path) if isfile(join(core_boxes_path, f)) and f.endswith(".yml")]
boxes: dict[str, Box] = {}
for file in boxes_files:
    boxes[file[:len(file) - 4]] = Box(open(boxes_path + file, "r"))
for file in core_boxes_files:
    boxes[file[:len(file) - 4]] = Box(open(core_boxes_path + file, "r"))

with Diagram("Schema", direction='TB', graph_attr={"margin": "3"}) as diag:
    pods = {}
    mstore = Pod("mstore")
    for box in boxes:
        pod = Cluster(box)
        pods[box] = pod
        with pod:
            pins = {}
            for pin in boxes[box].mq_subscribers:
                pins[pin] = RabbitMQ(pin)
            for pin in boxes[box].mq_publishers:
                pins[pin] = RabbitMQ(pin)
            for pin in boxes[box].grpc_servers:
                pins[pin] = Server(pin)
            for pin in boxes[box].grpc_clients:
                pins[pin] = Client(pin)
            pods[box+"pins"] = pins

    for box in boxes:
        pins = boxes[box].mq_subscribers
        for pin in pins:
            if "linkTo" in pins[pin]:
                links = pins[pin]["linkTo"]
                box_to = box
                pin_to = pins[pin]["name"]
                for link in links:
                    box_from = link["box"]
                    pin_from = link["pin"]
                    pods[box_from+"pins"][pin_from] >> Edge(color="red", style="bold", label="mq") >> pods[box_to+"pins"][pin_to]
    for box in boxes:
        pins = boxes[box].mq_publishers
        for pin in pins:
            if "store" in pins[pin]["attributes"]:
                pods[box+"pins"][pin] >> Edge(color="red", style="bold", label="mq") >> mstore

    for box in boxes:
        pins = boxes[box].grpc_clients
        for pin in pins:
            if "linkTo" in pins[pin]:
                links = pins[pin]["linkTo"]
                box_from = box
                pin_from = pins[pin]["name"]
                for link in links:
                    box_to = link["box"]
                    pin_to = link["pin"]
                    pods[box_from+"pins"][pin_from] >> Edge(color="blue", style="bold", label="grpc") >> pods[box_to+"pins"][pin_to]


diag
