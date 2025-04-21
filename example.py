
from normalization.components import Relvar, FunctionalDependency, MultivaluedDependency, Attribute
from normalization.algorithms import closure, is_superkey, is_key, is_relvar_in_bcnf, is_relvar_in_4nf
from normalization.exceptions import InvalidExpression # Import exception for potential testing

# Helper function to create sets of Attribute objects from strings easily
def attrs(names_str: str) -> set[Attribute]:
    """Creates a set of Attribute objects from a comma-separated string."""
    if not names_str:
        return set()
    return {Attribute(name.strip()) for name in names_str.split(',')}

if __name__ == "__main__":

    print("=============================================")
    print(" Testing Implementations from Tarea 3 ")
    print("=============================================\n")

    # --- 1. Test is_trivial (FD and MVD) ---
    print("--- 1. Testing is_trivial ---")
    # Functional Dependencies
    fd_trivial = FunctionalDependency("{A, B} -> {A}")
    fd_nontrivial = FunctionalDependency("{A} -> {B}")
    print(f"FD: {fd_trivial} -> Trivial? {fd_trivial.is_trivial()} (Expected: True)")
    print(f"FD: {fd_nontrivial} -> Trivial? {fd_nontrivial.is_trivial()} (Expected: False)")

    # Multivalued Dependencies
    heading_simple1 = attrs("A,B,C,D")
    mvd_trivial_subset = MultivaluedDependency("{A, B} ->-> {A}") # Y subset X
    mvd_trivial_union = MultivaluedDependency("{A, B} ->-> {C, D}") # X union Y = R
    mvd_nontrivial = MultivaluedDependency("{A} ->-> {B}") # Neither condition met

    print(f"MVD: {mvd_trivial_subset} on heading { {a.name for a in heading_simple1} } -> Trivial? {mvd_trivial_subset.is_trivial(heading_simple1)} (Expected: True)")
    print(f"MVD: {mvd_trivial_union} on heading { {a.name for a in heading_simple1} } -> Trivial? {mvd_trivial_union.is_trivial(heading_simple1)} (Expected: True)")
    print(f"MVD: {mvd_nontrivial} on heading { {a.name for a in heading_simple1} } -> Trivial? {mvd_nontrivial.is_trivial(heading_simple1)} (Expected: False)")
    print("-" * 20)

    # --- Setup Relvar from Original example.py ---
    print("\n--- Setting up Original Relvar ---")
    fd1 = FunctionalDependency("{RFC} -> {Nombre, CP}")
    fd2 = FunctionalDependency("{FolioF} -> {RFC}")
    fd3 = FunctionalDependency("{FolioF} -> {MontoF, IVA, FechaF}")
    fd4 = FunctionalDependency("{FolioF} -> {RegimenF, CFDI}")
    fd5 = FunctionalDependency("{FolioP} -> {MontoP, FechaP}")
    fd6 = FunctionalDependency("{FolioP} -> {FolioF}")
    # fd7 = FunctionalDependency("{MontoF} -> {IVA}") # Potentially redundant / transitive

    mvd1 = MultivaluedDependency("{RFC} ->-> {RegimenC}")

    try:
        original_relvar = Relvar(
            heading=["Nombre", "RFC", "CP", "RegimenF", "RegimenC", "CFDI", "FolioF", "MontoF", "IVA", "FechaF", "Producto", "FolioP", "MontoP", "FechaP"],
            functional_dependencies=[fd1, fd2, fd3, fd4, fd5, fd6], # Add fd7 if needed
            multivalued_dependencies=[mvd1]
        )
        print(f"Original Relvar defined with heading: { {a.name for a in original_relvar.heading} }")
        print(f"FDs: {original_relvar.functional_dependencies}")
        print(f"MVDs: {original_relvar.multivalued_dependencies}")

        # Test is_trivial on MVD from original example
        print(f"MVD: {mvd1} on original heading -> Trivial? {mvd1.is_trivial(original_relvar.heading)} (Expected: False)")

    except (InvalidExpression, ValueError, TypeError) as e:
        print(f"Error creating original relvar: {e}")
        original_relvar = None # Ensure it's None if creation failed

    print("-" * 20)


    # Proceed only if original_relvar was created successfully
    if original_relvar:
        # --- 2. Test closure ---
        print("\n--- 2. Testing closure ---")
        attrs_foliop = attrs("FolioP")
        closure_foliop = closure(attrs_foliop, original_relvar.functional_dependencies)
        print(f"Closure of {{FolioP}}: { {a.name for a in closure_foliop} }")
        # Expected based on FDs: {FolioP, MontoP, FechaP, FolioF, RFC, Nombre, CP, MontoF, IVA, FechaF, RegimenF, CFDI}

        attrs_rfc = attrs("RFC")
        closure_rfc = closure(attrs_rfc, original_relvar.functional_dependencies)
        print(f"Closure of {{RFC}}: { {a.name for a in closure_rfc} }")
        # Expected: {RFC, Nombre, CP}
        print("-" * 20)

        # --- 3. Test is_superkey and is_key ---
        print("\n--- 3. Testing is_superkey and is_key ---")
        # Test {FolioP} - not a superkey based on closure calculation
        print(f"Is {{FolioP}} a superkey? {is_superkey(attrs_foliop, original_relvar.heading, original_relvar.functional_dependencies)} (Expected: False)")
        print(f"Is {{FolioP}} a candidate key? {is_key(attrs_foliop, original_relvar.heading, original_relvar.functional_dependencies)} (Expected: False)")

        # Test {FolioP, Producto, RegimenC} - should be a superkey and key
        attrs_candidate = attrs("FolioP, Producto, RegimenC")
        closure_candidate = closure(attrs_candidate, original_relvar.functional_dependencies)
        print(f"Closure of {{FolioP, Producto, RegimenC}}: { {a.name for a in closure_candidate} }")
        print(f"(Closure contains all heading attributes? {original_relvar.heading.issubset(closure_candidate)})")

        print(f"Is {{FolioP, Producto, RegimenC}} a superkey? {is_superkey(attrs_candidate, original_relvar.heading, original_relvar.functional_dependencies)} (Expected: True)")
        # To check if it's a key, need to check proper subsets:
        # C({FolioP, Producto}) = Closure(FolioP) U {Producto} -> No
        # C({FolioP, RegimenC}) = Closure(FolioP) U {RegimenC} -> No
        # C({Producto, RegimenC}) = {Producto, RegimenC} -> No
        print(f"Is {{FolioP, Producto, RegimenC}} a candidate key? {is_key(attrs_candidate, original_relvar.heading, original_relvar.functional_dependencies)} (Expected: True)")
        print("-" * 20)


        # --- 4. Test is_relvar_in_bcnf ---
        print("\n--- 4. Testing is_relvar_in_bcnf ---")
        # Test original relvar
        # Violation likely: RFC -> {Nombre, CP}. Cierre(RFC) = {RFC, Nombre, CP}. Not a superkey.
        print(f"Is Original Relvar in BCNF? {is_relvar_in_bcnf(original_relvar)} (Expected: False)")

        # Simple BCNF examples
        fd_bcnf_yes = FunctionalDependency("{A, B} -> {C}")
        relvar_bcnf_yes = Relvar(heading=["A", "B", "C"], functional_dependencies=[fd_bcnf_yes])
        print(f"Is Relvar(A,B,C FDs={{AB->C}}) in BCNF? {is_relvar_in_bcnf(relvar_bcnf_yes)} (Expected: True)")

        fd_bcnf_no1 = FunctionalDependency("{A, B} -> {C}")
        fd_bcnf_no2 = FunctionalDependency("{C} -> {B}")
        relvar_bcnf_no = Relvar(heading=["A", "B", "C"], functional_dependencies=[fd_bcnf_no1, fd_bcnf_no2])
        print(f"Is Relvar(A,B,C FDs={{AB->C, C->B}}) in BCNF? {is_relvar_in_bcnf(relvar_bcnf_no)} (Expected: False)")
        print("-" * 20)

        # --- 5. Test is_relvar_in_4nf ---
        print("\n--- 5. Testing is_relvar_in_4nf ---")
        # Test original relvar
        # Fails BCNF, so should fail 4NF. Also MVD {RFC} ->-> {RegimenC} is non-trivial, and RFC is not a superkey.
        print(f"Is Original Relvar in 4NF? {is_relvar_in_4nf(original_relvar)} (Expected: False)")

        # Simple 4NF examples
        # This one is BCNF and has no MVDs, so it's 4NF
        print(f"Is Relvar(A,B,C FDs={{AB->C}}) in 4NF? {is_relvar_in_4nf(relvar_bcnf_yes)} (Expected: True)")

        # Example CTX : R(C,T,X), MVDs={C->>T, C->>X} (no FDs)
        mvd_ctx1 = MultivaluedDependency("{C} ->-> {T}")
        mvd_ctx2 = MultivaluedDependency("{C} ->-> {X}")
        relvar_ctx = Relvar(heading=["C", "T", "X"], functional_dependencies=[], multivalued_dependencies=[mvd_ctx1, mvd_ctx2])
        print(f"Is Relvar(C,T,X MVDs={{C->>T, C->>X}}) in BCNF? {is_relvar_in_bcnf(relvar_ctx)} (Expected: True)") # True as no FDs violate
        print(f"Is Relvar(C,T,X MVDs={{C->>T, C->>X}}) in 4NF? {is_relvar_in_4nf(relvar_ctx)} (Expected: False)") # False because C is not superkey
        print("-" * 20)

    else:
        print("\nSkipping algorithm tests because original relvar creation failed.")

    print("\n=============================================")
    print("          Testing Complete          ")
    print("=============================================")
"""
from normalization.components import Relvar, FunctionalDependency, MultivaluedDependency


if __name__ == "__main__":
    fd1 = FunctionalDependency("{RFC} -> {Nombre, CP}")
    fd2 = FunctionalDependency("{FolioF} -> {RFC}")
    fd3 = FunctionalDependency("{FolioF} -> {MontoF, IVA, FechaF}")
    fd4 = FunctionalDependency("{FolioF} -> {RegimenF, CFDI}")
    fd5 = FunctionalDependency("{FolioP} -> {MontoP, FechaP}")
    fd6 = FunctionalDependency("{FolioP} -> {FolioF}")
    fd7 = FunctionalDependency("{MontoF} -> {IVA}")

    mvd1 = MultivaluedDependency("{RFC} ->-> {RegimenC}")

    relvar = Relvar(
        heading=["Nombre", "RFC", "CP", "RegimenF", "RegimenC", "CFDI", "FolioF", "MontoF", "IVA", "FechaF", "Producto", "FolioP", "MontoP", "FechaP"],
        functional_dependencies=[fd1, fd2, fd3, fd4, fd5, fd6],
        multivalued_dependencies=[mvd1]
    )

    print(f"Relvar: {relvar}")

    print("\nFunctional dependencies:")
    for fd in relvar.functional_dependencies:
        print(fd)

    print("\nMultivalued dependencies:")
    for mvd in relvar.multivalued_dependencies:
        print(mvd)
"""