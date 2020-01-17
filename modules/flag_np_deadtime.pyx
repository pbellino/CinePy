cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def flag_np_deadtime(unsigned long[:] data, int tau_np,
                          unsigned long flag):
    cdef unsigned long[:] result
    cdef int i, j, N_tot
    result = data.copy()
    N_tot = data.size
    for i in range(N_tot):
        if result[i] != flag:
            for j in range(1, N_tot-i):
                if result[i+j] - result[i] <= tau_np:
                    result[i+j] = flag
                else:
                    break
        else:
            pass
    return result
