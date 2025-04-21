# ITAM Primavera 2025 - Tarea de Normalización

---

## Configuración

Este proyecto no tiene dependencias adicionales de Python, por lo que no es 
necesario crear un ambiente virtual. Está desarollado y probado con Python 3.13,
pero debe funcionar con 3.8 o superior.

## Funcionalidad Implementada

Este proyecto implementa las siguientes funcionalidades basadas en la teoría de normalización de bases de datos relacionales:

1.  **`FunctionalDependency.is_trivial()`**: Verifica si una dependencia funcional $X \rightarrow Y$ es trivial (es decir, si $Y \subseteq X$).
2.  **`MultivaluedDependency.is_trivial(heading)`**: Verifica si una dependencia multivaluada $X \twoheadrightarrow Y$ en un esquema con atributos $R$ (heading) es trivial (es decir, si $Y \subseteq X$ o $X \cup Y = R$).
3.  **`closure(attributes, fds)`**: Calcula la clausura $X^+$ de un conjunto de atributos $X$ bajo un conjunto de dependencias funcionales $F$.
4.  **`is_superkey(attributes, heading, fds)`**: Verifica si un conjunto de atributos $K$ es una superllave para un esquema con atributos $R$ y dependencias funcionales $F$ (es decir, si la clausura $K^+$ contiene a todos los atributos en $R$).
5.  **`is_key(attributes, heading, fds)`**: Verifica si un conjunto de atributos $K$ es una llave candidata (es decir, si es una superllave y ningún subconjunto propio de $K$ es también una superllave).
6.  **`is_relvar_in_bcnf(relvar)`**: Verifica si una variable de relación (esquema) cumple con la Forma Normal de Boyce-Codd (BCNF). Requiere que para toda dependencia funcional (FD) no trivial $X \rightarrow Y$, $X$ sea una superllave.
7.  **`is_relvar_in_4nf(relvar)`**: Verifica si una variable de relación cumple con la Cuarta Forma Normal (4NF). Requiere que esté en BCNF y que para toda dependencia multivaluada (MVD) no trivial $X \twoheadrightarrow Y$, $X$ sea una superllave.

## Suposiciones

* **Representación de Atributos**: Los atributos se manejan como objetos `Attribute` inmutables (basados en `dataclass(frozen=True)`). Cada atributo se identifica únicamente por su nombre (`str`).
* **Creación de Dependencias**: Las dependencias funcionales (FDs) y multivaluadas (MVDs) se crean a partir de strings con un formato específico, como `"{A, B} -> {C}"` o `"{X} ->-> {Y}"`. Las clases `FunctionalDependency` y `MultivaluedDependency` se encargan de validar y parsear estas expresiones. Los espacios en blanco alrededor de los nombres de atributos y separadores se ignoran.
* **Conjuntos de Atributos**: Los componentes de las dependencias (`determinant`, `dependant`) y el encabezado de la relación (`heading`) se representan internamente como `set` de Python que contienen objetos `Attribute`.
* **Clase `Relvar`**: Esta clase encapsula la definición de un esquema de relación, almacenando su `heading` (conjunto de atributos), `functional_dependencies` (conjunto de FDs) y `multivalued_dependencies` (conjunto de MVDs). Valida que cualquier dependencia añadida solo contenga atributos presentes en el `heading`.
* **Trivialidad de MVDs**: La verificación de si una MVD es trivial (`MultivaluedDependency.is_trivial`) requiere conocer el `heading` completo de la relación a la que pertenece, ya que una de las condiciones de trivialidad ($X \cup Y = R$) depende de ello.
* **Corrección de Algoritmos**: La correctitud de los resultados de las funciones de `algorithms.py` (cálculo de clausura, verificación de llaves y formas normales) depende de que el conjunto de FDs y MVDs proporcionado al `Relvar` o a las funciones sea completo y correcto para el esquema relacional que se está analizando.

## Ejemplos de Uso

El archivo `example.py` contiene código ejecutable para probar las funciones. A continuación se muestran fragmentos clave y los resultados esperados:

### 1. Preparación (Creación de Atributos y Dependencias)

```python
from normalization.components import Relvar, FunctionalDependency, MultivaluedDependency, Attribute
from normalization.algorithms import closure, is_superkey, is_key, is_relvar_in_bcnf, is_relvar_in_4nf

# Función auxiliar para crear conjuntos de Atributos fácilmente
def attrs(names_str: str) -> set[Attribute]:
    """Crea un conjunto de objetos Attribute desde un string separado por comas."""
    if not names_str:
        return set()
    return {Attribute(name.strip()) for name in names_str.split(',')}

# Crear Dependencias Funcionales (FDs)
fd1 = FunctionalDependency("{RFC} -> {Nombre, CP}")
fd2 = FunctionalDependency("{FolioF} -> {RFC}")
fd_trivial = FunctionalDependency("{A, B} -> {A}")
fd_nontrivial = FunctionalDependency("{A} -> {B}")

# Crear Dependencias Multivaluadas (MVDs)
mvd1 = MultivaluedDependency("{RFC} ->-> {RegimenC}")
mvd_trivial_subset = MultivaluedDependency("{A, B} ->-> {A}") # Y subconjunto X
mvd_trivial_union = MultivaluedDependency("{A, B} ->-> {C, D}") # X union Y = R
mvd_nontrivial = MultivaluedDependency("{A} ->-> {B}")

# Crear un conjunto de atributos para un encabezado (heading)
heading_simple = attrs("A,B,C,D")

# Crear una Variable de Relación (Relvar)
# (Usando FDs y MVDs del ejemplo original en example.py)
all_fds = [
    FunctionalDependency("{RFC} -> {Nombre, CP}"),
    FunctionalDependency("{FolioF} -> {RFC}"),
    FunctionalDependency("{FolioF} -> {MontoF, IVA, FechaF}"),
    FunctionalDependency("{FolioF} -> {RegimenF, CFDI}"),
    FunctionalDependency("{FolioP} -> {MontoP, FechaP}"),
    FunctionalDependency("{FolioP} -> {FolioF}")
]
all_mvds = [
    MultivaluedDependency("{RFC} ->-> {RegimenC}")
]
original_heading_list = ["Nombre", "RFC", "CP", "RegimenF", "RegimenC", "CFDI", "FolioF", "MontoF", "IVA", "FechaF", "Producto", "FolioP", "MontoP", "FechaP"]

original_relvar = Relvar(
    heading=original_heading_list,
    functional_dependencies=all_fds,
    multivalued_dependencies=all_mvds
)