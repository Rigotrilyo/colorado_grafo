import heapq

class nodeInfo:
    def __init__(self, sat, deg, vertex):
        self.sat = sat
        self.deg = deg
        self.vertex = vertex

class maxSat:
    def __call__(self, node):
        return (-node.sat, -node.deg, node.vertex)

class Graph:
    def __init__(self, numNodes):
        self.n = numNodes
        self.adj = [set() for _ in range(numNodes+1)]

    def addEdge(self, u, v):
        if not(1 <= u <= self.n and 1<= v <= self.n):
            raise ValueError(f"Los nodos deben estar entre 1 y {self.n}")
        if u==v:
            raise ValueError("Un nodo no puede ser vecino de sí mismo")
        
        self.adj[u].add(v)
        self.adj[v].add(u)

    def DSatur(self):
        colores = [0] * (self.n + 1)

        while  any(colores[u] == 0 for u in range(1, self.n +1)):
            def prioridad(u):
                colores_vecinos = {
                    colores[v] for v in self.adj[u] if colores[v] != 0
                }
                return (len(colores_vecinos), len(self.adj[u]), -u)

            u = max(
                (v for v in range(1, self.n +1) if colores[v] == 0),
                key=prioridad
            )

            prohibidos = {colores[v] for v in self.adj[u]}
            color = 1
            while color in prohibidos:
                color += 1

            colores[u] = color
        for u in range(1, self.n +1):
            print(f"Nodo {u} ---> Color {colores[u]}")

        print(f"Colores utilizados: {max(colores)}")
        return colores

if __name__ == '__main__':
    G1 = Graph(19)
    G1.addEdge(1,16)
    G1.addEdge(1,4)
    G1.addEdge(1,2)
    G1.addEdge(2,3)
    G1.addEdge(2,4)
    G1.addEdge(2,5)
    G1.addEdge(2,6)
    G1.addEdge(2,7)
    G1.addEdge(3,7)
    G1.addEdge(3,11)
    G1.addEdge(3,19)
    G1.addEdge(4,8)
    G1.addEdge(4,9)
    G1.addEdge(4,5)
    G1.addEdge(5,6)
    G1.addEdge(5,9)
    G1.addEdge(5,10)
    G1.addEdge(6,7)
    G1.addEdge(6,11)
    G1.addEdge(6,14)
    G1.addEdge(7,11)
    G1.addEdge(8,9)
    G1.addEdge(8,12)
    G1.addEdge(9,10)
    G1.addEdge(9,12)
    G1.addEdge(9,13)
    G1.addEdge(9,15)
    G1.addEdge(10,13)
    G1.addEdge(10,14)
    G1.addEdge(11,14)
    G1.addEdge(11,19)
    G1.addEdge(12,15)
    G1.addEdge(12,16)
    G1.addEdge(13,14)
    G1.addEdge(13,15)
    G1.addEdge(13,17)
    G1.addEdge(13,18)
    G1.addEdge(14,18)
    G1.addEdge(14,19)
    G1.addEdge(15,16)
    G1.addEdge(15,17)
    G1.addEdge(16,17)
    G1.addEdge(17,18)
    G1.addEdge(17,19)
    G1.addEdge(18,19)
    print("Coloring of graph G1")
    G1.DSatur()

colores = G1.DSatur()

conflictos = [
    (u,v)
    for u in range(1, G1.n + 1)
    for v in G1.adj[u]
    if u < v and colores[u] == colores[v]
]

print(f"Conexiones con conflicto: {conflictos}")
print(f"Número de colores: {len(set(colores[1:]))}")