from .components import FunctionalDependency, Attribute, Relvar

def closure(attributes: set[Attribute], functional_dependencies: set[FunctionalDependency]) -> set[Attribute]:
    """
    Calcula la clausura de atributos de un conjunto de atributos bajo un conjunto de dependencias funcionales.

    Args:
        attributes (set[Attribute]): El conjunto inicial de atributos.
        functional_dependencies (set[FunctionalDependency]): El conjunto de dependencias funcionales.

    Returns:
        set[Attribute]: La clausura de atributos (X+).
    """
    current_closure = set(attributes) # Empezar con los atributos iniciales

    while True:
        closure_changed = False
        # Iterar sobre una copia del conjunto para evitar problemas si el conjunto pudiera cambiar (no debería ocurrir aquí)
        for fd in functional_dependencies:
            # Verificar si el determinante (X) de la DF X -> Y está completamente contenido en la clausura actual
            if fd.determinant.issubset(current_closure):
                # Encontrar atributos en el dependiente (Y) que aún no están en la clausura
                new_attributes = fd.dependant - current_closure
                if new_attributes:
                    # Añadir los nuevos atributos a la clausura
                    current_closure.update(new_attributes)
                    closure_changed = True # Marcar que la clausura ha crecido

        # Si no se añadieron nuevos atributos en una pasada completa, la clausura está completa
        if not closure_changed:
            break

    return current_closure


def is_superkey(attributes: set[Attribute], heading: set[Attribute], functional_dependencies: set[FunctionalDependency]) -> bool:
    """
    Verifica si un conjunto de atributos es una superllave para un esquema de relación.
    Un conjunto K es una superllave si su clausura K+ contiene todos los atributos de la relación (encabezado R).

    Args:
        attributes (set[Attribute]): El conjunto de atributos a verificar (potencial superllave K).
        heading (set[Attribute]): El conjunto de todos los atributos en la relación (R).
        functional_dependencies (set[FunctionalDependency]): El conjunto de dependencias funcionales (F).

    Returns:
        bool: True si los atributos forman una superllave, False en caso contrario.
    """
    # Calcular la clausura de los atributos dados usando las DFs proporcionadas
    attribute_closure = closure(attributes, functional_dependencies)
    # Verificar si la clausura calculada contiene todos los atributos en el encabezado
    # Debe cumplirse que R sea subconjunto de K+
    return heading.issubset(attribute_closure)


def is_key(attributes: set[Attribute], heading: set[Attribute], functional_dependencies: set[FunctionalDependency]) -> bool:
    """
    Verifica si un conjunto de atributos es una llave candidata para un esquema de relación.
    Un conjunto K es una llave candidata si:
    1. Es una superllave (K -> R).
    2. Es mínima (ningún subconjunto propio de K es también una superllave).

    Args:
        attributes (set[Attribute]): El conjunto de atributos a verificar (potencial llave K).
        heading (set[Attribute]): El conjunto de todos los atributos en la relación (R).
        functional_dependencies (set[FunctionalDependency]): El conjunto de dependencias funcionales (F).

    Returns:
        bool: True si los atributos forman una llave candidata, False en caso contrario.
    """
    # 1. Verificar si es una superllave
    if not is_superkey(attributes, heading, functional_dependencies):
        return False

    # 2. Verificar la minimalidad
    # Si el conjunto tiene 0 o 1 atributo, es mínimo por definición (si es una superllave)
    # Un conjunto vacío no puede ser una superllave a menos que el encabezado también esté vacío.
    if len(attributes) <= 1:
        return True # Es una superllave y no tiene subconjuntos propios para verificar (o solo el conjunto vacío)

    # Iterar sobre todos los subconjuntos propios (obtenidos eliminando un atributo)
    for attr_to_remove in attributes:
        proper_subset = attributes - {attr_to_remove}
        # Si el subconjunto propio está vacío, omitir (o manejar si el encabezado está vacío)
        if not proper_subset:
             continue
        # Verificar si este subconjunto propio también es una superllave
        if is_superkey(proper_subset, heading, functional_dependencies):
            # Si *cualquier* subconjunto propio es una superllave, entonces 'attributes' no es mínimo
            return False

    # Si es una superllave y no se encontró ningún subconjunto propio que sea superllave, entonces es una llave candidata
    return True


def is_relvar_in_bcnf(relvar: Relvar) -> bool:
    """
    Verifica si una variable de relación está en Forma Normal de Boyce-Codd (FNBC/BCNF).

    Args:
        relvar (Relvar): La variable de relación que contiene encabezado, DFs y DVMs.

    Returns:
        bool: True si la RelVar está en BCNF, False en caso contrario.
    """
    # Iterar sobre todas las dependencias funcionales definidas para la relvar
    for fd in relvar.functional_dependencies:
        # Verificar si la DF es no trivial usando el método de FunctionalDependency
        if not fd.is_trivial():
            # Si es no trivial, verificar si su determinante (X) es una superllave para la relvar
            # Usar la función is_superkey definida arriba
            determinant_is_superkey = is_superkey(fd.determinant, relvar.heading, relvar.functional_dependencies)
            # Si encontramos alguna DF no trivial donde el determinante NO es una superllave, viola BCNF
            if not determinant_is_superkey:
                return False

    # Si el bucle termina sin encontrar ninguna violación, la relvar está en BCNF
    return True


def is_relvar_in_4nf(relvar: Relvar) -> bool:
    """
    Verifica si una variable de relación está en Cuarta Forma Normal (4NF).

    Args:
        relvar (Relvar): La variable de relación que contiene encabezado, DFs y DVMs.

    Returns:
        bool: True si la RelVar está en 4NF, False en caso contrario.
    """
    # Comprobación 1: Debe estar en BCNF. Si no, no puede estar en 4NF.
    if not is_relvar_in_bcnf(relvar):
        # print("No está en 4NF porque no está en BCNF.") # Impresión de depuración opcional
        return False

    # Comprobación 2: Todas las DVMs no triviales X ->> Y deben tener X como superllave.
    # Iterar sobre todas las dependencias multivaluadas definidas para la relvar
    for mvd in relvar.multivalued_dependencies:
        # Verificar si la DVM es no trivial. Requiere el encabezado.
        # Pasar relvar.heading al método is_trivial de la DVM
        if not mvd.is_trivial(relvar.heading):
            # Si es no trivial, verificar si su determinante (X) es una superllave para la relvar
            # ¡El estado de superllave está determinado por las DFs!
            determinant_is_superkey = is_superkey(mvd.determinant, relvar.heading, relvar.functional_dependencies)
            # Si encontramos alguna DVM no trivial donde el determinante NO es una superllave, viola 4NF
            if not determinant_is_superkey:
                return False

    # Si pasa la comprobación de BCNF y la comprobación de DVM, entonces está en 4NF
    return True