import numpy as np
import random
import Image

"""
This is your object classifier. You should implement the train and
classify methods for this assignment.
"""
class ObjectClassifier():
    labels = ['Tree', 'Sydney', 'Steve', 'Cube']
    
    """
    Everytime a snapshot is taken, this method is called and
    the result is displayed on top of the four-image panel.
    """
    def classify(self, edge_pixels, orientations):
	prob_matrix = self.train()     
	
       	cube_conf = 1
	steve_conf = 1
        sydney_conf = 1
        tree_conf = 1

        (percent_edge, percent_top_horizontal, percent_top_vertical, percent_bottom_horizontal, percent_bottom_vertical, percent_edge_top_third) = self.image_features(edge_pixels,orientations)

        for x in range(0,4):
       	    conf = 1

	    if(percent_edge > 0.0175):
       	        conf *= prob_matrix[0][x]
	    else:
               	conf *= (1 - prob_matrix[0][x])

	    if(percent_top_horizontal < 0.677):
               	conf *= prob_matrix[1][x]
	    else:
               	conf *= (1 - prob_matrix[1][x])

            if(percent_top_vertical > 0.105):
       	        conf *= prob_matrix[2][x]
       	    else:
       	        conf *= (1 - prob_matrix[2][x])

       	    if(percent_bottom_horizontal < 0.41):
       	        conf *= prob_matrix[3][x]
       	    else:
       	        conf *= (1 - prob_matrix[3][x])

       	    if(percent_bottom_vertical > 0.188):
       	        conf *= prob_matrix[4][x]
       	    else:
       	        conf *= (1 - prob_matrix[4][x])

       	    if(percent_edge_top_third > 0.0073):
       	        conf *= prob_matrix[5][x]
       	    else:
       	        conf *= (1 - prob_matrix[5][x])                

	    print "Conf: " + str(conf)
	    if x == 0:
               	cube_conf = conf
	    elif x == 1:
               	steve_conf = conf
	    elif x == 2:    
               	sydney_conf = conf
            elif x == 3:
               	tree_conf = conf

        percent_conf = [tree_conf, sydney_conf, steve_conf, cube_conf]
        return self.labels[percent_conf.index(max(percent_conf))]
    
    """
    This is your training method. Feel free to change the
    definition to take a directory name or whatever else you
    like. The load_image (below) function may be helpful in
    reading in each image from your datasets.
    """
    def train(self):
#        for x in range(1,6):
#	    self.identify_image("NERO/snapshots/edges/Validation/cube-" + str(x) + ".png")
#	    
#        for x in range(1,6):
#	    self.identify_image("NERO/snapshots/edges/Validation/steve-" + str(x) + ".png")	    
#	
#        for x in range(1,6):
#	    self.identify_image("NERO/snapshots/edges/Validation/sydney-" + str(x) + ".png")      
#
#        for x in range(1,6):
#	    self.identify_image("NERO/snapshots/edges/Validation/tree-" + str(x) + ".png")
#	pass
        prob_matrix = np.array([[0.3636, 0.9231, 0.6429, 0.8182],
        	                [0.0909, 0.3077, 0.1429, 0.6364],
        	                [0.1818, 0.5385, 0.4286, 0.8182],
      		                [0.0909, 0.6923, 0.0714, 0.2727],
			        [0.2727, 0.9231, 0.5714, 0.7273],
	                        [0.3636, 0.4615, 0.6429, 1.0000]])

        return prob_matrix
      
    def identify_image(self, filename):      
	(edge, ori) = load_image(filename)
        self.image_features(edge, ori)

    def image_features(self, edge, ori):
	index = 0
	total_ori_pixels = float(len(ori)*len(ori[0]))
	total_edge_pixels = float(len(edge)*len(edge[0]))
	
	num_edges = sum(sum(1 for i in row if i > 100) for row in edge)
	percent_edge = float(num_edges)/total_edge_pixels
	
	num_edges_top_half_vertical = 0
	num_edges_top_half_horizontal = 0
	index = 0
	for row in ori:
	    if index < len(ori)/2:
                for i in row:
                    if i == 90 or i == 270:
                        num_edges_top_half_vertical += 1
                    if i == 0 or i == 180:
                        num_edges_top_half_horizontal += 1
            index += 1
	
	index = 0
	num_edges_bottom_half_horizontal = 0
	num_edges_bottom_half_vertical = 0
	for row in ori:
	    if index > len(ori)/2:
                for i in row:
                    if i == 90 or i == 270:
                        num_edges_bottom_half_vertical += 1
                    if i == 0 or i == 180:
                        num_edges_bottom_half_horizontal += 1
            index += 1
        
        percent_top_horizontal = float(num_edges_top_half_horizontal) / (total_ori_pixels/2)
        percent_top_vertical = float(num_edges_top_half_vertical) / (total_ori_pixels/2)
        percent_bottom_horizontal = float(num_edges_bottom_half_horizontal) / (total_ori_pixels/2)
        percent_bottom_vertical = float(num_edges_bottom_half_vertical) / (total_ori_pixels/2)
        
        index = 0
        num_edges_top_third = 0
        for row in edge:
	    if index < (len(edge)/3):
		for i in row:
		  if i > 100:
		      num_edges_top_third += 1
	    index += 1
        percent_edge_top_third = float(num_edges_top_third)/total_edge_pixels
        
        print str(percent_edge) + " ," + str(percent_top_horizontal) + " ," + str(percent_top_vertical) + " ," + str(percent_bottom_horizontal) + " ," + str(percent_bottom_vertical) + " ," + str(percent_edge_top_third)
	
	return (percent_edge, percent_top_horizontal, percent_top_vertical, percent_bottom_horizontal, percent_bottom_vertical, percent_edge_top_third)
        
        
"""
Loads an image from file and calculates the edge pixel orientations.
Returns a tuple of (edge pixels, pixel orientations).
"""
def load_image(filename):
    im = Image.open(filename)
    np_edges = np.array(im)
    upper_left = push(np_edges, 1, 1)
    upper_center = push(np_edges, 1, 0)
    upper_right = push(np_edges, 1, -1)
    mid_left = push(np_edges, 0, 1)
    mid_right = push(np_edges, 0, -1)
    lower_left = push(np_edges, -1, 1)
    lower_center = push(np_edges, -1, 0)
    lower_right = push(np_edges, -1, -1)
    vfunc = np.vectorize(find_orientation)
    orientations = vfunc(upper_left, upper_center, upper_right, mid_left, mid_right, lower_left, lower_center, lower_right)
    return (np_edges, orientations)

        
"""
Shifts the rows and columns of an array, putting zeros in any empty spaces
and truncating any values that overflow
"""
def push(np_array, rows, columns):
    result = np.zeros((np_array.shape[0],np_array.shape[1]))
    if rows > 0:
        if columns > 0:
            result[rows:,columns:] = np_array[:-rows,:-columns]
        elif columns < 0:
            result[rows:,:columns] = np_array[:-rows,-columns:]
        else:
            result[rows:,:] = np_array[:-rows,:]
    elif rows < 0:
        if columns > 0:
            result[:rows,columns:] = np_array[-rows:,:-columns]
        elif columns < 0:
            result[:rows,:columns] = np_array[-rows:,-columns:]
        else:
            result[:rows,:] = np_array[-rows:,:]
    else:
        if columns > 0:
            result[:,columns:] = np_array[:,:-columns]
        elif columns < 0:
            result[:,:columns] = np_array[:,-columns:]
        else:
            result[:,:] = np_array[:,:]
    return result

# The orientations that an edge pixel may have.
np_orientation = np.array([0,315,45,270,90,225,180,135])

"""
Finds the (approximate) orientation of an edge pixel.
"""
def find_orientation(upper_left, upper_center, upper_right, mid_left, mid_right, lower_left, lower_center, lower_right):
    a = np.array([upper_center, upper_left, upper_right, mid_left, mid_right, lower_left, lower_center, lower_right])
    return np_orientation[a.argmax()]
