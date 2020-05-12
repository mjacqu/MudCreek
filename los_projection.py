import numpy as np

def pol2cart(theta, phi, r=1):
    '''
    theta = angle counter-clockwise from x in x-y plane
    phi = positive down from z in x-z plane
    r = radius (default = 1)
    '''
    x = r * np.cos(theta) * np.sin(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(phi)
    return x, y, z

r=1
S = pol2cart(np.radians(230), np.radians(125))
P_asc = pol2cart(np.radians(190), np.radians(41.8))
P_desc = pol2cart(np.radians(-10), np.radians(38.7))

delta_asc = np.arccos(np.dot(P_asc,S)/(np.linalg.norm(P_asc)*np.linalg.norm(S)))
delta_desc = np.pi - np.arccos(np.dot(P_desc,S)/(np.linalg.norm(P_desc)*np.linalg.norm(S)))

desc_los = np.cos(delta_desc) * r
asc_los = np.cos(delta_asc) * r
