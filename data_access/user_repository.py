from controllers.controller_utils import encrypt_password, get_uuid
from data_access.fuseki_client import FusekiClient


class UserRepository:
    fuseki_client = None

    def __init__(self):
        self.fuseki_client = FusekiClient()

    @staticmethod
    def parse_json_result(result, index=0, add_password=False):
        local_result = result[index]

        if not local_result:
            return None

        ret_val = {
            "id": local_result["id"]["value"],
            "name": local_result["name"]["value"],
            "username": local_result["user"]["value"].split("#")[-1],
            "email": local_result["email"]["value"],
            "phone": local_result["phone"]["value"]
        }

        if add_password:
            ret_val["password"] = local_result["password"]["value"]

        return ret_val

    def parse_json_results(self, results):
        local_results = results["results"]["bindings"]
        res_list = []

        if not local_results:
            return None

        for index in range(len(local_results)):
            res_list.append(self.parse_json_result(local_results, index))

        return res_list

    def get_users(self):
        query = """
        PREFIX users: <http://www.semanticweb.org/ontologies/users#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT *
        WHERE {
            ?user rdf:type users:User .
            ?user users:id ?id .
            
            OPTIONAL {
                ?user users:name ?name .
                ?user users:email ?email .
                ?user users:phone ?phone .
                ?user users:password ?password .
            }
        }
        LIMIT 25
        """

        results = self.fuseki_client.query(query)

        return self.parse_json_results(results)

    def get_user_by_id(self, id, add_password=False):
        query = f"""
        PREFIX users: <http://www.semanticweb.org/ontologies/users#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT *
        WHERE {{
            ?user rdf:type users:User ;
                    users:id "{id}" .
            ?user users:id ?id .
            ?user users:name ?name .

            OPTIONAL {{
                ?user users:email ?email .
                ?user users:phone ?phone .
                ?user users:password ?password .
            }}
        }}
        LIMIT 1
        """

        result = self.fuseki_client.query(query)

        return self.parse_json_result(result["results"]["bindings"], add_password)

    def get_user_by_username(self, username, add_password=False):
        query = f"""
        PREFIX users: <http://www.semanticweb.org/ontologies/users#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT *
        WHERE {{
            users:{username} rdf:type ?user .
            users:{username} users:id ?id .
            users:{username} users:name ?name .

            OPTIONAL {{
                users:{username} users:email ?email .
                users:{username} users:phone ?phone .
                users:{username} users:password ?password .
            }}
        }}
        LIMIT 1
        """

        result = self.fuseki_client.query(query)

        return self.parse_json_result(result["results"]["bindings"], add_password)

    def insert_user(self, user):
        user["id"] = get_uuid()
        user["password"] = encrypt_password(user["password"])

        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX users: <http://www.semanticweb.org/ontologies/users#>
        INSERT DATA {{
            users:{user["username"]} rdf:type users:User ;
            users:email "{user["email"]}" ;
            users:name "{user["name"]}" ;
            users:phone "{user["phone"]}" ;
            users:password "{user["password"]}" ;
            users:id "{user["id"]}" .
        }}
        """

        self.fuseki_client.execute(query)

        return user

    def insert_visitor(self, visitor):
        visitor["id"] = get_uuid()

        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX users: <http://www.semanticweb.org/ontologies/users#>
        INSERT DATA {{
            users:{visitor["name"]} rdf:type users:User ;
            users:email "{visitor["name"]}" ;
            users:id "{visitor["id"]}" .
        }}
        """

        self.fuseki_client.execute(query)

        return visitor
