import yaml


class Box:

    def __init__(self, yamlFile):
        self.box_name: str
        self.mq_publishers: dict = dict()
        self.mq_subscribers: dict = dict()
        self.grpc_clients: dict = dict()
        self.grpc_servers: dict = dict()
        data = yaml.safe_load(yamlFile)
        self.box_name = yamlFile.name[yamlFile.name.rfind("/")+1:len(yamlFile.name) - 4]
        if self.box_name != data["metadata"]["name"]:
            raise Exception(f"File name {self.box_name} does not correspond with box name {data['metadata']['name']}")
        self.parse_v2(data)

    def parse_v2(self, data):
        if "pins" in data["spec"] and data["spec"]["pins"] is not None:
            if "mq" in data["spec"]["pins"]:
                if data["spec"]["pins"]["mq"]["subscribers"] is not None:
                    for pin in data["spec"]["pins"]["mq"]["subscribers"]:
                        self.mq_subscribers[pin["name"]] = pin
                if data["spec"]["pins"]["mq"]["publishers"] is not None:
                    for pin in data["spec"]["pins"]["mq"]["publishers"]:
                        self.mq_publishers[pin["name"]] = pin
            if "grpc" in data["spec"]["pins"]:
                if "client" in data["spec"]["pins"]["grpc"] and data["spec"]["pins"]["grpc"]["client"] is not None:
                    for pin in data["spec"]["pins"]["grpc"]["client"]:
                        self.grpc_clients[pin["name"]] = pin
                if "server" in data["spec"]["pins"]["grpc"] and data["spec"]["pins"]["grpc"]["server"] is not None:
                    for pin in data["spec"]["pins"]["grpc"]["server"]:
                        self.grpc_servers[pin["name"]] = pin


