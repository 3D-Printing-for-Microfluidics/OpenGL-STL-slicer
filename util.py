import numpy as np


def ortho(left, right, bottom, top, zNear, zFar, dtype):
    '''
    Return the following matrix
    |       2                               -(right+left)   |
    |  ----------       0           0       -------------   |
    |  right-left                             right-left    |
    |                                                       |
    |                   2                   -(top+bottom)   |
    |      0       ----------       0       -------------   |
    |              top-bottom                 top-bottom    |
    |                                                       |
    |                              -2       -(zFar+zNear)   |
    |      0            0      ----------   -------------   |
    |                          zFar-zNear     zFar-zNear    |
    |                                                       |
    |                                                       |
    |      0            0           0             1         |
    '''
    M = np.identity(4, dtype=dtype)
    M[0,0] = 2 / (right - left)
    M[1,1] = 2 / (top - bottom)
    M[2,2] = -2 / (zFar - zNear)
    M[0,3] = -(right + left) / (right - left)
    M[1,3] = -(top + bottom) / (top - bottom)
    M[2,3] = -(zFar + zNear) / (zFar - zNear)
    return M.T
    
    

def translation(direction, dtype):
    """Return matrix to translate by direction vector.

    If direction is [x, y, z], return the following matrix
    
    |   1   0   0   x   |
    |                   |
    |   0   1   0   y   |
    |                   |
    |   0   0   1   z   |
    |                   |
    |   0   0   0   1   |

    """
    M = np.identity(4, dtype=dtype)
    M[:3, 3] = direction[:3]
    return M.T
