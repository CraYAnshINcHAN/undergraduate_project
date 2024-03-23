from numba import njit

@njit(cache=True)
def _reset_scalar_ghost(input, ghost_idx, reset_value = 0.0):
    for k in ghost_idx:
        print("_reset_ghost_vector_or_scalar_6")
        print("reset_value: ", reset_value)
        input[k] = reset_value