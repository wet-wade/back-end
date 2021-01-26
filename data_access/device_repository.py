from controllers.controller_utils import get_uuid
from data_access.fuseki_client import FusekiClient


class DeviceRepository:

    fuseki_client = None

    prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX groups: <http://www.semanticweb.org/ontologies/groups#>
    PREFIX users: <http://www.semanticweb.org/ontologies/users#>
    PREFIX devices: <http://www.semanticweb.org/ontologies/devices#>
    PREFIX permissions: <http://www.semanticweb.org/ontologies/permissions#>
    PREFIX user: <http://schemas.talis.com/2005/user/schema#>
    PREFIX saref: <https://w3id.org/saref#>
    PREFIX dc: <http://purl.org/dc/terms/>
    PREFIX ns1: <https://www.w3.org/2019/wot/hypermedia#>
    PREFIX ns2: <https://www.w3.org/2019/wot/json-schema#>
    prefix ns0:   <https://www.w3.org/2019/wot/td#> 
    """

    def __init__(self):
        self.fuseki_client = FusekiClient()

    @staticmethod
    def parse_device_definition_csv(results):
        res = {}

        for line in results.decode("utf-8").strip().split("\r\n")[1:]:
            group, title, action_target_link, prop_name, prop_target_link, = line.split(',')

            if not res:
                res = {
                    "type": group.split("#")[-1],
                    "title": title,
                    "properties": [],
                    "actions": []
                }

            if action_target_link != "":
                action_name = action_target_link.split("/")[-1]
                action_filtering = list(filter(lambda prop: prop["name"] == action_name, res["actions"]))
                if not action_filtering:
                    res["actions"].append({
                        "name": action_name,
                        "link": action_target_link
                    })

            if prop_name != "" or prop_target_link != "":
                prop_filtering = list(filter(lambda prop: prop["name"] == prop_name, res["properties"]))
                if not prop_filtering:
                    res["properties"].append({
                        "name": prop_name,
                        "link": prop_target_link
                    })

        return res

    def get_device_definition_by_type(self, device_type):
        query = f"""
            {self.prefixes}
            SELECT ?group ?title ?action_target_link ?prop_name ?prop_target_link
            WHERE {{
                ?group rdf:type saref:Device .
                ?group dc:title ?title .
                ?group ns0:hasActionAffordance ?action_target .
                ?action_target ns0:hasForm ?action .
                ?action ns1:hasTarget ?action_target_link .
                ?group ns0:hasPropertyAffordance ?prop .
                ?prop ns2:propertyName ?prop_name .
                ?prop ns0:hasForm ?prop_form .
                ?prop_form ns1:hasTarget ?prop_target_link .
            
                FILTER (?group = devices:{device_type})
            }}
        """

        results = self.fuseki_client.query(query, return_format="csv")

        return self.parse_device_definition_csv(results)

    def insert_device(self, device):
        device["id"] = get_uuid()

        query = f"""
        {self.prefixes}
        INSERT DATA {{
            devices:{device["id"]} rdf:type devices:{device["type"]};
                devices:name "{device["name"]}" ;
                devices:id "{device["id"]}" ;
                devices:nickname "{device["nickname"]}" ;  
        }}
        """

        self.fuseki_client.execute(query)

        return device["id"]
