def set_shade(a,intensity=None,scale=10.0,azdeg=165.0,altdeg=45.0):
  ''' Created by Ran Novitsky:
  http://rnovitsky.blogspot.co.uk/2010/04/using-hillshade-image-as-intensity.html
  
    sets shading for data array based on intensity layer
  	or the data's value itself.inputs:
 	 a - a 2-d array or masked array
  	intensity - a 2-d array of same size as a (no chack on that)
                    representing the intensity layer. if none is given
                    the data itself is used after getting the hillshade values
                    see hillshade for more details.
  	cmap - a colormap (e.g matplotlib.colors.LinearSegmentedColormap
              instance)
  	scale,azdeg,altdeg - parameters for hilshade function see there for
              more details
  	output:
  	rgb - an rgb set of the Pegtop soft light composition of the data and 
           intensity can be used as input for imshow()
  	based on ImageMagick's Pegtop_light:
 	 http://www.imagemagick.org/Usage/compose/#pegtoplight
  '''

  from pylab import cm, pi
  cmap=cm.gist_gray
  if intensity is None:
# hilshading the data
    intensity = hillshade(a,scale=10.0,azdeg=165.0,altdeg=45.0)
  else:
# or normalize the intensity
    intensity = (intensity - intensity.min())/(intensity.max() - intensity.min())
# get rgb of normalized data based on cmap
  rgb = cmap((a-a.min())/float(a.max()-a.min()))[:,:,:3]
# form an rgb eqvivalent of intensity
  d = intensity.repeat(3).reshape(rgb.shape)
# simulate illumination based on pegtop algorithm.
  rgb = 2*d*rgb+(rgb**2)*(1-2*d)
  return rgb
  