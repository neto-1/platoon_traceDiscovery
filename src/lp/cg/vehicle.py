from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client

class Vehicle(object):
    def __init__(self,db, vehicleID, start, end):
        self.__vehicleID = vehicleID
        self.__path = []
        self.__db = db
        self.__start = start
        self.__end = end
        self.__polygon = []

    # get the starting node
    def getStart(self):
        return self.__start

    # get the ending node
    def getEnd(self):
        return self.__end

    # add a path to the list of paths
    def addPath(self, path):
        self.__path.append(path)

    # store the (unique) polygon as a list of points
    def store_polygon(self,polygon):
        self.__polygon.append(polygon)

    # get the list of paths
    def getPaths(self):
        return self.__path

    # get the polygon as a list of points
    def get_polygon(self):
        return self.__polygon[0]

    # get the id of the vehicle
    def getID(self):
        return self.__vehicleID

    # delete ALL paths
    def deletePaths(self):
        del self.__path[:]
