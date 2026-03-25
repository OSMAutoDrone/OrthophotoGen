#from osgeo import gdal
import numpy as np

############################
#for debugging
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

class Arrow3D(FancyArrowPatch):
    def __init__(self, x, y, z, dx, dy, dz, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._xyz = (x, y, z)
        self._dxdydz = (dx, dy, dz)

    def draw(self, renderer):
        x1, y1, z1 = self._xyz
        dx, dy, dz = self._dxdydz
        x2, y2, z2 = (x1 + dx, y1 + dy, z1 + dz)

        xs, ys, zs = proj3d.proj_transform((x1, x2), (y1, y2), (z1, z2), self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)
        
    def do_3d_projection(self, renderer=None):
        x1, y1, z1 = self._xyz
        dx, dy, dz = self._dxdydz
        x2, y2, z2 = (x1 + dx, y1 + dy, z1 + dz)
        xs, ys, zs = proj3d.proj_transform((x1, x2), (y1, y2), (z1, z2), self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs) 


def _arrow3D(ax, x, y, z, dx, dy, dz, *args, **kwargs):
    '''Add an 3d arrow to an `Axes3D` instance.'''
    arrow = Arrow3D(x, y, z, dx, dy, dz, *args, **kwargs)
    ax.add_artist(arrow)


def helperPlot(ground, camera_matrix, image_plane, gcp, pvector, img_norm, intersect, opacity):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    #ground
    ax.plot_trisurf(ground[0,:],ground[1,:],ground[2,:], color = (139/255, 69/255, 19/255, opacity))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    #camera
    arrowx = Arrow3D(camera_matrix[0,3],camera_matrix[1,3],camera_matrix[2,3], camera_matrix[0,0], camera_matrix[1,0], camera_matrix[2,0], mutation_scale=10, fc='red')
    arrowy = Arrow3D(camera_matrix[0,3],camera_matrix[1,3],camera_matrix[2,3], camera_matrix[0,1], camera_matrix[1,1], camera_matrix[2,1], mutation_scale=10, fc='green')
    arrowz = Arrow3D(camera_matrix[0,3],camera_matrix[1,3],camera_matrix[2,3], camera_matrix[0,2], camera_matrix[1,2], camera_matrix[2,2], mutation_scale=10, fc='blue')
    ax.add_artist(arrowx)
    ax.add_artist(arrowy)
    ax.add_artist(arrowz)
    #camera view
    ax.plot_trisurf(image_plane[0], image_plane[1], image_plane[2], color = (95/255, 158/255, 160/255, opacity))
    ax.plot3D([camera_matrix[0,3],image_plane[0,0]], [camera_matrix[1,3],image_plane[1,0]], [camera_matrix[2,3],image_plane[2,0]], color='Black')
    ax.plot3D([camera_matrix[0,3],image_plane[0,1]], [camera_matrix[1,3],image_plane[1,1]], [camera_matrix[2,3],image_plane[2,1]], color='Black')
    ax.plot3D([camera_matrix[0,3],image_plane[0,2]], [camera_matrix[1,3],image_plane[1,2]], [camera_matrix[2,3],image_plane[2,2]], color='Black')
    ax.plot3D([camera_matrix[0,3],image_plane[0,3]], [camera_matrix[1,3],image_plane[1,3]], [camera_matrix[2,3],image_plane[2,3]], color='Black')
    #gcp point vector
    ax.scatter3D(gcp[0,0],gcp[1,0],gcp[2,0], marker='x')
    arrowGCP = Arrow3D(pvector[0,0], pvector[1,0], pvector[2,0], pvector[3,0], pvector[4,0], pvector[5,0], mutation_scale=10, fc='black')
    ax.add_artist(arrowGCP)
    #image plane normal
    arrowImgN = Arrow3D(img_norm[0,0], img_norm[1,0], img_norm[2,0], img_norm[3,0], img_norm[4,0], img_norm[5,0], mutation_scale=10, fc='black')
    ax.add_artist(arrowImgN)
    #intersection point
    ax.scatter3D(intersect[0],intersect[1],intersect[2], marker='x')
    ax.plot3D([camera_matrix[0,3],intersect[0]],[camera_matrix[1,3],intersect[1]],[camera_matrix[2,3],intersect[2]], linestyle ='dashed', marker='x')

    plt.draw()
    plt.show()  

setattr(Axes3D, 'arrow3D', _arrow3D)

############################
#actual program

# load the camera fixed parameters 
def loadCameraParams(filename):
    return 0 

# load the images parameters and return the camera matrix
# lat, long, elevation and 
def loadImageParams(filename):
    return 0

#distance in meters (x,y) between 2 lat, long positions
def latLongDist(lat, long, distx, disty):
    return 0 

#return the image plane corners position world coord
def getImagePlaneCorners(camera_matrix, camera_params):
    camera_height = camera_matrix[2,3]
    flight_height = camera_params[2]
    x_half_fov = np.deg2rad(camera_params[0]/2)
    y_half_fov = np.deg2rad(camera_params[1]/2)
    x1 = flight_height*np.tan(x_half_fov)
    x2 = flight_height*np.tan(-x_half_fov)
    y1 = flight_height*np.tan(y_half_fov)
    y2 = flight_height*np.tan(-y_half_fov)

    c1 = toWorldCoord(camera_matrix, x1, y1, flight_height)
    c2 = toWorldCoord(camera_matrix, x1, y2, flight_height)
    c3 = toWorldCoord(camera_matrix, x2, y2, flight_height)
    c4 = toWorldCoord(camera_matrix, x2, y1, flight_height)
    
    corners = np.hstack((c1,c2,c3,c4))

    return corners


#transform a point in the camera origin to the world origin
def toWorldCoord(camera_matrix, x, y,z):
    point_matrix = np.array([[1,0,0,x],
                             [0,1,0,y],
                             [0,0,1,z],
                             [0,0,0,1]])
    pinw = np.matmul(camera_matrix,point_matrix)
    return pinw[0:3,[3]]


#invert the given homogen matrix
def invertHomogen(mat):
    R = np.array(mat[0:3, 0:3]).T
    P = np.matmul(-R,mat[0:3,[3]])
    return np.vstack((np.hstack((R,P)), [[0,0,0,1]]))


#unit vector starting at p1 in direction of p2
#return a column vector stacking p1 and direction
def vectorFrom2Points(p1, p2):
    vec = (p2-p1)/np.linalg.norm(p2-p1)
    return np.vstack((p1,vec))


#normal vector of a plan 
#return a column vector stacking p1 and normal
def planeNormalFrom3points(p1, p2, p3):
    p12 = p2 - p1
    p13 = p3 - p1
    n = np.cross(p12,p13,axis=0)
    n_norm = n/np.linalg.norm(n)
    return np.vstack((p1,n_norm))

#collision between a vector and a plane
# modified from from https://gist.github.com/TimSC/8c25ca941d614bf48ebba6b473747d72
def LinePlaneCollision(planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6):
	ndotu = planeNormal.dot(rayDirection)
	if abs(ndotu) < epsilon:
		raise RuntimeError("no intersection or line is within plane")
	w = rayPoint - planePoint
	si = -planeNormal.dot(w) / ndotu
	Psi = w + si * rayDirection + planePoint
	return Psi



#interpret arguments for this script
def argparsing():
    return 0

if __name__  == "__main__":
    #x,y metres centré sur la cam
    # z altitude ASL
    test_ground = np.array([[-2,-1, 0, 1, 2,
                         -2,-1, 0, 1, 2,
                         -2,-1, 0, 1, 2,
                         -2,-1, 0, 1, 2,
                         -2,-1, 0, 1, 2],
                        [-2,-2,-2,-2,-2,
                         -1,-1,-1,-1,-1,
                          0, 0, 0, 0, 0,
                          1, 1, 1, 1, 1,
                          2, 2, 2, 2, 2],
                        [10, 9, 8, 7, 6,
                         9,  9, 8, 7, 6,
                         9,  8, 7, 6, 6,
                         8,  7, 6, 5, 5,
                         7,  6, 5, 5, 5]])
    
    #world orogin (0,0,0) is x,y of camera and 0 ASL
    #posision and rotation matrix for the camera -> obtained from loaded params
    #T 0->Cam
    #on pose que le z pointe vers l'avant (sors de l'objectif) et le x vers le dessus de la camera
    #x et y devrait toujours être 0 puisque les données sont centré sur 
    test_camera_matrix = np.array([[0,1,0,0],
                                   [1,0,0,0],
                                   [0,0,-1,15],
                                   [0,0,0,1]])
    #fov degrees vertical, horizontal, flight height
    test_camera_params = [10,15,10]
    
    #plan de l'image
    test_corners = getImagePlaneCorners(test_camera_matrix,test_camera_params)
    
    #vecteur de gcp avec le point 14 du DEM
    v1 = vectorFrom2Points(test_camera_matrix[0:3,[3]],test_ground[0:3,[13]])

    # find the normal to the image plan
    image_plan_normal = planeNormalFrom3points(test_corners[:,[0]],test_corners[:,[1]],test_corners[:,[2]])

    #intersection point
    intersection_point = LinePlaneCollision(image_plan_normal[3:6,0],image_plan_normal[0:3,0],v1[3:6,0],v1[0:3,0])
    
    #plot for convenience
    helperPlot(test_ground, test_camera_matrix, test_corners,test_ground[0:3,[13]], v1, image_plan_normal, intersection_point, 0.5)
    
    
#resumé des steps
# 1- setup des variables de test
#       > pour l'instant représente un DEM imaginaire qui aurait déjà été transformé de lat/long à x/y metres centré sur le drone
# 2- calcul de la position des coins de l'image
# 3- calcul le vecteur de diretion de la camera vers un point de la grille du DEM
#       > TODO automatiser le choix des points à extraire
# 4- calcul la normale du plan de l'image
# 5- calcul l'intersection entre le vecteur de gcp et le plan de l'image
# 6- plot pour visualisation des données

##unknowns
# comment placer les coord avec l'orientation de la cam
# comment comment la transformation des param et position de la cam au dem en metre selon la cam


##Améliorations possibles
# multithreading du calcul des points
# preloading des bon DEM
# utiliser des points custom
