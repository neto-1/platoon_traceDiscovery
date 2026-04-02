from py2neo import Graph, Node, Relationship
from collections import defaultdict, deque
import random
from random import randint


road_point_label = "RoadPoint"
road_segment_name = "ROAD_SEGMENT"
vehicle_label = "Vehicle"
vehicle_start_name = "START_AT"
vehicle_end_name = "END_AT"

def gridGenerator(sizeX, sizeY, truckAmount, minWeight, maxWeight):
        graph = Graph("http://neo4j:12345678@localhost:7474/db/data/")
        graph.delete_all()

        locations = [[]]
        for i in range(0,sizeX):
                row = []
                for j in range(0,sizeY):
                        row.append(0)
                locations.insert(i, row)

        relNeighbour = []

        counter = 0

        for x in range(0, sizeX):
                for y in range(0, sizeY):
                        newNode = Node(road_point_label, name=str(counter), lon=x, lat=y)
                        locations[x][y]=newNode
                        if(x>0):
                                distance_m = randint(minWeight, maxWeight)
                                relLeft01 = Relationship(locations[x-1][y], road_segment_name, locations[x][y], distance_meter=distance_m, distance=distance_m/1000)
                                relNeighbour.append(relLeft01)

                                relLeft02 = Relationship(locations[x][y], road_segment_name, locations[x-1][y], distance_meter=distance_m, distance=distance_m/1000)
                                relNeighbour.append(relLeft02)

                        if(y>0):
                                distance_m = randint(minWeight, maxWeight)
                                relTop01 = Relationship(locations[x][y-1], road_segment_name, locations[x][y], distance_meter=distance_m, distance=distance_m/1000)
                                relNeighbour.append(relTop01)

                                relTop02 = Relationship(locations[x][y], road_segment_name, locations[x][y-1], distance_meter=distance_m, distance=distance_m/1000)
                                relNeighbour.append(relTop02)
                        counter = counter+1;


        trucks = []
        relStart = []
        relEnd = []
        for t in range(0, truckAmount):
                truck = Node(vehicle_label)
                trucks.append(truck)
                startX = random.randint(0, sizeX-1)
                startY = random.randint(0, sizeY-1)
                start = Relationship(truck, vehicle_start_name, locations[startX][startY])
                relStart.append(start)

                endX = random.randint(0, sizeX-1)
                endY = random.randint(0, sizeY-1)
                end = Relationship(truck, vehicle_end_name, locations[endX][endY])
                relEnd.append(end)


        tx = graph.begin()

        print("creating transaction")
        print("creating locations")
        for y in range(0, sizeY):
                for x in range(0, sizeX):
                        tx.create(locations[x][y])

        print("creating neighbour-relations")
        for i in range(0, len(relNeighbour)):
                tx.create(relNeighbour[i])




        print("creating trucks")
        # for i in range(0, len(trucks)):
        #         tx.create(trucks[i])
        # for i in range(0, len(relStart)):
        #         tx.create(relStart[i])
        #
        # for i in range(0, len(relEnd)):
        #         tx.create(relEnd[i])

        print("committing transaction")
        tx.commit()




gridGenerator(5,5,100, 1, 2000)
#gridGenerator(10,20,50)
