# core/questionnaire.py - Lógica y datos del cuestionario para Fundación de Julián

QUESTIONS = [
    ("¿Logra saltar en un pie sin perder el equilibrio inmediatamente?", "Sí", "Motor Grueso"),
    ("¿Puede atrapar una pelota lanzada desde una distancia corta?", "Sí", "Coordinación Visomotriz"),
    ("¿Sube y baja escaleras alternando los pies (un pie por escalón)?", "Sí", "Motor Grueso"),
    ("¿Se golpea frecuentemente con esquinas o muebles al caminar?", "No", "Propiocepción"),
    ("¿Puede dibujar un círculo o una cruz siguiendo un modelo?", "Sí", "Motor Fino"),
    ("¿Escribe o dibuja aplicando una presión adecuada (ni muy débil ni rompe el papel)?", "Sí", "Control Grafomotor"),
    ("¿Logra abotonarse la camisa o amarrarse las trenzas solo?", "Sí", "Autonomía Motora"),
    ("¿Utiliza cubiertos (tenedor/cuchara) de forma funcional sin derramar demasiado?", "Sí", "Motricidad Fina"),
    ("¿Sigue instrucciones de tres pasos (ej: 'Limpia la mesa, trae el libro y siéntate')?", "Sí", "Comprensión Cognitiva"),
    ("¿Puede narrar una historia breve con un inicio, nudo y desenlace claros?", "Sí", "Lenguaje Narrativo"),
    ("¿Pronuncia correctamente todos los fonemas (sonidos) para su edad?", "Sí", "Lenguaje Articulatorio"),
    ("¿Inicia conversaciones con adultos o pares de forma espontánea?", "Sí", "Pragmática Social"),
    ("¿Entiende cuando alguien le habla en tono de broma o sarcasmo?", "Sí", "Lenguaje Comprensivo"),
    ("¿Suele quedarse 'en blanco' o 'con la mirada perdida' durante una charla?", "No", "Atención Sostenida"),
    ("¿Se distrae con ruidos ambientales que otros ignoran fácilmente?", "No", "Atención Selectiva"),
    ("¿Puede esperar su turno en un juego sin desesperarse o interrumpir?", "Sí", "Control Inhibitorio"),
    ("¿Pierde con frecuencia útiles escolares, ropa o juguetes?", "No", "Organización"),
    ("¿Muestra mucha dificultad para empezar una tarea si no se le ayuda?", "No", "Iniciación de Tarea"),
    ("¿Recuerda las instrucciones dadas hace 5 minutos?", "Sí", "Memoria de Trabajo"),
    ("¿Se bloquea o se enoja mucho si se cambia el orden de una actividad prevista?", "No", "Flexibilidad Cognitiva"),
    ("¿Muestra interés por jugar con otros niños en lugar de jugar solo siempre?", "Sí", "Interacción Social"),
    ("¿Mantiene el contacto visual cuando le hablas directamente?", "Sí", "Comunicación No Verbal"),
    ("¿Entiende las expresiones faciales de los demás (tristeza, enojo, alegría)?", "Sí", "Cognición Social"),
    ("¿Comparte sus intereses o logros con los demás de forma natural?", "Sí", "Reciprocidad Social"),
    ("¿Tiene reacciones de llanto o ira extremas por frustraciones pequeñas?", "No", "Regulación Emocional"),
    ("¿Parece estar 'en su propio mundo' la mayor parte del tiempo?", "No", "Alerta Social"),
    ("¿Le molestan las etiquetas de la ropa o ciertas texturas de telas?", "No", "Procesamiento Sensorial"),
    ("¿Se tapa los oídos ante sonidos comunes (licuadora, secador, gritos)?", "No", "Hiperreactividad Auditiva"),
    ("¿Es extremadamente selectivo con la comida por su textura o color?", "No", "Sensibilidad Oral"),
    ("¿Busca constantemente girar sobre sí mismo o balancearse?", "No", "Busca Sensorial (Vestibular)"),
    ("¿Le cuesta reconocer letras o números que ya debería saber?", "No", "Aprendizaje Académico"),
    ("¿Confunde derecha con izquierda o arriba con abajo constantemente?", "No", "Orientación Espacial"),
    ("¿Se muestra excesivamente tímido o retraído en entornos nuevos?", "No", "Área Ansiedad/Inhibición"),
    ("¿Tiene pesadillas recurrentes o dificultades marcadas para dormir solo?", "No", "Área Psicológica"),
    ("¿Actúa de forma impulsiva, como correr hacia la calle sin mirar?", "No", "Seguridad / Impulsividad"),
    ("¿Repite palabras o frases que acaba de escuchar (ecolalia)?", "No", "Comunicación"),
    ("¿Tiene movimientos extraños con las manos (aleteo) cuando está excitado?", "No", "Estereotipias"),
    ("¿Puede resolver problemas simples (ej: cómo alcanzar un juguete alto)?", "Sí", "Razonamiento"),
    ("¿Reconoce sus errores y trata de corregirlos por sí mismo?", "Sí", "Metacognición"),
    ("¿Se adapta bien a nuevos entornos (parques, casas de familiares)?", "Sí", "Adaptación Ambiental"),
]

# Tabla de derivación: mapea un índice de pregunta a una especialidad
SPECIALTIES_MAP = {
    # Desarrollo Motor y Tono -> Terapia Física
    0: "Terapia Física", 1: "Terapia Física", 2: "Terapia Física", 3: "Terapia Física",

    # Habilidades Sensoriales y Finas -> Terapia Ocupacional
    4: "Terapia Ocupacional", 5: "Terapia Ocupacional", 6: "Terapia Ocupacional", 7: "Terapia Ocupacional",
    26: "Terapia Ocupacional", 27: "Terapia Ocupacional", 28: "Terapia Ocupacional", 29: "Terapia Ocupacional",

    # Lenguaje y Comunicación -> Terapia de Lenguaje
    9: "Terapia de Lenguaje", 10: "Terapia de Lenguaje", 11: "Terapia de Lenguaje", 12: "Terapia de Lenguaje",
    35: "Terapia de Lenguaje",

    # Neuropsicología (Atención/FE) -> Neuropsicología Profesional
    13: "Neuropsicología Profesional", 14: "Neuropsicología Profesional", 15: "Neuropsicología Profesional",
    16: "Neuropsicología Profesional", 17: "Neuropsicología Profesional", 18: "Neuropsicología Profesional",
    19: "Neuropsicología Profesional", 30: "Neuropsicología Profesional", 31: "Neuropsicología Profesional",
    37: "Neuropsicología Profesional", 38: "Neuropsicología Profesional",

    # Salud Mental y Conducta -> Psicología Clínica Infantil
    24: "Psicología Clínica Infantil", 32: "Psicología Clínica Infantil", 33: "Psicología Clínica Infantil",
    34: "Psicología Clínica Infantil", 39: "Psicología Clínica Infantil",

    # Espectro / Desarrollo Social -> Neuropediatría
    20: "Neuropediatría", 21: "Neuropediatría", 22: "Neuropediatría", 23: "Neuropediatría",
    25: "Neuropediatría", 36: "Neuropediatría"
}

def evaluate_questionnaire(answers: list[str]) -> str:
    """
    Evalúa las respuestas del cuestionario y retorna la especialidad recomendada.
    'answers' es una lista de 40 strings (ej: 'si', 'no').
    """
    scores = {
        "Terapia Física": 0,
        "Terapia Ocupacional": 0,
        "Terapia de Lenguaje": 0,
        "Neuropsicología Profesional": 0,
        "Psicología Clínica Infantil": 0,
        "Neuropediatría": 0
    }

    # "Analiza el cuestionario de 40 preguntas. Si el usuario marca una respuesta que NO es la 'Esperada',
    # cuenta un punto para el área correspondiente. Al finalizar, genera un Perfil de Necesidades
    # priorizando el área con más puntos. Si hay fallas en los ítems de 'Espectro/Desarrollo Social',
    # sugiere siempre una consulta con Neuropediatría para diagnóstico diferencial."

    for idx, answer in enumerate(answers):
        if idx >= len(QUESTIONS):
            break

        expected = QUESTIONS[idx][1].lower()
        user_ans = answer.lower().strip()

        # Mapeamos acentos y variantes comunes si es necesario
        if user_ans in ['si', 'sí', 's']:
            user_ans = 'sí'
        if user_ans in ['no', 'n']:
            user_ans = 'no'

        if user_ans != expected:
            # Respuesta anormal, sumar punto
            specialty = SPECIALTIES_MAP.get(idx)
            if specialty:
                scores[specialty] += 1

    # Prioridad: Neuropediatría
    if scores["Neuropediatría"] > 0:
        return "Neuropediatría"

    # De lo contrario, buscar la especialidad con mayor puntuación
    max_score = -1
    best_specialty = "Consulta General" # Default si no hay fallas o algo falla

    for specialty, score in scores.items():
        if score > max_score:
            max_score = score
            best_specialty = specialty

    if max_score == 0:
        return "Consulta General" # Si no tuvo ninguna falla

    return best_specialty
