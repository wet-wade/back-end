from controllers.controller_utils import get_uuid
from data_access.fuseki_client import FusekiClient


class PermissionRepository:
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

    def add_permission(self, group_id, permission):
        id = get_uuid()

        query = f"""
        {self.prefixes}
        INSERT DATA {{
            permissions:{id} rdf:Type permissions:Permission;
                permissions:id "{id}"
                permissions:deviceId "{permission["deviceId"]}" .
                permissions:memberId "{permission["memberId"]}" .
                permissions:manage "{permission["manage"]}" .
                permissions:read "{permission["read"]}" .
                permissions:write "{permission["write"]}" .
        }};

        INSERT DATA {{
            groups:{group_id} groups:hasPermission permissions:{id} .
        }}   
        """

        self.fuseki_client.execute(query)
