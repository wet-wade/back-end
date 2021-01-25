from data_access.fuseki_client import FusekiClient


class DeviceRepository:

    fuseki_client = None

    def __init__(self):
        self.fuseki_client = FusekiClient()

    def get_devices(self):
        query = """
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?subject ?predicate ?object
        WHERE {
          ?subject ?predicate ?object
        }
        LIMIT 25
            """

        results = self.fuseki_client.execute_statement(query)

        return results

    def insert_device(self):
        query = """
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    INSERT { <http://example/egbook> dc:title  "Other test" }
    WHERE {}
        """

        self.fuseki_client.execute_statement(query)

