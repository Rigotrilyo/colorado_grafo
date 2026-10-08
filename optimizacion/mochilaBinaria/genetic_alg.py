from statistics import mean
import random
import csv
import time

pesos = [
    61, 58, 92, 50, 108, 83, 93, 101, 54, 50,
    72, 51, 100, 108, 91, 112, 66, 58, 110, 73
]
beneficios = [
    1100, 1147, 1442, 1591, 1078, 1385, 1777, 1196, 1753, 1371,
    1517, 1675, 1193, 1177, 1365, 1143, 1314, 1526, 1470, 1605
]
capacidad = 800
#Parámetros de algoritmo genético
TAMANO_POBLACION = 50
NUM_CICLOS = 1000
TAMANO_TORNEO = 3
PROB_CRUCE = 0.9
PROB_MUTACION = 1 / len(pesos)
NUM_EJECUCIONES = 10
PENALIZACION = 2 * max(beneficios)  # Penalización por violar la restricción de capacidad
OPTIMO_GAMS = 18103
PESO_OPTIMO_GAMS = 800

def evaluar(cromosoma):
    peso = sum(
        pesos[i]*cromosoma[i]
        for i in range(len(pesos))
    )

    beneficio = sum(
       
        beneficios[i]*cromosoma[i]
        for i in range(len(pesos))
    )

    return peso, beneficio

def crear_poblacion(generador):
    poblacion = [[0]*len(pesos)] #Barco vacío

    for _ in range(TAMANO_POBLACION - 1):
        cromosoma = [
            generador.randint(0,1)
            for _ in range(len(pesos))
        ]
        poblacion.append(cromosoma)
    return poblacion

###Segundo bloque de cálculo fitness y seleccionar padres
def calcular_fitness(cromosoma):
    peso, beneficio = evaluar(cromosoma)
    exceso = max(0, peso - capacidad)
    return beneficio - PENALIZACION * exceso

def seleccionar_padres(poblacion, generador):
    candidatos = generador.sample(
        range(len(poblacion)),
        TAMANO_TORNEO
    )

    ganador = max(
        candidatos,
        key = lambda indice: calcular_fitness(poblacion[indice])
    )
    return ganador

def cruzar(padre1, padre2, generador):
    #Copias para conservar los padres
    hijo1 = padre1.copy()
    hijo2 = padre2.copy()

    if generador.random() < PROB_CRUCE:
        punto = generador.randint(1, len(padre1)-1)

        hijo1 = padre1[:punto] + padre2[punto:]
        hijo2 = padre2[:punto] + padre1[punto:]

        return hijo1, hijo2, punto

    return hijo1, hijo2, None

def mutar(hijo, generador):
    mutado = hijo.copy()
    for i in range(len(mutado)):
        if generador.random() < PROB_MUTACION:
            mutado[i] = 1 - mutado[i]
    return mutado

def ejecutar_genetico(semilla, solo_factibles=False):
    generador = random.Random(semilla)
    inicio = time.perf_counter()
    poblacion = crear_poblacion(generador)

    if solo_factibles:
        poblacion = [
            reparar(individuo, generador)
            for individuo in poblacion
        ]

    #Mejor solución factible de la solución inicial
    factibles = [
        cromosoma for cromosoma in poblacion
        if evaluar(cromosoma)[0] <= capacidad
    ]



    mejor_cromosoma = max(
        factibles,
        key=lambda cromosoma: evaluar(cromosoma)[1]
    ).copy()

    mejor_peso, mejor_beneficio = evaluar(mejor_cromosoma)

    for _ in range(NUM_CICLOS):
        indice1 = seleccionar_padres(poblacion, generador)
        indice2 = seleccionar_padres(poblacion, generador)

        hijo1, hijo2, _ = cruzar(
            poblacion[indice1],
            poblacion[indice2],
            generador
        )

        hijo1 = mutar(hijo1, generador)
        hijo2 = mutar(hijo2, generador)

        if solo_factibles:
            hijo1 = reparar(hijo1, generador)
            hijo2 = reparar(hijo2, generador)

        #Guardar mejor hijo factible, aún si sale de la población
        for hijo in (hijo1, hijo2):
            peso_hijo, beneficio_hijo = evaluar(hijo)

            if peso_hijo <= capacidad and beneficio_hijo > mejor_beneficio:
                mejor_cromosoma = hijo.copy()
                mejor_peso = peso_hijo
                mejor_beneficio = beneficio_hijo

        dos_peores = sorted(
            range(len(poblacion)),
            key=lambda indice: calcular_fitness(poblacion[indice])
        )[:2]

        poblacion[dos_peores[0]] = hijo1.copy()
        poblacion[dos_peores[1]] = hijo2.copy()

    tiempo = time.perf_counter() - inicio
    return mejor_cromosoma, mejor_peso, mejor_beneficio, tiempo

def reparar(cromosoma, generador):
    reparado = cromosoma.copy()

    while evaluar(reparado)[0] > capacidad:
        seleccionados = [
            i for i, bit in enumerate(reparado) if bit == 1
        ]
        quitar = generador.choice(seleccionados)
        reparado[quitar] = 0

    return reparado

resultados = []

for nombre, solo_factibles in [
    ("con penalización", False),
    ("solo factibles", True)
]:
    for semilla in range(1, NUM_EJECUCIONES + 1):
        cromosoma, peso, beneficio, tiempo = ejecutar_genetico(
            semilla,
            solo_factibles=solo_factibles
        )

        assert peso <= capacidad
        assert beneficio <= OPTIMO_GAMS, (
            "El genético superó el óptimo; revisa los datos de GAMS y Python"
        )

        resultados.append({
            "caso": 2,
            "propuesta": nombre,
            "etapa": f"{NUM_CICLOS} ciclos",
            "semilla": semilla,
            "peso": peso,
            "beneficio_factible": beneficio,
            "tiempo_s": tiempo,
            "optimo_gams": OPTIMO_GAMS,
            "diferencia_pct":
                100 * (OPTIMO_GAMS - beneficio) / OPTIMO_GAMS
        })

        print(
            f"{nombre}, semilla {semilla}: "
            f"beneficio={beneficio}, peso={peso}, "
            f"tiempo={tiempo:.6f} s"
        )

columnas = [
    "caso", "propuesta", "etapa", "semilla",
    "peso", "beneficio_factible", "tiempo_s",
    "optimo_gams", "diferencia_pct"
]

with open("resultado_ga.csv", "w", newline="", encoding="utf-8-sig") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=columnas)
    escritor.writeheader()
    escritor.writerows(resultados)

for nombre in ("con penalización", "solo factibles"):
    filas = [fila for fila in resultados if fila["propuesta"] == nombre]

    print(f"\nResumen de {nombre}:")
    print("Beneficio promedio:",
          mean(fila["beneficio_factible"] for fila in filas))
    print("Mejor beneficio:",
          max(fila["beneficio_factible"] for fila in filas))
    print("Tiempo promedio (s):",
          mean(fila["tiempo_s"] for fila in filas))
    print("Diferencia promedio (%):",
          mean(fila["diferencia_pct"] for fila in filas))
    print("Veces que alcanzó el óptimo:",
          sum(fila["diferencia_pct"] == 0 for fila in filas))

print("\nSe creó resultado_ga.csv con", len(resultados), "filas")

resumen = []

for nombre in ("con penalización", "solo factibles"):
    filas = [fila for fila in resultados if fila["propuesta"] == nombre]

    resumen.append({
        "propuesta": nombre, 
        "beneficio_promedio": mean(f["beneficio_factible"] for f in filas),
        "mejor_beneficio": max(f["beneficio_factible"] for f in filas),
        "brecha_promedio_pct": mean(f["diferencia_pct"] for f in filas),
        "veces_optimo": sum(f["diferencia_pct"] == 0 for f in filas),
        "tiempo_promedio_s": mean(f["tiempo_s"] for f in filas)
    })

with open("resumen_ga.csv", "w", newline="", encoding="utf-8-sig") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=resumen[0].keys())
    escritor.writeheader()
    escritor.writerows(resumen)

print("Se creó resumen_ga.csv")