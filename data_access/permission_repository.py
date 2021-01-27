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

    def set_permission(self, group_id, user_id, permission):
        if not self.check_manage_permission(group_id, user_id):
            return

        if not self.check_exists_permission(group_id, user_id, permission["deviceId"]):
            self.add_permission(group_id, permission)
        else:
            self.update_permission(group_id, permission)

    def check_manage_permission(self, group_id, user_id):
        query = f"""
        {self.prefixes}
        SELECT ?permission_can_manage
        WHERE {{
            ?group rdf:type groups:Group ;
                groups:id "{group_id}" .
            ?group groups:name ?name .
            ?group groups:id ?id .
    
    		OPTIONAL {{
                ?group groups:hasPermission ?permissions .
        		?permissions permissions:memberId ?permissions_member_id .
                ?permissions permissions:deviceId ?permission_device_id .
                ?permissions permissions:manage ?permission_can_manage .
                ?permissions permissions:read ?permission_can_read .
                ?permissions permissions:write ?permission_can_write .
      		}}
    
    		FILTER (?permissions_member_id = "{user_id}")
        }}
        """

        result = self.fuseki_client.query(query, "csv").decode("utf-8").strip().split("\r\n")[1:]

        if not result:
            return False
        elif result == ["1"]:
            return True

        return False

    def check_exists_permission(self, group_id, user_id, device_id):
        query = f"""
        {self.prefixes}
        SELECT ?permissions
        WHERE {{
            ?group rdf:type groups:Group ;
                groups:id "{group_id}" .
            ?group groups:name ?name .
            ?group groups:id ?id .

    		OPTIONAL {{
                ?group groups:hasPermission ?permissions .
        		?permissions permissions:memberId ?permissions_member_id .
                ?permissions permissions:deviceId ?permissions_device_id .
                ?permissions permissions:manage ?permission_can_manage .
                ?permissions permissions:read ?permission_can_read .
                ?permissions permissions:write ?permission_can_write .
      		}}

    		FILTER (?permissions_member_id = "{user_id}"
                &&  ?permissions_device_id = "{device_id}")
        }}
        """

        result = self.fuseki_client.query(query, "csv").decode("utf-8").strip().split("\r\n")[1:]

        if not result:
            return False
        elif result:
            return True

        return False

    def add_permission(self, group_id, permission):
        id = get_uuid()

        query = f"""
        {self.prefixes}
        INSERT DATA {{
            permissions:{id} rdf:Type permissions:Permission;
                permissions:id "{id}" ;
                permissions:deviceId "{permission["deviceId"]}" ;
                permissions:memberId "{permission["memberId"]}" ;
                permissions:manage "{int(permission["manage"])}" ;
                permissions:read "{int(permission["read"])}" ;
                permissions:write "{int(permission["write"])}" ;
        }};

        INSERT DATA {{
            groups:{group_id} groups:hasPermission permissions:{id} .
        }}   
        """

        self.fuseki_client.execute(query)

    def update_permission(self, group_id, permission):
        query = f"""
        {self.prefixes}
        DELETE {{
            ?permissions permissions:memberId ?permissions_member_id .
            ?permissions permissions:deviceId ?permissions_device_id .
            ?permissions permissions:manage ?permission_can_manage .
            ?permissions permissions:read ?permission_can_read .
            ?permissions permissions:write ?permission_can_write .
        }}
        INSERT {{
            ?permissions permissions:memberId "{permission["memberId"]}" .
            ?permissions permissions:deviceId "{permission["deviceId"]}" .
            ?permissions permissions:manage "{int(permission["manage"])}" .
            ?permissions permissions:read "{int(permission["read"])}" .
            ?permissions permissions:write "{int(permission["write"])}" .
        }}   
        WHERE {{
            ?group rdf:type groups:Group ;
                groups:id "{group_id}" .

            ?group groups:hasPermission ?permissions .
            ?permissions permissions:memberId ?permissions_member_id .
            ?permissions permissions:deviceId ?permissions_device_id .
            ?permissions permissions:manage ?permission_can_manage .
            ?permissions permissions:read ?permission_can_read .
            ?permissions permissions:write ?permission_can_write .

            FILTER (?permissions_member_id = "{permission["memberId"]}"
                &&  ?permissions_device_id = "{permission["deviceId"]}")
        }}
        """

        self.fuseki_client.execute(query)
