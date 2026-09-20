"""Bound a common output vector before separating its coordinates."""
from flint import arb,arb_mat
from bhsm.interface.input_linear_taylor import matrix_norm_bound,vector_norm
from bhsm.interface.shared_parameter_residual import validate_groups


def box_image_norm(matrix):
    """For |eta_i|<=1, ||C eta||²<=sum_ij |(C^T C)_ij|."""
    gram=matrix.transpose()*matrix
    correlated=sum((abs(v).upper() for v in gram.entries()),arb(0)).sqrt().upper()
    separated=vector_norm([sum((abs(matrix[i,j]).upper() for j in range(matrix.ncols())),arb(0)).upper()
                           for i in range(matrix.nrows())])
    return min(correlated,separated)


def euclidean_image_norm(matrix):
    gram=matrix.transpose()*matrix if matrix.ncols()<=matrix.nrows() else matrix*matrix.transpose()
    squared=max(sum((abs(gram[i,j]).upper() for j in range(gram.ncols())),arb(0)).upper()
                for i in range(gram.nrows()))
    return min(matrix_norm_bound(matrix),squared.sqrt().upper())


def joint_constant_support(matrix,groups):
    validate_groups(groups,matrix.ncols())
    total=arb(0)
    for start,stop,kind in groups:
        block=arb_mat(matrix.nrows(),stop-start,[matrix[i,j] for i in range(matrix.nrows()) for j in range(start,stop)])
        total+=euclidean_image_norm(block) if kind=='euclidean' else box_image_norm(block)
    return total.upper()
