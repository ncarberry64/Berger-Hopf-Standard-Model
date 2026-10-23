"""Signed seven-output implicit/adjoint reduction for supplied owned blocks.

Conditional algebra only: callers must supply the full internal residual and
the actual seven-port output derivatives at one base point in common frames.
The routine never infers that a local border is the complete joint operator.
"""
from flint import arb_mat


def reduce_seven_port(K, Fp, pieces):
    """F_n=K, Phi_p=-K^-1 Fp; Dg_red=sum(g_p)-lambda^T Fp.

K^T lambda=(sum(g_n))^T. Compose signed sectors before this common solve;
no sector is independently supported, normed, eliminated or zero-filled.
"""
    n=K.nrows();p=Fp.ncols()
    if K.ncols()!=n or Fp.nrows()!=n or not pieces:
        raise ValueError('square common internal block and explicit pieces required')
    gp=arb_mat(7,p);gn=arb_mat(7,n)
    for name,piece in pieces.items():
        if set(piece)!={'p','n'}:raise ValueError('each piece requires p and n derivatives: '+name)
        if (piece['p'].nrows(),piece['p'].ncols())!=(7,p):raise ValueError('port p shape differs')
        if (piece['n'].nrows(),piece['n'].ncols())!=(7,n):raise ValueError('port n shape differs')
        gp+=piece['p'];gn+=piece['n']
    adjoint=K.transpose().solve(gn.transpose())
    correction=-adjoint.transpose()*Fp
    return dict(reduced=gp+correction,direct=gp,internal=gn,adjoint=adjoint,
                correction=correction,adjoint_replay=K.transpose()*adjoint-gn.transpose())


def moving_port_jet(B, reaction, reaction_jet, dB):
    """D(B Lambda)[u]=(DB[u])Lambda+B D Lambda[u], with explicit DB."""
    if B.nrows()!=7 or reaction.ncols()!=1 or B.ncols()!=reaction.nrows():
        raise ValueError('seven-row port and reaction column required')
    if reaction_jet.nrows()!=reaction.nrows() or len(dB)!=reaction_jet.ncols():
        raise ValueError('reaction and port derivatives must share directions')
    columns=[]
    for k,derivative in enumerate(dB):
        if (derivative.nrows(),derivative.ncols())!=(7,B.ncols()):raise ValueError('DB shape differs')
        column=arb_mat([[reaction_jet[i,k]] for i in range(reaction.nrows())])
        columns.append(B*column+derivative*reaction)
    return arb_mat([[columns[k][i,0] for k in range(len(columns))] for i in range(7)])
