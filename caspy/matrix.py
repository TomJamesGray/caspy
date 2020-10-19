def gen_id_mat(n):
    """Makes the n x n identity matrix"""
    mat = []
    for row_n in range(n):
        mat.append([
            1 if j == row_n else 0 for j in range(n)
        ])
    return mat


def get_max_from_sub_mat(mat,i,j,n):
    """
    Gets maximum element in the sub matrix to be used for complete
    pivoting
    :returns: maximum element,row, column
    """
    ret = (mat[i][j],i,j)
    for row in range(i,n):
        for col in range(j,n):
            if ret[0] < mat[row][col]:
                ret = (mat[row][col],row,col)
    return ret


def row_swap(mat,r1,r2):
    mat[r1], mat[r2] = mat[r2], mat[r1]
    return mat


def col_swap(mat,c1,c2):
    for row in mat:
        row[c1], row[c2] = row[c2], row[c1]
    return mat

# TODO dimension checking??
def mat_mul(a,b):
    res = []
    for row_a in range(len(a)):
        row = []
        for col_a in range(len(b[0])):
            row.append(sum(
                [a[row_a][j] * b[j][col_a] for j in range(len(a[0]))]
            ))
        res.append(row)
    return res


def mat_vec_prod(a,vec):
    """Computes matrix (a) product with vector"""
    res = []
    for i in range(len(a)):
        res.append(sum(
            [a[i][j] * vec[j] for j in range(len(vec))]
        ))
    return res


def invert_mat(mat):
    """
    Inverts a matrix with gaussian elimination with complete pivoting
    :param mat: List of lists representing an n x n matrix
    :return: Inverted matrix
    """
    # TODO check square matrix?
    n = len(mat)
    # First need to augment the system to [mat | id_mat(n)]
    auged = []
    id_mat = gen_id_mat(n)
    permeutation_matricies = []
    for row_i in range(n):
        auged.append(mat[row_i] + id_mat[row_i])

    for gs_step in range(n):
        # Find the maximum element in the relevant sub matrix
        piv_elem,piv_row,piv_col = get_max_from_sub_mat(auged,gs_step,gs_step,n)
        # Perform pivoting
        auged = row_swap(auged,gs_step,piv_row)
        auged = col_swap(auged,gs_step,piv_col)
        # Store column permeutation matricies so we can re-order the final inverse
        permeutation_matricies.append(row_swap(gen_id_mat(n),gs_step,piv_col))
        # auged = col_swap(auged,gs_step + n,piv_col + n)

        for row_i in range(0, n):
            if row_i == gs_step:
                continue
            sf = auged[row_i][gs_step] / auged[gs_step][gs_step]
            for col_j in range(0, 2*n):
                auged[row_i][col_j] = auged[row_i][col_j] - sf * auged[gs_step][col_j]
            # Add in a zero
            auged[row_i][gs_step] = 0

    # Go and normalise the results ie, make sure it's all 1 on the diagonal
    for row_i in range(0,n):
        diag = auged[row_i][row_i]
        auged[row_i] = [x / diag for x in auged[row_i]]

    # Get final column permeutation matrix
    col_perm_mat = gen_id_mat(n)
    for perm_mat in permeutation_matricies:
        col_perm_mat = mat_mul(col_perm_mat,perm_mat)

    rhs_aug = []
    # Get right part of augmented matrix
    for row in auged:
        rhs_aug.append(row[n:])

    return mat_mul(col_perm_mat,rhs_aug)
