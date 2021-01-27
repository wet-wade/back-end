import random

from controllers.controller_utils import encrypt_password, get_uuid, known_devices
from data_access.device_repository import DeviceRepository
from data_access.fuseki_client import FusekiClient


class GroupRepository:
    fuseki_client = None

    prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX groups: <http://www.semanticweb.org/ontologies/groups#>
    PREFIX users: <http://www.semanticweb.org/ontologies/users#>
    PREFIX devices: <http://www.semanticweb.org/ontologies/devices#>
    PREFIX permissions: <http://www.semanticweb.org/ontologies/permissions#>
    """

    def __init__(self):
        self.fuseki_client = FusekiClient()

    @staticmethod
    def parse_detailed_csv_results(results):
        res = {}
        device_repository = DeviceRepository()

        for line in results.decode("utf-8").strip().split("\r\n")[1:]:
            group, name, id, owner, owner_id, owner_name, \
            member, member_id, member_name, \
            device, device_id, device_name, device_nickname, device_type, \
            permissions, permission_device_id, permission_member_id, \
            permission_manage, permission_read, permission_write = line.split(',')

            if not res:
                res = {
                    "id": id,
                    "name": name,
                    "ownerId": owner_id,
                    "members": [],
                    "devices": [],
                    "permissions": []
                }

            if member_id != "" or member_name != "":
                member_filtering = list(filter(lambda prop: prop["id"] == member_id, res["members"]))
                if not member_filtering:
                    res["members"].append({
                        "id": member_id,
                        "name": member_name
                    })

            if device != "" or device_id != "" or device_name != "" or device_nickname != "" or device_type != "":
                device_filtering = list(filter(lambda prop: prop["id"] == device_id, res["devices"]))
                device_type = device_type.split("#")[-1]
                if not device_filtering:
                    device_definition = device_repository.get_device_definition_by_type(device_type)

                    res["devices"].append({
                        "id": device_id,
                        "name": device_name,
                        "nickname": device_nickname,
                        "type": device_type,
                        "title": device_definition["title"],
                        "properties": device_definition["properties"],
                        "actions": device_definition["actions"]
                    })

            if permission_device_id != "" or permission_member_id != "" or permission_manage != "" \
                    or permission_read != "" or permission_write != "":
                permission_id = permissions.split("#")[-1]
                permission_filtering = list(filter(lambda prop: prop["id"] == permission_id, res["permissions"]))

                if not permission_filtering:
                    res["permissions"].append({
                        "id": permission_id,
                        "deviceId": permission_device_id,
                        "memberId": permission_member_id,
                        "manage": permission_manage,
                        "read": permission_read,
                        "write": permission_write,
                    })

        return res

    @staticmethod
    def parse_summary_csv_results(results):
        res_list = []

        for line in results.decode("utf-8").strip().split("\r\n")[1:]:
            name, id, owner_id = line.split(',')

            res = {
                "id": id,
                "name": name,
                "creatorId": owner_id
            }

            res_list.append(res)

        return res_list

    def get_groups_summary_by_user(self, user_id):
        query = f"""
        {self.prefixes}
        SELECT ?name ?id ?owner_id
        WHERE {{
            ?group groups:name ?name .
            ?group groups:id ?id .
    		?group groups:isOwnedBy ?owner .
    		?owner users:id ?owner_id .
            ?group groups:hasMember ?member .
            ?member users:id "{user_id}" .
        }}
            """

        results = self.fuseki_client.query(query, "csv")

        return self.parse_summary_csv_results(results)

    def get_group_summary_by_group(self, group_id):
        query = f"""
        {self.prefixes}
        SELECT ?name ?id ?owner_id
        WHERE {{
            ?group groups:name ?name .
            ?group groups:id "{group_id}" .
    		?group groups:isOwnedBy ?owner .
    		?owner users:id ?owner_id .
            ?group groups:hasMember ?member .
        }}
            """

        results = self.fuseki_client.query(query, "csv")

        return self.parse_summary_csv_results(results)[0]

    def get_group(self, group_id):

        query = f"""
        {self.prefixes}
        SELECT *
        WHERE {{
            ?group rdf:type groups:Group ;
                groups:id "{group_id}" .
            ?group groups:name ?name .
            ?group groups:id ?id .
            ?group groups:isOwnedBy ?owner .
            ?owner users:id ?owner_id .
            ?owner users:name ?owner_name .
            ?group groups:hasMember ?member .
            ?member users:id ?member_id .
            ?member users:name ?member_name .
            
            OPTIONAL {{
        		?group groups:consistsOf ?device .
                ?device devices:id ?device_id .
                ?device devices:name ?device_name .
        		?device devices:nickname ?device_nickname .
                ?device a ?device_type .
      		}}
    
    		OPTIONAL {{
                ?group groups:hasPermission ?permissions .
                ?permissions permissions:deviceId ?permission_device_id .
                ?permissions permissions:memberId ?permission_member_id .
                ?permissions permissions:manage ?permission_can_manage .
                ?permissions permissions:read ?permission_can_read .
                ?permissions permissions:write ?permission_can_write .
      		}}
        }}
        """

        result = self.fuseki_client.query(query, "csv")

        return self.parse_detailed_csv_results(result)

    def create_group(self, group):
        group["id"] = get_uuid()

        query = f"""
        {self.prefixes}
        INSERT DATA {{
            groups:{group["id"]} rdf:type groups:Group ;
                groups:name "{group["name"]}" ;
                groups:id "{group["id"]}" ;
                groups:isOwnedBy users:{group["owner"]["username"]} ;
                groups:hasMember users:{group["owner"]["username"]} .
        }}
        """

        self.fuseki_client.execute(query)

        return group["id"]

    @staticmethod
    def parse_group_devices_csv(results):
        current_devices = []

        for line in results.decode("utf-8").strip().split("\r\n")[1:]:
            current_devices.append(line.split("#")[-1])

        return current_devices

    @staticmethod
    def compute_sparql_devices(prefix, device_ids):
        result = ""
        for device_id in device_ids:
            if len(result) == 0:
                result = f"{prefix}:{device_id}"
            else:
                result = f"{result} , {prefix}:{device_id}"

        return result

    def get_group_devices(self, group_id):
        query = f"""
                PREFIX groups: <http://www.semanticweb.org/ontologies/groups#> 
                SELECT ?object WHERE
                {{
                    groups:{group_id} groups:consistsOf ?object
                }}
            """
        results = self.fuseki_client.query(query, "csv")

        return self.parse_group_devices_csv(results)

    def insert_new_device(self, group_id, device_id):
        current_devices = self.get_group_devices(group_id)
        current_devices.append(device_id)

        insert = f"""
                PREFIX devices: <http://www.semanticweb.org/ontologies/devices#>
                PREFIX groups: <http://www.semanticweb.org/ontologies/groups#>
                DELETE WHERE {{
                    groups:{group_id} groups:consistsOf ?object
                }};  
                INSERT DATA {{
                    groups:{group_id} groups:consistsOf {self.compute_sparql_devices('devices', current_devices)}
                }}
            """

        self.fuseki_client.execute(insert)

    def discover(self, group_id):

        device_repo = DeviceRepository()
        devices = []

        for k, devices in known_devices.items():
            device = {
                "id": get_uuid(),
                "nickname": "",
                "name": random.choice(known_devices[k]),
                "type": k
            }

            device_repo.insert_device(device)
            devices.append(device)

        return devices
