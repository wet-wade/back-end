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

        for line in results.decode("utf-8").strip().split("\r\n")[1:]:
            group, name, id, owner, owner_id, owner_name, \
            member, member_id, member_name, \
            device, device_id, device_name, device_nickname, device_type, \
            permissions, permission_device_id, permission_member_id, \
            permission_can_manage, permission_can_read, permission_can_write = line.split(',')

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
                if not device_filtering:
                    res["devices"].append({
                        "id": device_id,
                        "name": device_name,
                        "nickname": device_nickname,
                        "type": device_type.split("#")[-1]
                    })

            if permission_device_id != "" or permission_member_id != "" or permission_can_manage != "" \
                    or permission_can_read != "" or permission_can_write:
                res["permissions"].append({
                    "deviceId": permission_device_id,
                    "memberId": permission_member_id,
                    "canManage": permission_can_manage,
                    "canRead": permission_can_read,
                    "canWrite": permission_can_write,
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
                ?group groups:permissions ?permissions .
                ?permissions permissions:deviceId ?permission_device_id .
                ?permissions permissions:memberId ?permission_member_id .
                ?permissions permissions:canManage ?permission_can_manage .
                ?permissions permissions:canRead ?permission_can_read .
                ?permissions permissions:canWrite ?permission_can_write .
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

        # TODO PETRU!!
        # TODO trebuie construita legatura cu grupul la care le inseram

