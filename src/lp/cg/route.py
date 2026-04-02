from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client


class Route(object):

    def __init__(self, routeID, distance, path, nodesPath):
        self.__routeID = routeID
        self.__distance = distance
        self.__path = path
        self.__nodesPath = nodesPath

    # get the ID of the route
    def getRouteID(self):
        return self.__routeID

    # get the list of distances
    def getDistance(self):
        return self.__distance

    #get the list of IDs of the edges in the path
    def getPath(self):
        return self.__path

    # get the list of the edges displayed as two nodes
    def getNodesPath(self):
        return self.__nodesPath