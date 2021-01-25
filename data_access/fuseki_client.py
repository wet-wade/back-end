from SPARQLWrapper import SPARQLWrapper, CSV, JSON


class FusekiClient:

    conn_string = "https://wet-wade-fuseki.herokuapp.com/ds"

    regex = r"[ +\/()#*²]"
    subst = "_"
    fuseki_client = None

    def __init__(self):
        self.fuseki_client = SPARQLWrapper(self.conn_string)
        self.fuseki_client.method = "POST"

    def execute_statement(self, query, return_format=JSON):
        self.fuseki_client.setQuery(query)
        self.fuseki_client.setReturnFormat(return_format)
        results = self.fuseki_client.query().convert()

        return results


