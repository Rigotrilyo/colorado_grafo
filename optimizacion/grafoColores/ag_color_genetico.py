"""Coloración de un grafo con DSatur (referencia) y un algoritmo genético.

Los nodos externos se numeran del 1 al 19. Cada cromosoma del algoritmo
genético tiene 19 genes: el gen 0 guarda el color del nodo 1, etcétera.
"""

import random
from time import perf_counter


class Graph:
    def __init__(self, numNodes):
        self.n = numNodes
        self.adj = [set() for _ in range(numNodes + 1)]

    def addEdge(self, u, v):
        if not (1 <= u <= self.n and 1 <= v <= self.n) or u == v:
            raise ValueError(f"Conexión no válida: ({u}, {v})")
        self.adj[u].add(v)
        self.adj[v].add(u)

    def aristas(self):
        # Cada conexión de un grafo no dirigido se cuenta solo una vez.
        return [(u, v) for u in range(1, self.n + 1)
                for v in self.adj[u] if u < v]

    def conflictos(self, colores):
        """Recibe colores[1..n] y devuelve las conexiones con igual color."""
        return [(u, v) for u, v in self.aristas()
                if colores[u] == colores[v]]

    def DSatur(self):
        """Solución voraz de referencia, independiente del genético."""
        colores = [0] * (self.n + 1)

        while any(colores[u] == 0 for u in range(1, self.n + 1)):
            def prioridad(u):
                colores_vecinos = {colores[v] for v in self.adj[u]
                                   if colores[v] != 0}
                return len(colores_vecinos), len(self.adj[u]), -u

            u = max((v for v in range(1, self.n + 1) if colores[v] == 0),
                    key=prioridad)
            prohibidos = {colores[v] for v in self.adj[u]}
            color = 1
            while color in prohibidos:
                color += 1
            colores[u] = color

        return colores


def algoritmo_genetico(grafo, num_colores, tam_poblacion=100,
                       max_generaciones=1000, prob_cruce=0.8,
                       prob_mutacion=0.02, semilla=42):
    """Busca una coloración sin conflictos con una paleta fija de K colores.

    Selección por torneo de 3; cruza de un punto; mutación por gen;
    reemplazo generacional conservando los 2 mejores individuos.
    """
    if grafo.n < 2 or num_colores < 1 or tam_poblacion < 3:
        raise ValueError("Se requieren al menos 2 nodos, 1 color y 3 individuos")
    if max_generaciones < 0 or not (0 <= prob_cruce <= 1) or not (0 <= prob_mutacion <= 1):
        raise ValueError("Revisa el máximo de generaciones y las probabilidades")

    inicio = perf_counter()
    rng = random.Random(semilla)
    aristas = grafo.aristas()

    def contar_conflictos(cromosoma):
        # cromosoma[0] es el nodo 1; por eso se resta 1 a u y a v.
        return sum(cromosoma[u - 1] == cromosoma[v - 1]
                   for u, v in aristas)

    poblacion = [[rng.randint(1, num_colores) for _ in range(grafo.n)]
                 for _ in range(tam_poblacion)]
    mejor = min(poblacion, key=contar_conflictos)[:]
    mejor_conflictos = contar_conflictos(mejor)
    historial = [(0, mejor_conflictos)]
    generacion = 0

    while generacion < max_generaciones and mejor_conflictos > 0:
        poblacion.sort(key=contar_conflictos)
        nueva = [individuo[:] for individuo in poblacion[:2]]  # Elitismo

        def torneo():
            candidatos = rng.sample(poblacion, 3)
            return min(candidatos, key=contar_conflictos)

        while len(nueva) < tam_poblacion:
            padre1, padre2 = torneo(), torneo()

            if rng.random() < prob_cruce:
                punto = rng.randrange(1, grafo.n)  # Corte tras un gen
                hijos = [padre1[:punto] + padre2[punto:],
                         padre2[:punto] + padre1[punto:]]
            else:
                hijos = [padre1[:], padre2[:]]

            for hijo in hijos:
                for posicion in range(grafo.n):
                    if rng.random() < prob_mutacion and num_colores > 1:
                        # Elegir otro color de la paleta, distinto del actual.
                        nuevo = rng.randrange(1, num_colores)
                        if nuevo >= hijo[posicion]:
                            nuevo += 1
                        hijo[posicion] = nuevo
                if len(nueva) < tam_poblacion:
                    nueva.append(hijo)

        poblacion = nueva
        generacion += 1
        candidato = min(poblacion, key=contar_conflictos)
        conflictos_candidato = contar_conflictos(candidato)
        if conflictos_candidato < mejor_conflictos:
            mejor = candidato[:]
            mejor_conflictos = conflictos_candidato
        historial.append((generacion, mejor_conflictos))

    return {
        # El cero inicial permite validar con colores[u], como en DSatur.
        "colores": [0] + mejor,
        "conflictos": mejor_conflictos,
        "fitness": 1 / (1 + mejor_conflictos),
        "generaciones": generacion,
        "tiempo_s": perf_counter() - inicio,
        "historial": historial,
    }


if __name__ == "__main__":
    G1 = Graph(19)
    conexiones = [
        (1, 2), (1, 16), (1, 4),
        (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
        (3, 7), (3, 11), (3, 19),
        (4, 8), (4, 9), (4, 5),
        (5, 6), (5, 9), (5, 10),
        (6, 7), (6, 11), (6, 14),
        (7, 11),
        (8, 9), (8, 12),
        (9, 10), (9, 12), (9, 13), (9, 15),
        (10, 13), (10, 14),
        (11, 14), (11, 19),
        (12, 15), (12, 16),
        (13, 14), (13, 15), (13, 17), (13, 18),
        (14, 18), (14, 19),
        (15, 16), (15, 17),
        (16, 17),
        (17, 18), (17, 19),
        (18, 19),
    ]
    for u, v in conexiones:
        G1.addEdge(u, v)

    NUM_COLORES = 4  # Cambia esto según los colores disponibles en tu tarea.
    resultado = algoritmo_genetico(G1, num_colores=NUM_COLORES)
    colores = resultado["colores"]

    print("Nodo | Color genético | Color DSatur")
    referencia = G1.DSatur()
    for nodo in range(1, G1.n + 1):
        print(f"{nodo:>4} | {colores[nodo]:>14} | {referencia[nodo]:>12}")
    print(f"Conexiones: {len(G1.aristas())}")
    print(f"Conflictos de la solución genética: {G1.conflictos(colores)}")
    print(f"Colores utilizados: {len(set(colores[1:]))}")
    print(f"Fitness: {resultado['fitness']:.4f}")
    print(f"Generaciones ejecutadas: {resultado['generaciones']}")
    print(f"Tiempo: {resultado['tiempo_s']:.6f} segundos")
    print(f"DSatur usa {len(set(referencia[1:]))} colores; "
          f"conflictos: {len(G1.conflictos(referencia))}")
    if resultado["conflictos"]:
        print("No se encontró una coloración válida con esos colores "
              "y esa cantidad de generaciones.")
