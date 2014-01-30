def uk_map(fig1, indata, clevs, datlons, datlats, mtitle, munits, maskswitch):
	"""makes topography inclusive map of the UK, given a datset on an x*y grid, lon and lat 
	arrays on the same grid, contour levels, a title, and the correct units. Includes a 
	configurable scale for colour coding contours to any given function
	"""
	
	from mpl_toolkits import basemap as bm
	import matplotlib.cm as cm
	from mpl_toolkits.basemap import shiftgrid 
	from netCDF4 import Dataset
	from matplotlib.colors import LightSource
	import matplotlib.pyplot as plt
	import numpy as np
	
	# create the figure and axes instances.
	ax = fig1.add_axes([0.1,0.1,0.8,0.8])
	m = bm.Basemap(llcrnrlon=-9.5,llcrnrlat=49.5,urcrnrlon=2.5,urcrnrlat=59,rsphere=(6378137.00,6356752.3142),\
            	resolution='f',area_thresh=1000.,projection='laea', lat_0=54.5,lon_0=-2.75,ax=ax)
	m.drawcoastlines()
	
	# read in etopo5 topography/bathymetry.
	url = 'http://ferret.pmel.noaa.gov/thredds/dodsC/data/PMEL/etopo5.nc'
	etopodata = Dataset(url)
	topoin = etopodata.variables['ROSE'][:]
	lons = etopodata.variables['ETOPO05_X'][:]
	lats = etopodata.variables['ETOPO05_Y'][:]
	
	# shift data so lons go from -180 to 180 instead of 20 to 380.
	topoin,lons = shiftgrid(180.,topoin,lons,start=False)

	# transform coordinates
	x,y=m(datlons[:,:],datlats[:,:])
	# transform to nx x ny regularly spaced 5km native projection grid
	nx = int((m.xmax-m.xmin)/5000.)+1; ny = int((m.ymax-m.ymin)/5000.)+1
	topodat = m.transform_scalar(topoin,lons,lats,nx,ny)
	
	# create light source object for topography
	ls = LightSource(azdeg = 0, altdeg = 2)
	# use set_shade function (also available)
	rgb = set_shade(topodat)

	# plot image over map with imshow.
	im = m.imshow(rgb)
	
	# apply function to colormap pointers, can be any function at all, as long as
	# 0 remains 0, 1 remains 1, and values increase from one to the other.
	# x^4 is good for pseudo-log plots of rainfall
	log_jet=cmap_xmap(lambda x: (x*x*x*x), cm.hsv)
	#set to lambda x: x for not change. This is the version for no change:
	#log_jet=cmap_xmap(lambda x: (x), cm.jet)
	
	##apply function to colormap if desired to make whole scale 'hotter' or 'colder'
	##example makes colourmap significantly hotter by confining values to upper quarter	
	#log_jet=cmap_map(lambda x: x/4+0.75, cm.gist_rainbow)
	
	# mask out oceans, but not lakes. Useful when plotting or comparing against observed
	if maskswitch==1:
		# import missing data map for masking out of oceans 
		missdata = Dataset('/exports/work/geos_cxc/users/ahardin4/output/amibatch/afixa/miss.nc', 'r', format='NETCDF3_CLASSIC')
		missmap=missdata.variables['land_map']
		missmap2=missdata.variables['land_map']
		# cut from big mask to small mask if necessary
		#smallmap=missmap[0,6:46,0:34]
		smallmap=missmap[0,:,:]
		smallmap2=missmap2[0,:,:]
		# expand out by one to take into account interpolation
		
		for i in range(1,39):
			for j in range(1,33):
				if smallmap[i,j] == 0.0:
					smallmap2[i-1,j]=0.0 
					smallmap2[i,j-1]=0.0
					smallmap2[i+1,j]=0.0 
					smallmap2[i,j+1]=0.0
		
		# perform masking
		indata=np.ma.masked_array(indata,mask=(smallmap2<-0.5))
		print smallmap2[0,0], smallmap2[36,0], smallmap2[20,20]
		#indata[indata<=0.1]=np.nan
	# produce semi-transparent contour map
	contourmap=m.contourf(x,y,indata,clevs,cmap=cm.get_cmap(log_jet,len(clevs)-1),extend='both',
		alpha=0.5,origin='lower',rasterized=True)
		
	# produce simple block plot
	#contourmap=m.pcolor(x,y,indata,shading='interp',cmap=cm.get_cmap(log_jet,len(clevs)-1),
	#	alpha=0.5)
		
	# place colour bar on right
	cb = m.colorbar(contourmap,"right", size="5%", pad='3%')
	# configure colour bar labeling
	cl = plt.getp(cb.ax, 'ymajorticklabels')
	contourmap=plt.setp(cl, fontsize=14)

	# draw parallels and meridians so as not to clash with colour bar placement
	# labels = [left,right,top,bottom]
	m.drawparallels(np.arange(-70.,80,1.), labels=[1,0,0,1], fontsize=13)
	m.drawmeridians(np.arange(351.,362.,2.),labels=[1,0,0,1], fontsize=13)
	
	# configure title and units
	cb.ax.set_xlabel(munits, fontsize=12)
	contourmap=plt.title(mtitle, fontsize=14)
