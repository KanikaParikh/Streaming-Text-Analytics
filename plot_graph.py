# Kanika Parikh 216030215 and Kaumilkumar Patel 216008914
# Assignment 3 : Part A

# Reference: https://www.toptal.com/apache/apache-spark-streaming-twitter and https://pythonprogramming.net/live-graphs-matplotlib-tutorial/

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import style

style.use('ggplot') # visually apealing
fig = plt.figure()
ax = fig.add_subplot(1,1,1)

# i = interval & uses iterable frames 
def animate(i):

	values = open('values.txt','r').read() #reads line in file
	lines = values.split('\n')
	xs = []
	ys = []

	for l in lines:
		if len(l) > 1:
			x,y = l.split() # split hashtag and count the occurences 
			xs.append(x)
			ys.append(int(y))

	ax.clear()
	ax.barh(xs, ys,align='center',color='royalblue',edgecolor='black') #horizontal bar graph
	ax.set_xlabel('#Occurrences', fontsize=12)
	ax.plot()

ani = animation.FuncAnimation(fig, animate, interval=2000) # call animate function, interval = 2sec

# plt.tight_layout() automatically adjusts the padding of the subplot.
# plt.tight_layout()
# plt.show() is mandatory as it interacts with graphical backend.
plt.show()
