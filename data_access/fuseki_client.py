import json

from SPARQLWrapper import SPARQLWrapper, CSV, JSON, TURTLE
from rdflib import Graph, plugin
from rdflib.serializer import Serializer


class FusekiClient:

    conn_string = "https://wet-wade-fuseki.herokuapp.com/ds"

    regex = r"[ +\/()#*²]"
    subst = "_"

    def get_conn_string(self, is_query=True):
        return f"{self.conn_string}/query" if is_query else f"{self.conn_string}/update"

    def query(self, query, return_format=JSON):
        fuseki_client = SPARQLWrapper(self.get_conn_string())
        fuseki_client.method = "POST"
        fuseki_client.setQuery(query)
        fuseki_client.setReturnFormat(return_format)

        results = fuseki_client.queryAndConvert()

        return results

    def execute(self, command, return_format=JSON):
        fuseki_client = SPARQLWrapper(self.get_conn_string(False))
        fuseki_client.method = "POST"
        fuseki_client.setQuery(command)
        fuseki_client.setReturnFormat(return_format)

        results = fuseki_client.query()

        return results

